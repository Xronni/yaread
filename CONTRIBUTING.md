# Contributing to YaRead

Thank you for your interest in contributing to **YaRead**! 📚✨

We welcome contributions of all kinds: bug fixes, feature suggestions, documentation enhancements, UI/UX polish, translations, soundtrack additions, and code improvements.

---

## 🛠️ Local Development Setup

### System Prerequisites
- **Linux** (Ubuntu 22.04+, Debian 12+, Arch Linux, Fedora) or **Windows 10/11**
- **Python 3.10 or higher**

#### Install dependencies on Linux (Ubuntu / Debian):
```bash
sudo apt update && sudo apt install -y python3 python3-pyqt6 python3-pygame python3-fitz python3-bs4 python3-lxml python3-ebooklib
```

#### Install dependencies on Arch Linux:
```bash
sudo pacman -S python python-pyqt6 python-pygame python-pymupdf python-beautifulsoup4 python-lxml
pip install ebooklib --break-system-packages
```

#### Install dependencies on Fedora:
```bash
sudo dnf install python3 python3-pyqt6 python3-pygame python3-pymupdf python3-beautifulsoup4 python3-lxml python3-ebooklib
```

#### Using Python venv & pip:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Running Locally

```bash
git clone https://github.com/Xronni/yaread.git
cd yaread
./run.sh
```

---

## 🧪 Automated Testing & Verification

Before opening a Pull Request, verify that all files, syntax, and assets pass the test suite:

```bash
./test.sh
```

The verification suite checks Python syntax, bytecode compilation, presence and integrity of all 12 soundtrack loops, assets, and dependencies.

---

## 📦 Pull Request Guidelines

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feat/my-improvement
   ```
2. Make your changes and test them locally with `./run.sh` and `./test.sh`.
3. Follow Conventional Commits format (`feat: ...`, `fix: ...`, `docs: ...`).
4. Push your branch and submit a Pull Request on GitHub.
