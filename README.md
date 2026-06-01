# 📨 Email-IMAP-Checker — Professional, high-performance email validation tool with IMAP protocol support

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/zougar99/Email-IMAP-Checker/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/zougar99/Email-IMAP-Checker?style=social)](https://github.com/zougar99/Email-IMAP-Checker)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-blue)](https://github.com/zougar99/Email-IMAP-Checker)

> Professional, high-performance email validation tool with IMAP protocol support. Validates email accounts in bulk, checks IMAP/SMTP credentials, and generates detailed reports.

---

## 📖 Table of Contents
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Screenshots](#-screenshots)
- [Roadmap](#-roadmap)
- [FAQ](#-faq)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features
- ✔ **IMAP Validation** — Checks email credentials against IMAP servers
- ✔ **SMTP Check** — Validates SMTP login capabilities
- ✔ **Bulk Processing** — Check thousands of accounts from CSV/TXT files
- ✔ **Multi-Threading** — High-speed concurrent checking with configurable threads
- ✔ **Result Filtering** — Sort and filter results (valid/invalid/error)
- ✔ **Export** — Save validated accounts to CSV, JSON, TXT
- ✔ **Proxy Support** — HTTP/HTTPS/SOCKS5 proxy per connection

---

## 🔮 How It Works

```
  Input ──► Processing Pipeline ──► Output
  ┌────────┐   ┌────────┐   ┌────────┐
  │ Data   │──►│ Engine │──►│ Result │
  │ Source │   │ Logic  │   │        │
  └────────┘   └────────┘   └────────┘
```

1. **Input** — Load data from file, API, or user input
2. **Process** — Core engine applies logic/analysis/transformation
3. **Output** — Results displayed in UI, saved to file, or sent via API

---

## 💻 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| UI | CustomTkinter |
| Protocol | imaplib + smtplib |
| Concurrency | ThreadPoolExecutor |
| Storage | SQLite |

---

## 🚀 Installation

```bash
git clone https://github.com/zougar99/Email-IMAP-Checker.git
cd Email-IMAP-Checker
pip install -r requirements.txt
```

---

## 📄 Configuration

Create a `config.yaml` or `.env` file in the project root:

```yaml
# Application settings
debug: false
port: 8080
theme: dark
language: en
```

---

## 🧰 Usage Guide

1. Launch: `python main.py`
2. Upload email list (CSV/TXT, one per line)
3. Configure IMAP server settings or auto-detect
4. Set thread count and proxy (optional)
5. Click **Start Check**
6. Export results when complete

---

## 🖼 Screenshots

> *(Screenshots coming soon. PRs welcome!)*

---

## 🔄 Roadmap

- 🟢 Web dashboard
- 🟡 Mobile companion app
- ⚫ API access
- ⚫ Plugin system
- ⚫ Multi-language support

---

## ❓ FAQ

### How many threads can I use?
Depends on your network; 10-50 threads recommended.

### Does it store my credentials?
No — credentials are processed in memory and never saved to disk.

---

## 🚧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **App won't start** | Check Python version (3.10+); run `pip install -r requirements.txt` |
| **No output** | Check logs in `logs/` folder; enable debug mode in config |
| **Performance issues** | Close other applications; reduce batch size in config |
| **Dependency errors** | Create fresh venv: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📐 License
Distributed under the **MIT License**. See [`LICENSE`](https://github.com/zougar99/Email-IMAP-Checker/blob/main/LICENSE) for more information.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/zougar99">zougar99</a>
</p>
