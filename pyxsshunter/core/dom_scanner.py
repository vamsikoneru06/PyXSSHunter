from urllib.parse import urlparse, parse_qs
from rich.console import Console
from rich.progress import Progress
from playwright.sync_api import sync_playwright
from ..payloads.manager import PayloadManager
from ..stealth.delay import human_delay
from ..config import STEALTH_DELAYS
from ..utils.helpers import build_curl_command

console = Console()

class DomXSSScanner:
    """Detects DOM-based XSS by actually executing the page in a headless browser and
    watching for the payload firing a JS dialog (alert/confirm/prompt), rather than just
    inspecting the raw HTTP response text like reflected/stored detection do."""

    def __init__(self, stealth_level: str = "medium", max_payloads: int = 50):
        self.stealth_level = stealth_level
        self.min_delay, self.max_delay = STEALTH_DELAYS.get(stealth_level, STEALTH_DELAYS["medium"])
        self.payload_manager = PayloadManager(max_payloads=max_payloads)

    def _build_injection_urls(self, target_url: str, payloads: list) -> list:
        parsed = urlparse(target_url)
        params = parse_qs(parsed.query)
        keys = list(params.keys()) or ["q"]

        injections = []
        for payload in payloads:
            # Common DOM XSS sources: location.hash and location.search
            injections.append((f"{target_url}#{payload}", payload))
            for key in keys:
                sep = "&" if "?" in target_url else "?"
                injections.append((f"{target_url}{sep}{key}={payload}", payload))
        return injections

    def scan(self, target_url: str):
        results = []
        payloads = self.payload_manager.get_payloads()
        injections = self._build_injection_urls(target_url, payloads)

        console.print(f"[cyan]Testing {len(injections)} DOM injection points with headless browser...[/cyan]")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()

            with Progress() as progress:
                task = progress.add_task("[cyan]Rendering...", total=len(injections))

                for test_url, payload in injections:
                    triggered = {"fired": False}

                    def on_dialog(dialog, triggered=triggered):
                        triggered["fired"] = True
                        dialog.dismiss()

                    page = browser.new_page()
                    page.on("dialog", on_dialog)

                    try:
                        human_delay(self.min_delay, self.max_delay, self.stealth_level)
                        page.goto(test_url, timeout=10000, wait_until="load")
                        page.wait_for_timeout(500)

                        if triggered["fired"]:
                            results.append({
                                "type": "DOM-based",
                                "url": test_url,
                                "payload": payload,
                                "status": 200,
                                "evidence": "Payload executed client-side (JS dialog triggered) after page load",
                                "curl_command": build_curl_command(test_url, {"User-Agent": "Mozilla/5.0"})
                            })
                            console.print(f"[bold red]Potential DOM-based XSS found![/bold red] -> {test_url}")

                    except Exception as e:
                        console.print(f"[yellow]Render error: {str(e)[:100]}[/yellow]")
                    finally:
                        page.close()
                        progress.update(task, advance=1)

            browser.close()

        return results
