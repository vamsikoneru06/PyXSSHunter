# PyXSSHunter 🚀

**A stealthy, modern Python tool for discovering Cross-Site Scripting (XSS) vulnerabilities.**

PyXSSHunter is a fast and user-friendly automated XSS scanner with strong stealth capabilities, designed for bug bounty hunters, penetration testers, and security researchers.

> ⚠️ **Authorized use only.** PyXSSHunter must only be run against systems you own or have explicit, written authorization to test. Unauthorized scanning may violate the Computer Fraud and Abuse Act (CFAA) or equivalent laws in your jurisdiction. Every scan requires the `--i-have-permission` flag to confirm this.

## ✨ Features

- **Reflected XSS Detection** with smart payload injection
- **Stored XSS Detection** (opt-in via `--stored`) — submits payloads to forms found on the page and checks whether they persist and reflect back unsanitized on a later page load
- **DOM-based XSS Detection** (opt-in via `--dom`) — renders injection points (URL hash and query params) in a real headless browser and watches for the payload actually executing (JS dialog triggered), rather than just pattern-matching the HTTP response
- **Advanced Stealth Mode** (3 levels: low, medium, high)
    - Random realistic User-Agents
    - Random headers & referrers
    - Human-like random delays
    - Proxy support (HTTP/SOCKS5)
- Beautiful rich CLI interface with progress bar
- HTML report generation with vulnerable URLs highlighted and a ready-to-run **curl PoC** for each finding
- **PDF report export** (opt-in via `--pdf`)
- **Screenshot-based PoC capture** (opt-in via `--screenshot`) — embeds a screenshot of each finding in the report
- Docker support for easy deployment
- Clean, modular and extensible codebase

## 🛠️ Installation

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/vamsikoneru06/PyXSSHunter.git
cd PyXSSHunter

# Build the Docker image
docker build -t pyxsshunter:latest -f docker/Dockerfile .
```

> The image bundles headless Chromium (for `--dom`/`--screenshot`), so the build downloads ~400MB of browser + OS dependencies and the build takes a few minutes.

### Option 2: Local Install

```bash
# Clone the repository
git clone https://github.com/vamsikoneru06/PyXSSHunter.git
cd PyXSSHunter

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate # Linux/macOS

pip install -r requirements.txt

# --dom and --screenshot need a headless browser binary (not installed by pip alone)
playwright install chromium
```

## 📖 Usage

Every scan requires `--i-have-permission` to confirm you are authorized to test the target. Scans without it are refused.

**Local install:**
```bash
python -m pyxsshunter.cli \
    --url "http://testphp.vulnweb.com/search.php?test=1" \
    --i-have-permission \
    --stealth-level medium \
    --max-payloads 80 \
    --output reports
```

**Using Docker (Windows PowerShell):**
```powershell
docker run --rm `
  -v "${PWD}/reports:/app/reports" `
  pyxsshunter:latest `
  --url "http://testphp.vulnweb.com/search.php?test=1" `
  --i-have-permission `
  --stealth-level medium `
  --max-payloads 80 `
  --output /app/reports
```

### Options

| Flag | Description | Default |
|---|---|---|
| `--url`, `-u` | Target URL to scan (required) | — |
| `--i-have-permission` | Confirms you are authorized to test the target (required) | `False` |
| `--stealth-level` | `low` / `medium` / `high` | `medium` |
| `--proxies` | Path to a file of HTTP/SOCKS5 proxies, one per line | — |
| `--max-payloads` | Max payloads to test | `50` |
| `--output`, `-o` | Directory to save the HTML report | `reports` |
| `--report-name` | Custom report filename (without extension) | auto-generated |
| `--stored` | Also test for stored XSS by submitting payloads to forms on the page. **Writes data to the target** (comments, guestbook entries, etc.) — only use where persisting test data is acceptable. | `False` |
| `--dom` | Also test for DOM-based XSS by rendering injection points in a headless browser. Slower — launches a real browser per payload. | `False` |
| `--pdf` | Also export the report as PDF alongside the HTML report. | `False` |
| `--screenshot` | Capture and embed a PoC screenshot for each finding. Slower — launches a headless browser to revisit every finding. | `False` |

> **Hardening note on `--screenshot`:** the headless browser follows HTTP redirects with no destination restriction, same as any browser. A malicious or compromised target could redirect it to an internal address and have that page captured into your report. Review embedded screenshots before sharing a report externally.

## 📄 Reports

Each finding in the HTML report includes the vulnerable URL, the payload used, the response status, a **curl command** you can run directly to reproduce it, and (with `--screenshot`) a screenshot of the finding — ready to paste into a bug bounty write-up or pentest deliverable. With `--pdf`, the same findings are also exported as a PDF using a print-friendly per-finding layout.

## Disclaimer

This tool is intended for authorized security testing only. The author accepts no liability for misuse or damage caused by this tool. Always obtain explicit permission before testing any system you do not own.
