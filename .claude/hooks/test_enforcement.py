#!/usr/bin/env python3
"""
Test Enforcement Hook for Claude Code

Runs before git commit commands to ensure:
1. Tests are written for source changes
2. Tests PASS (verified by checking last test run or running tests)

This hook enforces the CLAUDE.md workflow strictly.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


# File to track last successful test run
TEST_STATUS_FILE = ".claude/.last_test_run"


def get_staged_files():
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return [f for f in result.stdout.strip().split('\n') if f]
    except Exception:
        pass
    return []


def get_last_test_status():
    """Check if tests passed recently (within last 10 minutes)."""
    try:
        if os.path.exists(TEST_STATUS_FILE):
            with open(TEST_STATUS_FILE, 'r') as f:
                data = json.load(f)
                last_run = datetime.fromisoformat(data.get('timestamp', ''))
                passed = data.get('passed', False)

                # Tests must have passed within last 10 minutes
                if passed and (datetime.now() - last_run) < timedelta(minutes=10):
                    return True, data.get('summary', 'Tests passed')
    except Exception:
        pass
    return False, None


def record_test_status(passed: bool, summary: str = ""):
    """Record test run status."""
    try:
        os.makedirs(os.path.dirname(TEST_STATUS_FILE), exist_ok=True)
        with open(TEST_STATUS_FILE, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'passed': passed,
                'summary': summary
            }, f)
    except Exception:
        pass


def main():
    """Main hook function."""
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only check Bash commands
    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "")

    # Track test runs to record pass/fail status
    if "npm run test" in command or "npm test" in command or "playwright test" in command:
        # This is a test run - we'll let it proceed
        # The PostToolUse hook or manual tracking will record results
        sys.exit(0)

    # Only check git commit commands
    if "git commit" not in command:
        sys.exit(0)

    # Skip if --no-verify is used (escape hatch)
    if "--no-verify" in command:
        print("WARNING: Skipping test enforcement with --no-verify")
        sys.exit(0)

    # Get staged files
    staged_files = get_staged_files()

    if not staged_files:
        sys.exit(0)

    # Check for source file changes
    src_changes = [f for f in staged_files if f.startswith('src/') and f.endswith(('.ts', '.tsx'))]
    test_changes = [f for f in staged_files if 'test' in f.lower() or f.startswith('tests/')]

    # Also check for .claude/ config changes (these don't need tests)
    config_only = all(
        f.startswith('.claude/') or
        f.startswith('docs/') or
        f.endswith('.md') or
        f.endswith('.json')
        for f in staged_files
    )

    if config_only:
        sys.exit(0)  # Config/docs changes don't need tests

    # RULE 1: Source changes require test changes
    if src_changes and not test_changes:
        error_msg = f"""
COMMIT BLOCKED: Tests required for source changes

Source files staged ({len(src_changes)}):
{chr(10).join('  - ' + f for f in src_changes[:5])}
{'  ... and ' + str(len(src_changes) - 5) + ' more' if len(src_changes) > 5 else ''}

No test files found in staged changes.

Per CLAUDE.md workflow:
- New features: Write E2E tests in tests/e2e/specs/
- Bug fixes: Add regression test
- Existing features: Update tests if behavior changes

To proceed:
1. Write tests for your changes
2. Stage the test files: git add tests/
3. Run tests: npm run test
4. Try commit again
"""
        print(error_msg)
        sys.exit(1)

    # RULE 2: Tests must have passed recently
    if src_changes or test_changes:
        tests_passed, summary = get_last_test_status()

        if not tests_passed:
            error_msg = f"""
COMMIT BLOCKED: Tests must pass before commit

You have source/test changes staged, but no recent passing test run.

To proceed:
1. Run tests: npm run test
2. Ensure all tests pass
3. Try commit again

This ensures the feature actually works, not just that tests were written.
"""
            print(error_msg)
            sys.exit(1)
        else:
            # Tests passed - show confirmation
            print(f"Tests verified: {summary}")

    sys.exit(0)


if __name__ == "__main__":
    main()
