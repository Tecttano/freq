#!/usr/bin/env python3

from collections import Counter, defaultdict
import datetime
import re
import os
import argparse
import sys

def detect_current_shell():
    # Check SHELL environment variable first
    shell_path = os.environ.get('SHELL', '')
    if shell_path:
        shell_name = os.path.basename(shell_path)
        if 'zsh' in shell_name:
            return 'zsh'
        elif 'bash' in shell_name:
            return 'bash'
    
    # Fallback: check parent process
    try:
        import psutil
        parent = psutil.Process().parent()
        if parent:
            parent_name = parent.name().lower()
            if 'zsh' in parent_name:
                return 'zsh'
            elif 'bash' in parent_name:
                return 'bash'
    except ImportError:
        pass
    
    return None

def find_history_file_for_shell(shell_type):
    if shell_type == 'zsh':
        zsh_paths = [
            os.path.expanduser("~/.zsh_history"),
            os.path.expanduser("~/.histfile"),
            "/root/.zsh_history"
        ]
        for path in zsh_paths:
            if os.path.exists(path):
                return path
    elif shell_type == 'bash':
        bash_paths = [
            os.path.expanduser("~/.bash_history"),
            "/root/.bash_history"
        ]
        for path in bash_paths:
            if os.path.exists(path):
                return path
    
    return None

def find_history_files():
    history_files = {}
    
    zsh_paths = [
        "/root/.zsh_history",
        os.path.expanduser("~/.zsh_history"),
        os.path.expanduser("~/.histfile")
    ]
    
    for path in zsh_paths:
        if os.path.exists(path):
            history_files['zsh'] = path
            break
    
    bash_paths = [
        os.path.expanduser("~/.bash_history"),
        "/root/.bash_history"
    ]
    
    for path in bash_paths:
        if os.path.exists(path):
            history_files['bash'] = path
            break
    
    return history_files

def detect_shell_type(history_file):
    # Detect shell type based on history file format
    if not os.path.exists(history_file):
        return None
    
    try:
        with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                lines.append(line.strip())
                if i >= 10:
                    break
        
        # Check for zsh format (: timestamp:duration;command)
        zsh_pattern = re.compile(r'^: \d{10}:\d+;')
        if any(zsh_pattern.match(line) for line in lines):
            return 'zsh'
        
        # Check for bash timestamp format (#timestamp)
        if any(line.startswith('#') and line[1:].isdigit() for line in lines):
            return 'bash_timestamped'
        
        return 'bash'
        
    except Exception:
        return None

def parse_zsh_history(history_file, full_command=False, date_filter=None, command_filter=None):
    history = []
    
    try:
        with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # Extract timestamp
                date_match = re.search(r': (\d{10}):', line)
                if not date_match:
                    continue
                
                timestamp = int(date_match.group(1))
                
                # Early date filtering
                if date_filter:
                    start_time, end_time = date_filter
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    
                # Extract command - format: ": timestamp:duration;command"
                if ';' in line:
                    timestamp_end = line.find(':0;')
                    if timestamp_end != -1:
                        full_cmd = line[timestamp_end + 3:].strip()
                    else:
                        duration_match = re.search(r': \d{10}:\d+;', line)
                        if duration_match:
                            full_cmd = line[duration_match.end():].strip()
                        else:
                            continue
                else:
                    continue
                    
                if not full_cmd:
                    continue
                    
                command = extract_command(full_cmd, full_command)
                if command:
                    # Early command filtering
                    if command_filter:
                        if not (command.startswith(command_filter + " ") or command == command_filter):
                            continue
                    
                    history.append((command, timestamp))
                
    except Exception as e:
        print(f"Error reading zsh history file: {e}")
        return []
    
    return history

def parse_bash_history(history_file, full_command=False, date_filter=None, command_filter=None):
    history = []
    
    try:
        with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
            current_timestamp = None
            
            for line in f:
                line = line.strip()
                
                # Check if this line is a timestamp
                if line.startswith('#') and len(line) > 1 and line[1:].isdigit():
                    current_timestamp = int(line[1:])
                    continue
                
                if line:
                    timestamp = current_timestamp if current_timestamp else int(datetime.datetime.now().timestamp())
                    
                    # Early date filtering
                    if date_filter:
                        start_time, end_time = date_filter
                        if start_time and timestamp < start_time:
                            current_timestamp = None
                            continue
                        if end_time and timestamp > end_time:
                            current_timestamp = None
                            continue
                    
                    command = extract_command(line, full_command)
                    if command:
                        # Early command filtering
                        if command_filter:
                            if not (command.startswith(command_filter + " ") or command == command_filter):
                                current_timestamp = None
                                continue
                        
                        history.append((command, timestamp))
                        current_timestamp = None
            
    except Exception as e:
        print(f"Error reading bash history file: {e}")
        return []
    
    return history

