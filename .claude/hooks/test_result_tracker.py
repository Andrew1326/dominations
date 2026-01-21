#!/usr/bin/env python3
"""
Test Result Tracker Hook for Claude Code

Runs after test commands to record pass/fail status.
This enables the test_enforcement hook to verify tests passed before commit.
"""

import json
import os
import sys
from datetime import datetime


TEST_STATUS_FILE = ".claude/.last_test_run"


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
    except Exception as e:
        print(f"Warning: Could not record test status: {e}")


def main():
    """Main hook function."""
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    tool_result = input_data.get("tool_result", {})

    # Only check Bash commands
    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "")

    # Only track test commands
    if not any(test_cmd in command for test_cmd in ["npm run test", "npm test", "playwright test"]):
        sys.exit(0)

    # Get the output to determine pass/fail
    output = tool_result.get("stdout", "") + tool_result.get("stderr", "")

    # Also check the content field if stdout/stderr not available
    if not output:
        output = str(tool_result.get("content", ""))

    # Determine if tests passed
    # Look for common pass/fail indicators
    passed = False
    summary = "Unknown result"

    # Playwright indicators
    if "passed" in output.lower():
        # Extract pass count
        import re
        match = re.search(r'(\d+)\s+passed', output)
        if match:
            passed = True
            summary = f"{match.group(1)} tests passed"

    # Check for failures
    if "failed" in output.lower() or "error" in output.lower():
        match = re.search(r'(\d+)\s+failed', output)
        if match and int(match.group(1)) > 0:
            passed = False
            summary = f"{match.group(1)} tests failed"
        elif "Error:" in output or "FAILED" in output:
            passed = False
            summary = "Tests failed"

    # Check exit code if available
    exit_code = tool_result.get("exit_code", tool_result.get("exitCode"))
    if exit_code is not None:
        if exit_code == 0 and "passed" in output.lower():
            passed = True
        elif exit_code != 0:
            passed = False
            summary = f"Tests failed (exit code {exit_code})"

    # Record the result
    record_test_status(passed, summary)

    # Output status for visibility
    if passed:
        print(f"Test status recorded: PASSED - {summary}")
    else:
        print(f"Test status recorded: FAILED - {summary}")

    sys.exit(0)


if __name__ == "__main__":
    main()
