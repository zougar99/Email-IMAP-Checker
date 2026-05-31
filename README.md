# Email IMAP Checker Pro v4.0

A professional, high-performance email validation tool with IMAP protocol support. Validates email accounts across **1,833+ global email providers** from **100+ countries**.

![Version](https://img.shields.io/badge/version-4.0-blue)
![Python](https://img.shields.io/badge/python-3.6+-green)
![Providers](https://img.shields.io/badge/providers-1833+-orange)
![Countries](https://img.shields.io/badge/countries-100+-purple)

---

## Features

### Core Engine (`imop.py`)
- **Multi-threaded Validation**: Process thousands of emails simultaneously using gevent
- **1,833+ Email Providers**: Comprehensive database covering global ISPs
- **IMAP SSL Support**: Secure connection to email servers
- **Auto Host Discovery**: Automatically finds IMAP servers for unknown domains
- **ISP/Boite Sorting**: Automatically sorts valid emails by domain
- **Resume Support**: Continue from where you left off
- **Email Content Grabbing**: Search email contents with custom patterns
- **Session Management**: Results saved in timestamped folders

### GUI (`gui.py`)
- **Modern Professional Interface**: Dark / Light / Blue / Purple themes
- **Real-time Statistics Dashboard**: Live counters for valid/invalid emails
- **Progress Tracking**: Visual progress bar with ETA
- **Output Log**: Color-coded log with timestamps
- **One-click Output Access**: Quick access to result folders

### Auto Monitor (`auto_checker.py`)
- **File Watching**: Monitors `input.txt` for changes
- **Auto Processing**: Runs checker automatically on new lines
- **Processed Line Tracking**: Moves checked lines to `input_processed.txt`

### Statistics (`stats.py`)
- **Results Analysis**: Comprehensive session reports
- **Provider Breakdown**: Emails per ISP/domain
- **Valid/Invalid Ratios**: Success rate calculations

---

## File Structure

```
Email-IMAP-Checker/
├── main.py             # Main launcher with mode selection (GUI/CLI/Auto)
├── gui.py              # Professional GUI application (tkinter)
├── imop.py             # Core IMAP checker engine (main)
├── atr3_original_backup.py  # Backup of original engine
├── auto_checker.py     # Auto-monitoring mode
├── stats.py            # Statistics analyzer
├── hoster.dat          # Email provider database (1,833 providers)
├── matchers.dat        # Email search patterns for grabbing
├── input.txt           # Input file (email:password)
├── requirements.txt    # Python dependencies
├── last_line.log       # Resume position tracker
├── M-P-V-I/            # Output directory
│   └── YYYY-MM-DD_HH-MM-SS/
│       ├── mail_pass_valid.txt
│       ├── mail_pass_invalid.txt
│       └── valid_with_passwords/
│           └── mail_pass_valid_with_password.txt
└── isp+boite/          # Emails sorted by domain
    ├── mail_gmail.com.txt
    ├── mail_yahoo.com.txt
    └── ...
```

---

## Installation

### Requirements
- Python 3.6 or higher
- pip (Python package manager)

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/your-repo/Email-IMAP-Checker.git
cd Email-IMAP-Checker

# 2. Install dependencies
pip install -r requirements.txt

# Or install manually:
pip install gevent
```

---

## Usage

### Method 1: Main Launcher (Recommended)

```bash
python main.py
```

Then select from the menu:
```
[1]  GUI Mode         - Professional Interface
[2]  CLI Mode         - Command Line Interface
[3]  Auto Monitor     - Watch & Process Files
[4]  Statistics       - View Results & Stats
[5]  Help             - Show Documentation
[6]  Exit             - Quit Application
```

### Method 2: GUI Mode (Direct)

```bash
python gui.py
```

### Method 3: CLI Mode (Direct)

```bash
# Basic usage
python atr3.py -i input.txt -t 500 -to 5

# Or using imop.py
python imop.py -i input.txt -t 500 -to 5

# Full options
python imop.py -i input.txt -t 1000 -to 10 -r -b -uh -iu
```

### Method 4: Auto Monitor

```bash
python auto_checker.py
# Or with custom settings:
python auto_checker.py -i input.txt -t 10
```

---

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input file path | `mail_pass.txt` |
| `-o, --output` | Output file path | `mail_pass_valid.txt` |
| `-t, --threads` | Number of concurrent greenlets | `1000` |
| `-to, --timeout` | Connection timeout (seconds) | `5` |
| `-uh` | Check unknown hosts | `True` |
| `-iu` | Save invalid emails | `True` |
| `-g` | Grab email contents | `False` |
| `-ga` | Grab all emails | `False` |
| `-mf` | Matchers file path | `matchers.dat` |
| `-r` | Resume from last position | `False` |
| `-b` | Big file mode (skip line counting) | `False` |
| `-gper` | Grab performance mode (no save) | `False` |

---

## Input Format

The input file (`input.txt`) should contain emails in one of these formats:

```
email@example.com:password
user@domain.com:pass123
```

**Supported formats:**
- `email@domain.com:password` - Email with password
- `email@domain.com` - Email without password (empty login attempt)

**Auto-cleaning:** The tool automatically removes invalid lines (bad format, missing @, etc.)

---

## Output Files

### Main Output (`M-P-V-I/YYYY-MM-DD_HH-MM-SS/`)

| File | Description |
|------|-------------|
| `mail_pass_valid.txt` | Valid email addresses only |
| `mail_pass_invalid.txt` | Invalid email addresses |
| `valid_with_passwords/mail_pass_valid_with_password.txt` | Valid emails with passwords |

### ISP Sorted (`isp+boite/`)

| File | Description |
|------|-------------|
| `mail_gmail.com.txt` | Gmail emails |
| `mail_yahoo.com.txt` | Yahoo emails |
| `mail_outlook.com.txt` | Outlook emails |
| `mail_*` | One file per domain/provider |

---

## Supported Regions

| Region | Providers | Countries |
|--------|-----------|-----------|
| **USA** | 73 | AT&T, Comcast, Verizon, Cox, Charter... |
| **Europe** | 298+ | France, Germany, UK, Spain, Italy, Netherlands... |
| **Asia** | 280+ | Japan, China, Korea, India, Indonesia, Malaysia... |
| **Africa** | 192+ | Morocco, Egypt, Nigeria, Kenya, South Africa... |
| **Middle East** | 39+ | UAE, Saudi Arabia, Israel, Turkey... |
| **South America** | 50+ | Brazil, Mexico, Argentina, Chile, Colombia... |
| **Oceania** | 30+ | Australia, New Zealand... |
| **Scandinavia** | 51+ | Norway, Sweden, Denmark, Finland, Iceland... |

---

## GUI Themes

| Theme | Description |
|-------|-------------|
| **Dark** (Default) | Easy on the eyes for long sessions |
| **Light** | Clean, bright interface |
| **Blue** | Professional blue theme |
| **Purple** | Stylish purple accent |

---

## Tips for Best Results

1. **Optimal Thread Count**: Start with 500 threads, increase if your connection allows
2. **Timeout Setting**: 5-10 seconds works best for most providers
3. **Input Cleaning**: The tool automatically removes invalid lines
4. **Large Files**: Use `-b` flag to skip line counting for files >1M lines
5. **Resume Feature**: If interrupted, use `-r` flag to continue
6. **Unknown Hosts**: Keep `-uh` enabled to auto-discover IMAP servers

---

## Troubleshooting

### Common Issues

**"charmap codec can't decode" error**
- Make sure your terminal supports UTF-8 encoding

**"Python 2.7 detected" error**
- Use `python3` instead of `python` command

**"gevent not found" error**
```bash
pip install gevent
```

**Connection timeouts**
- Increase timeout: `-to 10`
- Reduce threads: `-t 200`

**"No input file found" error**
- Make sure `input.txt` exists in the project directory
- Or specify custom path: `-i path/to/file.txt`

---

## Contact

- **Telegram**: [@werlist99](https://t.me/werlist99)

---

## License

This project is for educational purposes only. Use responsibly and respect the terms of service of email providers.

---

**Email IMAP Checker Pro v4.0** - Professional Email Validation Tool