def extract_command(full_cmd, full_command=False):
    if not full_cmd:
        return ""
    
    if full_command:
        return full_cmd
    else:
        command_parts = full_cmd.split()
        if command_parts:
            first_word = command_parts[0]
            # Handle malformed entries
            if first_word.endswith("'") and (first_word.isdigit() or first_word in ["35'", "00;35'"]):
                if full_cmd.startswith("export"):
                    return "export"
                else:
                    for cmd in ["export", "echo", "set", "alias"]:
                        if cmd in full_cmd:
                            return cmd
                    return "malformed"
            else:
                return first_word
        return ""

def parse_history(history_file, full_command=False, shell_type=None, date_filter=None, command_filter=None):
    if shell_type is None:
        shell_type = detect_shell_type(history_file)
    
    if shell_type == 'zsh':
        return parse_zsh_history(history_file, full_command, date_filter, command_filter)
    elif shell_type in ['bash', 'bash_timestamped']:
        return parse_bash_history(history_file, full_command, date_filter, command_filter)
    else:
        print(f"Unknown shell type: {shell_type}")
        return []

def load_aliases():
    aliases = {}
    alias_sources = {}
    alias_files = [
        os.path.expanduser("~/.aliases"),
        os.path.expanduser("~/.bash_aliases"),
        os.path.expanduser("~/.zshrc"),
        os.path.expanduser("~/.bashrc"),
    ]
    
    for file_path in alias_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        
                        if line.startswith('alias ') and '=' in line:
                            alias_def = line[6:]
                            if '=' in alias_def:
                                alias_name, alias_cmd = alias_def.split('=', 1)
                                alias_cmd = alias_cmd.strip().strip('\'"')
                                if alias_cmd:
                                    base_cmd = alias_cmd.split()[0]
                                    aliases[alias_name.strip()] = base_cmd
                                    alias_sources[alias_name.strip()] = os.path.basename(file_path)
                                
            except Exception:
                continue
    
    return aliases, alias_sources

def show_alias_summary(aliases, alias_sources, history, resolved_history):
    if not aliases:
        return {}
    
    used_aliases = []
    alias_contributions = {}
    
    for alias_name, resolved_cmd in aliases.items():
        if alias_name != resolved_cmd:
            alias_count = sum(1 for cmd, _ in history if cmd.split()[0] == alias_name)
            if alias_count > 0:
                used_aliases.append(f"{alias_name}→{resolved_cmd}")
                if resolved_cmd not in alias_contributions:
                    alias_contributions[resolved_cmd] = []
                alias_contributions[resolved_cmd].append(alias_name)
    
    if used_aliases:
        print(f"Resolved aliases: {', '.join(used_aliases)}")
        print()
    
    return alias_contributions

def resolve_command(command, aliases):
    return aliases.get(command, command)

def filter_commands(history, exclude_list):
    if not exclude_list:
        return history
    
    exclude_set = set(exclude_list)
    filtered = []
    for command, timestamp in history:
        base_cmd = command.split()[0] if command else command
        if base_cmd not in exclude_set:
            filtered.append((command, timestamp))
    
    return filtered

def get_command_correlations(history, target_command, window_seconds=300):
    correlations = defaultdict(int)
    
    sorted_history = sorted(history, key=lambda x: x[1])
    
    for i, (cmd, timestamp) in enumerate(sorted_history):
        if cmd == target_command:
            for j in range(max(0, i-10), min(len(sorted_history), i+11)):
                if i != j:
                    other_cmd, other_time = sorted_history[j]
                    if abs(other_time - timestamp) <= window_seconds and other_cmd != target_command:
                        correlations[other_cmd] += 1
    
    return correlations

