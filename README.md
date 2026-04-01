# PyXSSHunter 🚀

**A stealthy, modern Python tool for discovering Cross-Site Scripting (XSS) vulnerabilities.**

PyXSSHunter is a fast and user-friendly automated XSS scanner with strong stealth capabilities, designed for bug bounty hunters, penetration testers, and security researchers.

## ✨ Features

- **Reflected XSS Detection** with smart payload injection
- **Advanced Stealth Mode** (3 levels: low, medium, high)
    - Random realistic User-Agents
    - Random headers & referrers
    - Human-like random delays
    - Proxy support (HTTP/SOCKS5)
- Beautiful rich CLI interface with progress bar
- Automatic HTML report generation with vulnerable URLs highlighted
- Docker support for easy deployment
- Clean, modular and extensible codebase

## 🛠️ Installation

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/PyXSSHunter.git
cd PyXSSHunter

# Build the Docker image
docker build -t pyxsshunter:latest -f docker/Dockerfile .

# Run a scan (see usage below)
git clone https://github.com/yourusername/PyXSSHunter.git
cd PyXSSHunter

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate # Linux/macOS

pip install -r requirements.txt