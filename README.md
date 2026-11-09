<div align="center">

# 📨 Email IMAP Checker

**A desktop and command-line tool for checking authorized IMAP account access.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Interface](https://img.shields.io/badge/Interface-Tkinter%20%7C%20CLI-0d9488)](#usage)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Quick start](#quick-start) · [Usage](#usage) · [Results](#understanding-results) · [Security](#security--privacy) · [Troubleshooting](#troubleshooting)

</div>

---

> **Use responsibly:** Check only accounts you own or have explicit permission to administer. Respect provider policies and rate limits. This project handles sensitive passwords: read [Security & privacy](#security--privacy) before running it.

## Overview

Email IMAP Checker reads an `email:password` text file and attempts IMAP login over TLS using provider settings in `hoster.dat`. Run it through the desktop GUI, the interactive launcher, or directly from the command line. Results distinguish a rejected login from a connection error or a missing provider configuration.

### Features

- **Desktop GUI** — choose an input file, configure checks, watch progress and open results.
- **Command-line mode** — control concurrency, timeouts, and optional host probing.
- **Non-destructive input** — malformed lines are skipped; the original file is not rewritten.
- **Categorized results** — separate valid, rejected, network-error, and unknown-provider addresses.
- **File monitor** — rerun the checker when a watched file changes.
- **Local statistics** — inspect previous results and provider distribution.
- **TLS verification** — certificates and hostnames are checked for IMAP connections.
- **Offline tests** — unit and integration tests use mocked connections, not real accounts.

## Requirements

- Python **3.10 or newer**.
- `gevent` (installed from `requirements.txt`).
- Tkinter and a graphical desktop for the GUI. On some Linux distributions Tkinter is a separate system package, commonly named `python3-tk`.
- Network access to the relevant IMAP servers for actual checks.

## Quick start

Clone the repository and create an isolated Python environment:

```bash
git clone https://github.com/zougar99/Email-IMAP-Checker.git
cd Email-IMAP-Checker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

On Windows PowerShell, use the following instead:

```powershell
git clone https://github.com/zougar99/Email-IMAP-Checker.git
cd Email-IMAP-Checker
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Choose **GUI Mode** or **CLI Mode** in the launcher. Run commands from the repository directory so the program can find `hoster.dat` and its other data files.

## Preparing an input file

Create a UTF-8 text file containing one account per line. For example, using fictional credentials:

```text
# Lines beginning with # are comments
user@example.com:example-password
other@example.org:password:with:colons
```

- The first `:` separates the address from its password; additional colons belong to the password.
- Blank lines, comments, malformed addresses and entries without a password are skipped.
- The parser accepts common address formats, not every address allowed by the email RFCs.
- The checker does **not** modify the input file.
- `input.txt` is tracked by Git. **Do not put real credentials in it or commit credential files.** Prefer a private file outside the repository and select it using the GUI or `-i`.

## Usage

### Desktop application

```bash
python gui.py
```

1. Select your private input file with **Browse**.
2. Choose the worker count and timeout. Start with a low worker count.
3. Optionally enable unknown-host checks or disable saving rejected addresses.
4. Select **Start Checking** and monitor the progress and log.
5. Open the results folder when the run finishes; use **Stop** to interrupt a run.

The GUI requires a working display; use the CLI on a headless machine.

### Command-line checker

```bash
python atr3.py -i /path/to/private-accounts.txt -t 10 -to 10
```

| Option | Default | Description |
| --- | --- | --- |
| `-i`, `--input` | `input.txt` | Path to a UTF-8 account list. |
| `-t`, `--threads` | `10` | Concurrent gevent workers, from 1 to 100. |
| `-to`, `--timeout` | `10` | Positive per-connection timeout in seconds. |
| `-uh`, `--unknownhosts` | `False` | Use `-uh True` to probe possible hosts for unknown domains. |
| `-iu`, `--invunma` | `True` | Use `-iu False` to disable saving rejected and unmatched addresses. |
| `-g`, `--grabber` | `False` | Optional legacy mailbox-content feature; see the security warning below. |

Boolean options take a value, for example `-uh True` or `-iu False`. The legacy resume option is disabled because old checkpoints could skip unfinished accounts. Run `python atr3.py --help` for the full legacy option list; some legacy options do not control the current output layout.

### File monitor

```bash
python auto_checker.py -i /path/to/private-accounts.txt -t 5
```

The monitor checks for content changes every five seconds. **Each change rechecks the entire file**, not just new lines. It does not erase, move, or archive the input; changes made during a run are picked up on the next interval. Stop with `Ctrl+C`.

### Statistics

```bash
python stats.py
```

The launcher also offers a statistics view. The GUI's **Statistics** button shows current-run counts and domain distribution.

## Understanding results

Each run creates a timestamped directory under `M-P-V-I/`:

```text
M-P-V-I/<run>/
├── mail_pass_valid.txt                   # successful addresses
├── mail_pass_invalid.txt                 # rejected login addresses, if enabled
├── mail_unmatched.txt                   # unknown-provider addresses, if enabled
├── mail_errors.txt                      # connection/protocol errors
└── valid_with_passwords/
    └── mail_pass_valid_with_password.txt # plaintext credentials — sensitive!
```

Valid addresses are also grouped by domain under `isp+boite/`. The GUI log includes live counts of errors and unmatched providers.

| Result | Meaning |
| --- | --- |
| **Valid** | The IMAP server accepted the login. |
| **Invalid** | The server rejected the login; this can also reflect provider policy or authentication requirements, not necessarily a wrong password. |
| **Error** | A connection, TLS, timeout, or protocol problem occurred. This does **not** prove the password is invalid. |
| **Unmatched** | No provider configuration was found and no host was discovered. |

There are no automatic retries. Check provider documentation before retrying: some services require an app password or OAuth, restrict IMAP, or do not expose a standard third-party IMAP server. This application uses password-based IMAP login; it does not implement OAuth.

## Provider configuration

`hoster.dat` maps domains to IMAP servers, one entry per line:

```text
example.com:imap.example.com:993
```

Check the hostname and port against the provider's current documentation. Automatic unknown-host probing is disabled by default and may not discover the correct server. Some entries may require local bridge software or provider-specific setup.

## Security & privacy

- **Passwords are stored in plaintext** in the input and in the successful-credentials output. Restrict file access, avoid shared machines, and delete sensitive files when no longer needed.
- The optional legacy **Grab Emails** feature can save mailbox contents and credentials, potentially in paths outside the ignored results directory. Leave it disabled unless explicitly needed and authorized; handle and remove those files securely.
- Generated result folders are ignored by Git, but arbitrary credential files and grabbed content are not necessarily ignored. Always inspect `git status` before committing.
- Start with a low concurrency value to reduce the risk of provider rate limits or account lockouts.
- This project is not an SMTP checker and does not implement CSV import, proxies, JSON export, or YAML configuration.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Interactive mode selector. |
| `gui.py` | Tkinter desktop application. |
| `atr3.py` | Main IMAP checker and result writers. |
| `checker_core.py` | Shared input parser and IMAP connection helper. |
| `auto_checker.py` | File-change monitor. |
| `stats.py` | Local results and provider statistics. |
| `hoster.dat` | Domain-to-IMAP-server mappings. |
| `tests/` | Offline unit and CLI integration tests. |

## Troubleshooting

| Problem | What to check |
| --- | --- |
| GUI does not open | Install Tkinter and run in a graphical desktop session. Use `python atr3.py` on headless systems. |
| No accounts processed | Confirm the file is UTF-8 and lines have the `email:password` format. Comments and malformed lines are skipped. |
| Unknown provider | Verify the domain's entry in `hoster.dat` or explicitly enable unknown-host probing. |
| Network or TLS errors | Check connectivity, timeout, the server hostname/port, and its certificate. These errors are not invalid passwords. |
| Login rejected | Confirm the account's IMAP settings, app-password requirements and provider policy. Avoid repeated attempts. |
| Dependency error | Activate the virtual environment and run `pip install -r requirements.txt` again. |

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests use mock IMAP behavior and do not connect to real servers. Real provider compatibility and desktop display behavior should be checked separately in an appropriate environment.

## Contributing

Issues and pull requests are welcome. Keep changes focused, add tests where practical, and **never include real accounts, passwords, or mailbox contents** in examples, logs, or commits.

## License

Distributed under the [MIT License](LICENSE).