def parse_date_filter(date_filter):
    now = datetime.datetime.now()
    
    if date_filter == "1h" or date_filter == "hour":
        start_time = (now - datetime.timedelta(hours=1)).timestamp()
        return int(start_time), None
    elif date_filter == "24h" or date_filter == "day":
        start_time = (now - datetime.timedelta(hours=24)).timestamp()
        return int(start_time), None
    elif date_filter == "today":
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return int(start_of_day.timestamp()), None
    elif date_filter == "week" or date_filter == "7d":
        start_time = (now - datetime.timedelta(days=7)).timestamp()
        return int(start_time), None
    elif date_filter == "month" or date_filter == "30d":
        start_time = (now - datetime.timedelta(days=30)).timestamp()
        return int(start_time), None
    elif date_filter == "year" or date_filter == "365d":
        start_time = (now - datetime.timedelta(days=365)).timestamp()
        return int(start_time), None
    else:
        try:
            if ":" in date_filter:
                start_str, end_str = date_filter.split(":")
                start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d")
                end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d") + datetime.timedelta(days=1)
                return int(start_date.timestamp()), int(end_date.timestamp())
            else:
                date_obj = datetime.datetime.strptime(date_filter, "%Y-%m-%d")
                start_time = int(date_obj.timestamp())
                end_time = int((date_obj + datetime.timedelta(days=1)).timestamp())
                return start_time, end_time
        except ValueError:
            print(f"Error: Invalid date format '{date_filter}'")
            print("Use: 1h, 24h, day, week, month, year, today, YYYY-MM-DD, or YYYY-MM-DD:YYYY-MM-DD")
            return None, None

def show_command_analysis(history, target_command, num_commands=10, show_timeline=False, show_correlations=False):
    if not history:
        print(f"No '{target_command}' commands found in history")
        return
    
    most_common = Counter([item[0] for item in history]).most_common(num_commands)
    actual_count = len(most_common)
    print(f"=== TOP {actual_count} '{target_command.upper()}' VARIATIONS ===")
    print(f"Total '{target_command}' executions: {len(history):,}")
    print()
    
    for i, (command, count) in enumerate(most_common, 1):
        display_cmd = command if len(command) <= 50 else command[:47] + "..."
        print(f"{i:2d}. {display_cmd:<50} ({count:,} times)")
    
    if show_correlations and len(history) > 1:
        correlations = get_command_correlations(history, target_command)
        if correlations:
            print(f"\n=== COMMANDS OFTEN USED WITH '{target_command.upper()}' ===")
            top_correlations = sorted(correlations.items(), key=lambda x: x[1], reverse=True)[:5]
            for cmd, count in top_correlations:
                print(f"  {cmd:<20} ({count} times)")
    
    if show_timeline:
        timestamps = [item[1] for item in history]
        if timestamps:
            most_recent = max(timestamps)
            oldest = min(timestamps)
            recent_date = datetime.datetime.fromtimestamp(most_recent)
            oldest_date = datetime.datetime.fromtimestamp(oldest)
            
            print(f"\n=== USAGE TIMELINE ===")
            print(f"First used: {oldest_date.strftime('%B %d, %Y at %H:%M')}")
            print(f"Last used:  {recent_date.strftime('%B %d, %Y at %H:%M')}")
            
            total_days = (recent_date - oldest_date).days + 1
            if total_days > 0:
                avg_per_day = len(history) / total_days
                print(f"Average:    {avg_per_day:.1f} times per day over {total_days} days")

def smart_defaults(args):
    # Auto-enable timeline for development commands
    if args.command:
        dev_commands = ['git', 'python', 'python3', 'node', 'npm', 'cargo', 'go', 'java', 'mvn', 'gradle']
        if args.command.lower() in dev_commands and not args.timeline:
            args.timeline = True
            if not args.debug:
                print(f"Auto-enabled timeline for {args.command}")
    
    # Auto-detect recent activity requests
    recent_keywords = ['today', 'recent', 'latest', 'now']
    if any(keyword in ' '.join(sys.argv).lower() for keyword in recent_keywords):
        if not args.date:
            args.date = '24h'
            if not args.debug:
                print("Auto-filtered to last 24 hours")
    
    # Smart number defaults
    if args.advanced and args.number == 10:
        args.number = 15
    elif args.command and args.number == 10:
        args.number = 20
    
    return args

def show_basic_analysis(history, num_commands=10):
    if not history:
        print("No commands found in history")
        return
    
    most_common = Counter([item[0] for item in history]).most_common(num_commands)
    for i, (command, count) in enumerate(most_common, 1):
        print(f"{i:2d}. {command:<15} {count}")

