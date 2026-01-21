#!/usr/bin/env python3
"""
Session Reflection Hook - Automatic analysis on session end.
Analyzes conversation transcript and generates improvement suggestions.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
MIN_TOOL_CALLS = int(os.environ.get('MIN_REFLECT_TOOL_CALLS', '5'))

# Patterns indicating user corrections or friction
CORRECTION_PATTERNS = [
    r'\bno,?\s+(i|actually|that\'s not|wrong)',
    r'\bactually,?\s+i\s+(meant|want)',
    r'\binstead,?\s+',
    r'\bwait,?\s+',
    r'\bsorry,?\s+i\s+meant',
    r'\bthat\'s\s+not\s+what',
]

FRICTION_PATTERNS = [
    r'\bstop\b',
    r'\bcancel\b',
    r'\bundo\b',
    r'\bwhy\s+(did|are)\s+you',
]


def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())


def parse_transcript(transcript_path: str) -> dict:
    """Parse JSONL transcript file into structured data."""
    entries = []
    if not transcript_path or not os.path.exists(transcript_path):
        return {'entries': [], 'tool_calls': [], 'user_messages': [], 'errors': []}

    with open(transcript_path, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                entries.append(entry)
            except json.JSONDecodeError:
                continue

    tool_calls = []
    user_messages = []
    errors = []

    for entry in entries:
        entry_type = entry.get('type', '')

        if entry_type == 'tool_use':
            tool_calls.append({
                'name': entry.get('name', ''),
                'input': entry.get('input', {}),
                'timestamp': entry.get('timestamp', ''),
                'is_error': False,
                'result': ''
            })

        elif entry_type == 'tool_result':
            if tool_calls:
                tool_calls[-1]['result'] = str(entry.get('content', ''))[:500]
                tool_calls[-1]['is_error'] = entry.get('is_error', False)
            if entry.get('is_error'):
                errors.append({
                    'tool': tool_calls[-1]['name'] if tool_calls else 'unknown',
                    'error': str(entry.get('content', ''))[:200]
                })

        elif entry_type == 'user':
            content = entry.get('message', {}).get('content', '')
            if isinstance(content, str):
                # Strip system reminders
                if '<system-reminder>' in content:
                    content = content.split('<system-reminder>')[0].strip()
                if content:
                    user_messages.append(content)

    return {
        'entries': entries,
        'tool_calls': tool_calls,
        'user_messages': user_messages,
        'errors': errors
    }


def analyze_tool_failures(tool_calls: list) -> list:
    """Identify tool failures and retry patterns."""
    issues = []

    for call in tool_calls:
        if call.get('is_error'):
            issues.append({
                'type': 'tool_failure',
                'tool': call.get('name', ''),
                'error': call.get('result', '')[:150],
                'priority': 'HIGH'
            })

    # Detect retries (same tool called 3+ times consecutively)
    for i in range(len(tool_calls) - 2):
        if (tool_calls[i]['name'] == tool_calls[i+1]['name'] == tool_calls[i+2]['name']):
            tool_name = tool_calls[i]['name']
            # Avoid duplicate retry detections
            already_detected = any(
                iss['type'] == 'retry_pattern' and iss['tool'] == tool_name
                for iss in issues
            )
            if not already_detected:
                issues.append({
                    'type': 'retry_pattern',
                    'tool': tool_name,
                    'count': 3,
                    'priority': 'MEDIUM'
                })

    return issues


def analyze_friction(user_messages: list) -> list:
    """Identify workflow friction from user corrections."""
    issues = []
    seen = set()

    for msg in user_messages:
        msg_lower = msg.lower()

        for pattern in CORRECTION_PATTERNS:
            if re.search(pattern, msg_lower):
                evidence = msg[:100]
                if evidence not in seen:
                    seen.add(evidence)
                    issues.append({
                        'type': 'user_correction',
                        'evidence': evidence,
                        'priority': 'MEDIUM'
                    })
                break

        for pattern in FRICTION_PATTERNS:
            if re.search(pattern, msg_lower):
                evidence = msg[:100]
                if evidence not in seen:
                    seen.add(evidence)
                    issues.append({
                        'type': 'friction_signal',
                        'evidence': evidence,
                        'priority': 'LOW'
                    })
                break

    return issues


def analyze_efficiency(tool_calls: list) -> list:
    """Identify efficiency issues."""
    issues = []
    read_files = defaultdict(int)
    search_patterns = defaultdict(int)

    for call in tool_calls:
        tool_name = call.get('name', '')
        tool_input = call.get('input', {})

        if tool_name == 'Read':
            file_path = tool_input.get('file_path', '')
            if file_path:
                read_files[file_path] += 1

        if tool_name in ('Grep', 'Glob'):
            pattern = tool_input.get('pattern', '')
            if pattern:
                search_patterns[pattern] += 1

    for file_path, count in read_files.items():
        if count > 2:
            issues.append({
                'type': 'repeated_read',
                'file': file_path,
                'count': count,
                'priority': 'LOW',
                'suggestion': 'Consider creating a skill with this file\'s key info'
            })

    for pattern, count in search_patterns.items():
        if count > 2:
            issues.append({
                'type': 'repeated_search',
                'pattern': pattern[:50],
                'count': count,
                'priority': 'LOW',
                'suggestion': 'Consider adding this pattern knowledge to a skill'
            })

    return issues


def get_session_summary(data: dict) -> dict:
    """Generate brief session summary."""
    tool_counts = defaultdict(int)
    for call in data['tool_calls']:
        tool_counts[call.get('name', '')] += 1

    task = "Unknown task"
    for msg in data['user_messages']:
        if len(msg) > 20:
            task = msg[:150]
            if len(msg) > 150:
                task += "..."
            break

    return {
        'task': task,
        'tool_counts': dict(tool_counts),
        'total_tools': len(data['tool_calls']),
        'total_errors': len(data['errors'])
    }


def generate_reflection_file(analysis: dict, output_dir: Path) -> str:
    """Generate markdown reflection file."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    filename = f"{timestamp}.md"
    filepath = output_dir / filename

    summary = analysis['summary']
    tool_failures = [i for i in analysis['issues'] if i['type'] == 'tool_failure']
    friction = [i for i in analysis['issues'] if i['type'] in ('user_correction', 'friction_signal')]
    efficiency = [i for i in analysis['issues'] if i['type'] in ('repeated_read', 'repeated_search', 'retry_pattern')]

    tools_str = ', '.join(f"{k}({v})" for k, v in summary['tool_counts'].items())

    content = f"""# Session Reflection - {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Session Summary
- **Task**: {summary['task']}
- **Total tool calls**: {summary['total_tools']}
- **Errors encountered**: {summary['total_errors']}
- **Tools used**: {tools_str}

## Issues Found

### Tool Failures ({len(tool_failures)} issues)
"""

    if tool_failures:
        content += "| Tool | Error | Priority |\n|------|-------|----------|\n"
        for issue in tool_failures[:5]:
            error = issue.get('error', '').replace('\n', ' ').replace('|', '/')[:80]
            content += f"| {issue['tool']} | {error}... | {issue['priority']} |\n"
    else:
        content += "No tool failures detected.\n"

    content += f"""
### Workflow Friction ({len(friction)} issues)
"""

    if friction:
        for issue in friction[:5]:
            evidence = issue.get('evidence', '').replace('\n', ' ')[:80]
            content += f"- **{issue['type']}**: \"{evidence}...\"\n"
    else:
        content += "No significant friction detected.\n"

    content += f"""
### Efficiency Concerns ({len(efficiency)} issues)
"""

    if efficiency:
        for issue in efficiency[:5]:
            if issue['type'] == 'repeated_read':
                content += f"- File `{issue['file']}` read {issue['count']} times\n"
            elif issue['type'] == 'repeated_search':
                content += f"- Search pattern `{issue['pattern']}` used {issue['count']} times\n"
            elif issue['type'] == 'retry_pattern':
                content += f"- Tool `{issue['tool']}` retried {issue['count']}+ times consecutively\n"
    else:
        content += "No efficiency issues detected.\n"

    content += """
## Suggested Improvements

### Immediate Actions
"""

    suggestions = []
    if tool_failures:
        suggestions.append("- [ ] Review tool failure patterns and add validation/error handling")
    if any(i['type'] == 'retry_pattern' for i in efficiency):
        suggestions.append("- [ ] Investigate retry patterns - may need different approach")
    if any(i['type'] == 'repeated_read' for i in efficiency):
        suggestions.append("- [ ] Create skill with commonly accessed file knowledge")
    if friction:
        suggestions.append("- [ ] Review friction points for clearer communication")

    if suggestions:
        content += '\n'.join(suggestions)
    else:
        content += "- No immediate actions needed"

    content += """

### Potential Skills to Create
"""

    skill_suggestions = []
    for issue in efficiency:
        if issue['type'] == 'repeated_read':
            fname = issue['file'].split('/')[-1]
            skill_suggestions.append(f"- [ ] `{fname}-context`: Cache key info from `{issue['file']}`")

    if skill_suggestions:
        content += '\n'.join(skill_suggestions[:3])
    else:
        content += "- No new skills suggested"

    content += """

### Potential Hooks to Add
"""

    hook_suggestions = []
    if tool_failures:
        hook_suggestions.append("- [ ] `path_validator`: PreToolUse hook to validate file paths")
    if any(i['type'] == 'retry_pattern' for i in efficiency):
        hook_suggestions.append("- [ ] `retry_detector`: Alert when same tool fails repeatedly")

    if hook_suggestions:
        content += '\n'.join(hook_suggestions[:3])
    else:
        content += "- No new hooks suggested"

    content += f"""

---
*Generated automatically by session_reflect hook*
*Review and apply changes manually*
*Total issues: {len(analysis['issues'])}*
"""

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)

    return str(filepath)


