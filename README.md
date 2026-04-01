# PyXSSHunter
A fast, modern Python CLI tool that automatically scans any website/URL for Cross-Site Scripting (XSS) vulnerabilities (Reflected, Stored, and DOM-based). It injects smart payloads, detects successful injections, and generates a professional HTML/PDF report with proof-of-concept screenshots or curl commands.
## Docker Usage (Recommended)

### Build the image
```bash
docker build -t pyxsshunter:latest -f docker/Dockerfile .