def show_advanced_analysis(history, num_commands=10):
    if not history:
        print("No commands found in history")
        return
    
    print(f"Analyzed {len(history):,} commands\n")
    
    print(f"=== TOP {num_commands} MOST USED COMMANDS ===")
    most_common = Counter([item[0] for item in history]).most_common(num_commands)
    for i, (command, count) in enumerate(most_common, 1):
        print(f"{i:2d}. {command:<15} ({count:,} times)")
    
    timestamps = [item[1] for item in history]
    if timestamps:
        start_date = datetime.datetime.fromtimestamp(min(timestamps))
        end_date = datetime.datetime.fromtimestamp(max(timestamps))
        total_days = (end_date - start_date).days + 1
        
        print(f"\n=== TIME RANGE ANALYSIS ===")
        print(f"Data from: {start_date.strftime('%B %d, %Y')}")
        print(f"Data to:   {end_date.strftime('%B %d, %Y')}")
        print(f"Total days: {total_days:,}")
        print(f"Average commands per day: {len(history) / total_days:.1f}")
    
    print(f"\n=== DAILY ACTIVITY ANALYSIS ===")
    daily_counts = defaultdict(int)
    for _, timestamp in history:
        date = datetime.datetime.fromtimestamp(timestamp).date()
        daily_counts[date] += 1
    
    if daily_counts:
        max_day = max(daily_counts.values())
        min_day = min(daily_counts.values())
        avg_day = sum(daily_counts.values()) / len(daily_counts)
        
        print(f"Most active day: {max_day:,} commands")
        print(f"Least active day: {min_day:,} commands")
        print(f"Average per active day: {avg_day:.1f} commands")
        print(f"Days with activity: {len(daily_counts):,}")
    
    print(f"\n=== COMMAND DIVERSITY ===")
    unique_commands = len(set(item[0] for item in history))
    print(f"Unique commands: {unique_commands:,}")
    print(f"Total executions: {len(history):,}")
    print(f"Average uses per command: {len(history) / unique_commands:.1f}")
    
    single_use = [cmd for cmd, count in Counter([item[0] for item in history]).items() if count == 1]
    print(f"Commands used only once: {len(single_use):,} ({len(single_use)/unique_commands*100:.1f}%)")