def update_patterns_db(analysis: dict, patterns_file: Path):
    """Update cross-session patterns database."""
    patterns = {}
    if patterns_file.exists():
        try:
            with open(patterns_file, 'r') as f:
                patterns = json.load(f)
        except (json.JSONDecodeError, IOError):
            patterns = {}

    now = datetime.now().isoformat()

    for issue in analysis['issues']:
        context = issue.get('tool', issue.get('pattern', issue.get('file', 'general')))
        if isinstance(context, str) and len(context) > 50:
            context = context[:50]
        issue_key = f"{issue['type']}:{context}"

        if issue_key not in patterns:
            patterns[issue_key] = {
                'count': 0,
                'first_seen': now,
                'last_seen': None
            }
        patterns[issue_key]['count'] += 1
        patterns[issue_key]['last_seen'] = now

    patterns_file.parent.mkdir(parents=True, exist_ok=True)
    with open(patterns_file, 'w') as f:
        json.dump(patterns, f, indent=2)


def main():
    """Main hook function."""
    load_env()

    # Check if auto-reflect is disabled
    if os.environ.get('DISABLE_AUTO_REFLECT') == '1':
        sys.exit(0)

    # Read input from stdin
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data:
            sys.exit(0)
        input_data = json.loads(stdin_data)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    transcript_path = input_data.get('transcript_path', '')

    # Parse transcript
    data = parse_transcript(transcript_path)

    # Skip trivial sessions
    if len(data['tool_calls']) < MIN_TOOL_CALLS:
        sys.exit(0)

    # Run analysis
    issues = []
    issues.extend(analyze_tool_failures(data['tool_calls']))
    issues.extend(analyze_friction(data['user_messages']))
    issues.extend(analyze_efficiency(data['tool_calls']))

    # Skip if no issues found
    if not issues:
        sys.exit(0)

    analysis = {
        'summary': get_session_summary(data),
        'issues': issues
    }

    # Determine output directory
    project_root = Path(__file__).parent.parent.parent
    reflections_dir = project_root / '.claude' / 'reflections'
    patterns_file = reflections_dir / '.patterns.json'

    # Generate reflection file
    filepath = generate_reflection_file(analysis, reflections_dir)

    # Update cross-session patterns
    update_patterns_db(analysis, patterns_file)

    # Print notification
    print(f"\n[Reflect] Session analyzed: {len(issues)} issues found", file=sys.stderr)
    print(f"[Reflect] Saved to: {filepath}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
