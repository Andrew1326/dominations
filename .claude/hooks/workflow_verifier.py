#!/usr/bin/env python3
"""
Workflow Verifier Hook for Claude Code

Runs at Stop to verify workflow completion:
1. Tests exist for source changes
2. Tests pass (from .last_test_run)
3. Docs updated if significant changes

This provides end-of-session verification that the workflow was followed.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta


TEST_STATUS_FILE = ".claude/.last_test_run"
STALE_MINUTES = 10


def get_changed_files(prefix: str = "") -> list[str]:
    """Get list of changed files, optionally filtered by prefix."""
    try:
        # Unstaged changes
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        changed = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Staged changes
        result_staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            timeout=5
        )
        staged = result_staged.stdout.strip().split("\n") if result_staged.stdout.strip() else []

        all_changed = list(set(changed + staged))

        if prefix:
            return [f for f in all_changed if f.startswith(prefix)]
        return all_changed
    except Exception:
        return []


def get_test_status() -> dict | None:
    """Read last test run status."""
    try:
        if os.path.exists(TEST_STATUS_FILE):
            with open(TEST_STATUS_FILE, 'r') as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data.get('timestamp', ''))
                is_stale = (datetime.now() - timestamp) > timedelta(minutes=STALE_MINUTES)
                return {
                    'passed': data.get('passed', False),
                    'summary': data.get('summary', 'Unknown'),
                    'stale': is_stale,
                    'timestamp': timestamp
                }
    except Exception:
        pass
    return None


def is_config_only_change(files: list[str]) -> bool:
    """Check if changes are only config/docs (no tests needed)."""
    return all(
        f.startswith('.claude/') or
        f.startswith('docs/') or
        f.endswith('.md') or
        f.endswith('.json') or
        f.endswith('.yml') or
        f.endswith('.yaml')
        for f in files
    )


def main():
    """Main hook function."""
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except json.JSONDecodeError:
        sys.exit(0)

    # Get changed files
    all_changed = get_changed_files()
    src_changed = get_changed_files("src/")
    test_changed = [f for f in all_changed if f.startswith("tests/") or "test" in f.lower()]
    docs_changed = get_changed_files("docs/")

    # Skip verification if no changes or config-only changes
    if not all_changed or is_config_only_change(all_changed):
        sys.exit(0)

    # Skip if no source changes
    if not src_changed:
        sys.exit(0)

    issues = []
    warnings = []

    # Check 1: Tests written for source changes?
    if src_changed and not test_changed:
        issues.append(f"Tests not written ({len(src_changed)} src files changed)")

    # Check 2: Tests run and passed?
    test_status = get_test_status()
    if not test_status:
        issues.append("Tests were not run (no .last_test_run found)")
    elif not test_status['passed']:
        issues.append(f"Tests failed: {test_status['summary']}")
    elif test_status['stale']:
        warnings.append(f"Test results are stale ({test_status['timestamp'].strftime('%H:%M')})")

    # Check 3: Docs updated for significant changes?
    significant_patterns = ["lib/ai/", "services/", "api/", "models/", "components/"]
    significant_src = [f for f in src_changed if any(p in f for p in significant_patterns)]

    if len(significant_src) >= 2 and not docs_changed:
        warnings.append(f"Consider updating docs ({len(significant_src)} significant files changed)")

    # Output verification report
    if issues or warnings:
        print("\n" + "=" * 60)
        print("WORKFLOW VERIFICATION")
        print("=" * 60)

        if issues:
            print("\nISSUES (workflow incomplete):")
            for issue in issues:
                print(f"  - {issue}")

        if warnings:
            print("\nWARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")

        print("\nChanged files:")
        print(f"  src/: {len(src_changed)} files")
        print(f"  tests/: {len(test_changed)} files")
        print(f"  docs/: {len(docs_changed)} files")

        if issues:
            print("\nTo complete workflow:")
            print("  1. Write tests for your changes")
            print("  2. Run: npm run test")
            print("  3. Ensure tests pass")

        print("=" * 60 + "\n")
    else:
        # All good - brief confirmation
        test_info = test_status['summary'] if test_status else "verified"
        print(f"\nWorkflow verified: {test_info}")

    sys.exit(0)


if __name__ == "__main__":
    main()