def write_output(content, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nReport saved to: {output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def capture_output(func, *args, **kwargs):
    import io
    from contextlib import redirect_stdout
    
    output = io.StringIO()
    with redirect_stdout(output):
        func(*args, **kwargs)
    return output.getvalue()

def main():
    parser = argparse.ArgumentParser(description='Analyze command frequency from shell history (bash, zsh)')
    parser.add_argument('-a', '--advanced', action='store_true', 
                        help='Show detailed analysis instead of just top commands')
    parser.add_argument('-f', '--file', type=str, 
                        help='Specify custom history file path')
    parser.add_argument('-s', '--shell', type=str, choices=['bash', 'zsh', 'auto', 'all'],
                        default='current', help='Specify shell type (current shell by default, use "all" to search all shells)')
    parser.add_argument('-n', '--number', type=int, default=10,
                        help='Number of top commands to show')
    parser.add_argument('-d', '--date', type=str,
                        help='Filter by date range. Options: 1h, 24h, day, week, month, year, today, YYYY-MM-DD, or YYYY-MM-DD:YYYY-MM-DD')
    parser.add_argument('-c', '--command', type=str,
                        help='Analyze frequency of a specific command and its variations')
    parser.add_argument('-t', '--timeline', action='store_true',
                        help='Show usage timeline (only works with -c flag)')
    parser.add_argument('-x', '--exclude', type=str,
                        help='Exclude commands (comma-separated list)')
    parser.add_argument('-o', '--output', type=str,
                        help='Save output to file')
    parser.add_argument('--correlations', action='store_true',
                        help='Show command correlations (only works with -c flag)')
    parser.add_argument('--resolve-aliases', action='store_true',
                        help='Resolve shell aliases to their actual commands')
    parser.add_argument('--list-files', action='store_true',
                        help='List available history files for all shells')
    parser.add_argument('--debug', action='store_true',
                        help='Show debug information during processing')
    
    args = parser.parse_args()
    
    args = smart_defaults(args)
    
    if args.list_files:
        print("Searching for history files...")
        available_files = find_history_files()
        current_shell = detect_current_shell()
        if current_shell:
            print(f"Current shell: {current_shell}")
        
        if available_files:
            print("Found history files:")
            for shell, path in available_files.items():
                marker = " (current)" if shell == current_shell else ""
                print(f"  {shell}: {path}{marker}")
        else:
            print("No history files found")
        return
    
    # Validate flag combinations
    if args.timeline and not args.command:
        print("Error: -t/--timeline flag can only be used with -c/--command flag")
        return
    
    if args.correlations and not args.command:
        print("Error: --correlations flag can only be used with -c/--command flag")
        return
    
    # Find history file
    if args.file:
        history_file = args.file
        if not os.path.exists(history_file):
            print(f"Error: File not found: {history_file}")
            return
        shell_type = args.shell if args.shell not in ['current', 'auto', 'all'] else None
    else:
        if args.shell == 'current':
            current_shell = detect_current_shell()
            if current_shell:
                history_file = find_history_file_for_shell(current_shell)
                if history_file:
                    shell_type = current_shell
                else:
                    print(f"No history file found for current shell ({current_shell})")
                    print("Use --list-files to see available options or -s all to search all shells")
                    return
            else:
                print("Could not detect current shell, falling back to search all available")
                args.shell = 'all'
        
        if args.shell == 'all' or args.shell == 'auto':
            available_files = find_history_files()
            if not available_files:
                print("No shell history files found in common locations")
                print("Use -f flag to specify custom path or --list-files to see what we're looking for")
                return
            
            # Use the first available file, preferring zsh, then bash
            for preferred_shell in ['zsh', 'bash']:
                if preferred_shell in available_files:
                    history_file = available_files[preferred_shell]
                    shell_type = preferred_shell
                    break
        elif args.shell in ['bash', 'zsh']:
            history_file = find_history_file_for_shell(args.shell)
            shell_type = args.shell
            if not history_file:
                print(f"No {args.shell} history file found")
                return
    
    # Parse history with optimizations
    use_full_commands = bool(args.command)
    date_filter_parsed = None
    command_filter = args.command if args.command else None
    
    if args.date:
        date_filter_parsed = parse_date_filter(args.date)
        if date_filter_parsed[0] is None and date_filter_parsed[1] is None:
            return
    
    if args.debug:
        print(f"Parsing {shell_type} history: {history_file}")
        print(f"Full command mode: {use_full_commands}")
        if date_filter_parsed:
            print(f"Early date filtering enabled")
        if command_filter:
            print(f"Early command filtering for: {command_filter}")
    
    history = parse_history(history_file, full_command=use_full_commands, shell_type=shell_type, 
                          date_filter=date_filter_parsed, command_filter=command_filter)
    
    if not history:
        print("No commands found in history file")
        return
    
    if not args.debug:
        print(f"Analyzed {len(history):,} commands from {shell_type} history")
    else:
        print(f"Loaded {len(history):,} commands from history")
    
    # Load aliases and resolve if requested
    if args.resolve_aliases:
        if args.debug:
            print("Loading and resolving aliases...")
        aliases, alias_sources = load_aliases()
        
        if aliases:
            resolved_history = []
            for command, timestamp in history:
                if use_full_commands:
                    parts = command.split()
                    if parts:
                        resolved_cmd = resolve_command(parts[0], aliases)
                        full_resolved = resolved_cmd + (' ' + ' '.join(parts[1:]) if len(parts) > 1 else '')
                        resolved_history.append((full_resolved, timestamp))
                    else:
                        resolved_history.append((command, timestamp))
                else:
                    resolved_cmd = resolve_command(command, aliases)
                    resolved_history.append((resolved_cmd, timestamp))
            
            alias_contributions = show_alias_summary(aliases, alias_sources, history, resolved_history)
            history = resolved_history
    
    # Apply remaining filters
    if args.exclude:
        exclude_list = [cmd.strip() for cmd in args.exclude.split(',')]
        original_count = len(history)
        history = filter_commands(history, exclude_list)
        print(f"Excluded {len(exclude_list)} commands, filtered from {original_count:,} to {len(history):,} commands")
        print()
    
    if args.date and not date_filter_parsed:
        start_time, end_time = parse_date_filter(args.date)
        if start_time is None and end_time is None:
            return
        
        original_count = len(history)
        filtered = []
        for command, timestamp in history:
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            filtered.append((command, timestamp))
        history = filtered
        
        period_names = {
            "1h": "last hour", "hour": "last hour",
            "24h": "last 24 hours", "day": "last 24 hours", "today": "today",
            "week": "last week", "7d": "last week",
            "month": "last month", "30d": "last month",
            "year": "last year", "365d": "last year"
        }
        period_name = period_names.get(args.date, f"date range {args.date}")
        
        print(f"Filtered to {len(history):,} commands from {period_name} (was {original_count:,})")
        if not history:
            print("No commands found in specified date range")
            return
        print()
    
    def run_analysis():
        if args.command:
            cmd_history = []
            for command, timestamp in history:
                if command.startswith(args.command + " ") or command == args.command:
                    cmd_history.append((command, timestamp))
            show_command_analysis(cmd_history, args.command, args.number, args.timeline, args.correlations)
        elif args.advanced:
            show_advanced_analysis(history, args.number)
        else:
            show_basic_analysis(history, args.number)
    
    # Run analysis and optionally save to file
    if args.output:
        output_content = capture_output(run_analysis)
        write_output(output_content, args.output)
        run_analysis()
    else:
        run_analysis()

if __name__ == "__main__":
    main()