import typer
from rich.console import Console
from pathlib import Path
from .core.scanner import StealthScanner
from .reporting.reporter import generate_html_report, save_report

console = Console()
app = typer.Typer(help="PyXSSHunter - Stealthy XSS Scanner")

@app.command()
def scan(
        url: str = typer.Option(..., "--url", "-u", help="Target URL to scan"),
        stealth_level: str = typer.Option("medium", "--stealth-level", help="Stealth level: low/medium/high"),
        proxies: str = typer.Option(None, "--proxies", help="Path to proxies.txt file"),
        max_payloads: int = typer.Option(50, "--max-payloads", help="Max payloads to test"),
        output: str = typer.Option("reports", "--output", "-o", help="Directory to save reports"),
        report_name: str = typer.Option(None, "--report-name", help="Custom report filename (without extension)"),
):
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

    scanner = StealthScanner(
        stealth_level=stealth_level,
        proxies=proxy_list,
        max_payloads=max_payloads
    )

    results = scanner.scan(url)

    console.print(f"[green]Scan completed! Found {len(results)} potential vulnerabilities.[/green]")

    # Generate and save report
    if results:
        html_content = generate_html_report(results, url)
        filename = save_report(html_content, output_dir, report_name or f"xss_report_{urlparse(url).netloc}")
        console.print(f"[bold green]Report saved to: {filename}[/bold green]")
    else:
        console.print("[yellow]No vulnerabilities found. No report generated.[/yellow]")

if __name__ == "__main__":
    app()