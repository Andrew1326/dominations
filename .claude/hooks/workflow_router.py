#!/usr/bin/env python3
"""
Workflow Router Hook for Claude Code
Evaluates task complexity and suggests using Gemini or native agents.
"""

import json
import sys

WORKFLOW_REMINDER = """
<user-prompt-submit-hook>
MANDATORY WORKFLOW for implementation tasks:

1. PLAN
   - Complex (3+ files)? Call Gemini → Create story file
   - Add task to docs/planning/sprint.md (In Progress)

2. IMPLEMENT - Write the code

3. TEST (MANDATORY - never skip!)
   - New features: Write E2E tests for acceptance criteria
   - Bug fixes: Add regression test
   - Existing features: Update tests if behavior changes

4. VERIFY - npm run test (must PASS)

5. REVIEW - Self-check: security, bugs, code quality

6. DONE - Move task to Done in sprint.md

No feature is complete without tests. Only report DONE after all steps complete.

Skip for: questions, git commands, /slash commands.
</user-prompt-submit-hook>
"""


def main():
    """Main hook function."""
    # Read input from stdin
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except json.JSONDecodeError:
        sys.exit(0)  # Allow to proceed if we can't parse input

    # Get the user's prompt
    prompt = input_data.get("prompt", "").lower()

    # Skip for simple questions/greetings that don't need BMAD
    skip_patterns = [
        "hello", "hi ", "hey", "thanks", "thank you",
        "what is", "what's", "explain", "tell me about",
        "how does", "why ", "can you",
        "commit", "push", "status", "diff",  # git commands
        "/",  # slash commands
        "bmad",  # already asking about BMAD
    ]

    for pattern in skip_patterns:
        if prompt.startswith(pattern) or (len(prompt) < 20 and pattern in prompt):
            sys.exit(0)  # Skip reminder for simple queries

    # Show workflow reminder for task-like prompts
    print(WORKFLOW_REMINDER)

    # Allow to proceed (don't block)
    sys.exit(0)


if __name__ == "__main__":
    main()
