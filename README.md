# freq - Shell History Analyzer

A minimal CLI tool to analyze your shell command usage patterns. Gives insights into your most-used commands and usage trends.

## Features

- **Multi-shell support** - Works with both Bash and Zsh
- **Smart analysis** - Basic stats or detailed breakdowns
- **Command-specific analysis** - Deep dive into specific commands and their variations
- **Timeline tracking** - See usage patterns over time
- **Alias resolution** - Resolves shell aliases to show actual command usage
- **Flexible filtering** - Filter by date ranges, exclude commands, analyze specific time periods
- **Command correlations** - Find commands often used together
- **Export reports** - Save analysis to files

## Quick Start

```bash
# Clone and install
git clone https://github.com/Tecttano/freq.git
cd freq
chmod +x install.sh
./install.sh

# Basic usage
freq                    # Show top 10 commands
freq -n 20             # Show top 20 commands
freq -a                # Detailed analysis
```

## Installation

### Quick Install

1. Clone the repository:
```bash
git clone https://github.com/Tecttano/freq.git
cd freq
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Start using `freq`:
```bash
freq
freq -a
freq -c git
```

### Manual Installation

If you prefer to install manually:

```bash
# Copy to system directory
sudo cp freq.py /usr/local/bin/freq
sudo chmod +x /usr/local/bin/freq
```

### User Installation (No sudo required)

If you don't have sudo access:

```bash
# Create local bin directory
mkdir -p ~/.local/bin

# Copy the script
cp freq.py ~/.local/bin/freq
chmod +x ~/.local/bin/freq

# Add to PATH (add this to your ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Reload your shell
source ~/.bashrc  # or source ~/.zshrc
```

## Usage Examples

### Basic Analysis
```bash
freq                    # Top 10 commands
freq -n 5              # Top 5 commands
freq -n 20             # Top 20 commands
```

### Advanced Analysis
```bash
freq -a                # Detailed breakdown with stats
freq -a -n 15          # Detailed analysis, top 15 commands
```

### Command-Specific Analysis
```bash
freq -c git            # Analyze all git command variations
freq -c python3        # Analyze python3 usage patterns
freq -c git --timeline # Git usage with timeline
freq -c npm --correlations  # Commands often used with npm
```

### Date Filtering
```bash
freq -d today          # Today's commands only
freq -d week           # Last 7 days
freq -d month          # Last 30 days
freq -d 2025-05-01     # Specific date
freq -d 2025-05-01:2025-05-31  # Date range
```

### Filtering and Exclusions
```bash
freq -x "ls,cd,pwd"    # Exclude common navigation commands
freq --resolve-aliases # Resolve shell aliases
freq -c git -d week -x "git status"  # Git commands this week, exclude status
```

### Export Reports
```bash
freq -a -o report.txt                    # Save detailed analysis
freq -c git --timeline -o git_report.txt # Save git analysis
```

### Advanced Combinations
```bash
# Detailed analysis with aliases resolved, excluding noise
freq -a --resolve-aliases -x "ls,cd,clear" -n 15

# Git analysis for last month with timeline and correlations
freq -c git -d month --timeline --correlations

# Today's activity excluding basic commands, save report
freq -d today -x "ls,cd,pwd,clear" -o daily_activity.txt
```

## Command Options

| Option | Description |
|--------|-------------|
| `-n, --number` | Number of top commands to show (default: 10) |
| `-a, --advanced` | Show detailed analysis with statistics |
| `-c, --command` | Analyze specific command and variations |
| `-t, --timeline` | Show usage timeline (use with `-c`) |
| `-d, --date` | Filter by date range (1h, 24h, week, month, year, today, YYYY-MM-DD) |
| `-x, --exclude` | Exclude commands (comma-separated) |
| `--correlations` | Show command correlations (use with `-c`) |
| `--resolve-aliases` | Resolve shell aliases to actual commands |
| `-o, --output` | Save output to file |
| `-s, --shell` | Specify shell type (bash, zsh, all) |
| `-f, --file` | Use custom history file |
| `--list-files` | List available history files |
| `--debug` | Show debug information |

## Sample Output

### Basic Analysis
```
Analyzed 959 commands from zsh history
 1. ls              138
 2. git             84
 3. python3         80
 4. sudo            67
 5. nano            45
```

### Advanced Analysis
```
=== TOP 10 MOST USED COMMANDS ===
 1. ls              (138 times)
 2. git             (84 times)
 3. python3         (80 times)

=== TIME RANGE ANALYSIS ===
Data from: April 17, 2025
Data to:   May 28, 2025
Total days: 42
Average commands per day: 22.8

=== COMMAND DIVERSITY ===
Unique commands: 108
Commands used only once: 42 (38.9%)
```

### Command-Specific Analysis
```
=== TOP 10 'GIT' VARIATIONS ===
Total 'git' executions: 84

 1. git init                     (8 times)
 2. git commit -m "Initial"      (8 times)
 3. git add .                    (7 times)
 4. git push origin main         (6 times)

=== USAGE TIMELINE ===
First used: April 17, 2025 at 09:22
Last used:  May 23, 2025 at 12:04
Average: 2.3 times per day over 37 days
```

## Smart Features

- **Auto-timeline**: Automatically enables timeline for development commands (git, python3, node, etc.)
- **Recent activity detection**: Auto-filters to last 24 hours when keywords like "today" or "recent" are detected
- **Alias resolution**: Finds and resolves aliases from `.bashrc`, `.zshrc`, and other config files
- **Early filtering**: Optimized parsing for large history files
- **Cross-shell detection**: Automatically detects and uses the appropriate shell history format

## Requirements

- **Python 3.6+**
- **Linux/Unix-like system** (Windows WSL supported)
- **Bash or Zsh shell**
- **Optional**: `psutil` package for enhanced shell detection

## Supported Shells

- **Zsh** - Full support including timestamped history
- **Bash** - Full support with and without timestamps
- **Auto-detection** - Automatically detects shell type and history format

## History File Locations

The tool automatically searches common locations:

**Zsh:**
- `~/.zsh_history`
- `~/.histfile`
- `/root/.zsh_history`

**Bash:**
- `~/.bash_history`
- `/root/.bash_history`

## Troubleshooting

### Command not found after installation
```bash
# Check if installed correctly
which freq
ls -la /usr/local/bin/freq

# If using user install, ensure PATH is set
echo $PATH | grep -o ~/.local/bin
```

### No history found
```bash
# List available history files
freq --list-files

# Use specific file
freq -f /path/to/your/history/file

# Check your shell's history settings
echo $HISTFILE
```

### Permission errors
```bash
# For user installation (no sudo required)
./install.sh user

# Or install to user directory manually
cp freq.py ~/.local/bin/freq
```

## Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various shell configurations
5. Submit a pull request

### Testing

```bash
# Test basic functionality
freq --debug
freq --list-files

# Test with different shells
freq -s bash
freq -s zsh

# Test date filtering
freq -d today --debug
```

## Uninstall

```bash
# Using install script
./install.sh uninstall

# Manual removal
sudo rm /usr/local/bin/freq

# User installation
rm ~/.local/bin/freq
```

## License

MIT License - see LICENSE file for details.

## Author

Created by [Tecttano](https://github.com/Tecttano)

---
