import typer
from typing import List
from datetime import datetime
from urllib.parse import urlparse
from rich.console import Console
from pathlib import Path
from .core.scanner import StealthScanner
from .core.dom_scanner import DomXSSScanner
from .reporting.reporter import generate_html_report, save_report
from .reporting.pdf import save_pdf_report
from .utils.screenshot import ScreenshotCapturer
from .utils.helpers import parse_cookie_string, parse_header_list

console = Console()
app = typer.Typer(help="PyXSSHunter - Stealthy XSS Scanner")

DISCLAIMER = (
    "[bold yellow]PyXSSHunter must only be used against systems you own or have explicit, "
    "written authorization to test. Unauthorized scanning may violate the Computer Fraud and "
    "Abuse Act (CFAA) or equivalent laws in your jurisdiction. The author accepts no liability "
    "for misuse.[/bold yellow]"
)

@app.command()
def scan(
        url: str = typer.Option(..., "--url", "-u", help="Target URL to scan"),
        stealth_level: str = typer.Option("medium", "--stealth-level", help="Stealth level: low/medium/high"),
        proxies: str = typer.Option(None, "--proxies", help="Path to proxies.txt file"),
        max_payloads: int = typer.Option(50, "--max-payloads", help="Max payloads to test"),
        output: str = typer.Option("reports", "--output", "-o", help="Directory to save reports"),
        report_name: str = typer.Option(None, "--report-name", help="Custom report filename (without extension)"),
        i_have_permission: bool = typer.Option(
            False, "--i-have-permission",
            help="Confirm you own or are explicitly authorized to test the target URL. Required to run a scan."
        ),
        stored: bool = typer.Option(
            False, "--stored",
            help="Also test for stored XSS by submitting payloads to forms found on the page. "
                 "This WRITES data to the target (e.g. comments, guestbook entries) - only use "
                 "on targets where persisting test data is acceptable."
        ),
        dom: bool = typer.Option(
            False, "--dom",
            help="Also test for DOM-based XSS by rendering injection points (URL hash/query params) "
                 "in a headless browser and watching for JS execution. Slower - launches a real browser."
        ),
        pdf: bool = typer.Option(
            False, "--pdf",
            help="Also export the report as PDF alongside the HTML report."
        ),
        screenshot: bool = typer.Option(
            False, "--screenshot",
            help="Capture a PoC screenshot for each finding and embed it in the report. "
                 "Slower - launches a headless browser to revisit every finding."
        ),
        cookie: str = typer.Option(
            None, "--cookie",
            help="Cookie header to send with every request, e.g. 'PHPSESSID=abc123; security=low'. "
                 "Needed to scan pages behind a login."
        ),
        header: List[str] = typer.Option(
            [], "--header", "-H",
            help="Custom header to send with every request, e.g. 'Authorization: Bearer xyz'. "
                 "Can be repeated."
        ),
):
    console.print(DISCLAIMER)

    if not i_have_permission:
        console.print(
            "[bold red]Refusing to scan: pass --i-have-permission to confirm you are "
            "authorized to test this target.[/bold red]"
        )
        raise typer.Exit(code=1)

    if stored:
        console.print(
            "[bold yellow]--stored is enabled: this will submit payloads to any forms found "
            "on the page, which may persist data (comments, entries, etc.) on the target.[/bold yellow]"
        )

    console.print(f"[bold cyan]Starting PyXSSHunter scan on {url}[/bold cyan]")
    console.print(f"[yellow]Stealth Level: {stealth_level.upper()}[/yellow]")

    # Ensure output directory exists
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    proxy_list = []
    if proxies:
        try:
            with open(proxies, "r") as f:
                proxy_list = [line.strip() for line in f if line.strip()]
        except Exception as e:
            console.print(f"[red]Failed to load proxies: {e}[/red]")

    cookies = parse_cookie_string(cookie)
    extra_headers = parse_header_list(header)

    scanner = StealthScanner(
        stealth_level=stealth_level,
        proxies=proxy_list,
        max_payloads=max_payloads,
        extra_headers=extra_headers,
        cookies=cookies
    )

    results = scanner.scan(url)

    if stored:
        results += scanner.scan_stored(url)

    dom_scanner = None
    if dom:
        dom_scanner = DomXSSScanner(
            stealth_level=stealth_level, max_payloads=max_payloads,
            extra_headers=extra_headers, cookies=cookies
        )
        results += dom_scanner.scan(url)

    total_attempts = scanner.total_attempts + (dom_scanner.total_attempts if dom_scanner else 0)
    failed_attempts = scanner.failed_attempts + (dom_scanner.failed_attempts if dom_scanner else 0)

    if total_attempts:
        console.print(f"[cyan]{total_attempts - failed_attempts}/{total_attempts} requests succeeded ({failed_attempts} failed).[/cyan]")
        if failed_attempts == total_attempts:
            console.print(
                "[bold red]Every request failed - this target was likely unreachable. "
                "'No vulnerabilities found' below does not mean the target is safe; "
                "check connectivity before trusting this result.[/bold red]"
            )

    console.print(f"[green]Scan completed! Found {len(results)} potential vulnerabilities.[/green]")

    if not results:
        console.print("[yellow]No vulnerabilities found. No report generated.[/yellow]")
        return

    if screenshot:
        console.print("[cyan]Capturing PoC screenshots...[/cyan]")
        with ScreenshotCapturer(extra_headers=extra_headers, cookies=cookies) as capturer:
            for r in results:
                shot = capturer.capture(r["url"])
                if shot:
                    r["screenshot_b64"] = shot

    # Generate and save report
    html_content = generate_html_report(results, url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = report_name or f"xss_report_{urlparse(url).netloc}"

    filename = save_report(html_content, output_dir, base_name, timestamp=timestamp)
    console.print(f"[bold green]Report saved to: {filename}[/bold green]")

    if pdf:
        pdf_filename = save_pdf_report(results, url, output_dir, base_name, timestamp=timestamp)
        console.print(f"[bold green]PDF report saved to: {pdf_filename}[/bold green]")

if __name__ == "__main__":
    app()
