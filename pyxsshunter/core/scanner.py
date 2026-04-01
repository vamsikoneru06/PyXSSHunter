import requests
from urllib.parse import urlparse, parse_qs, urlencode, urljoin
from rich.console import Console
from rich.progress import Progress
from ..stealth.headers import get_random_headers
from ..stealth.delay import human_delay
from ..stealth.proxy import ProxyManager
from ..payloads.manager import PayloadManager
from .analyzer import analyze_response
from ..config import DEFAULT_TIMEOUT, STEALTH_DELAYS

console = Console()

class StealthScanner:
    def __init__(self, stealth_level: str = "medium", proxies: list = None, max_payloads: int = 50):
        self.stealth_level = stealth_level
        self.session = requests.Session()
        self.proxy_manager = ProxyManager(proxies)
        self.payload_manager = PayloadManager(max_payloads=max_payloads)
        self.min_delay, self.max_delay = STEALTH_DELAYS.get(stealth_level, STEALTH_DELAYS["medium"])

    def scan(self, target_url: str):
        results = []
        payloads = self.payload_manager.get_payloads()

        console.print(f"[cyan]Testing {len(payloads)} payloads with {self.stealth_level} stealth...[/cyan]")

        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning...", total=len(payloads))

            for payload in payloads:
                try:
                    human_delay(self.min_delay, self.max_delay, self.stealth_level)
                    headers = get_random_headers()
                    proxy = self.proxy_manager.get_proxy()

                    # Simple reflected test: append payload to query params
                    parsed = urlparse(target_url)
                    params = parse_qs(parsed.query)
                    for key in list(params.keys()) or ["q"]:  # fallback param
                        test_url = target_url
                        if "?" in target_url:
                            test_url += f"&{key}={payload}" if params else f"?{key}={payload}"
                        else:
                            test_url += f"?{key}={payload}"

                        resp = self.session.get(
                            test_url,
                            headers=headers,
                            proxies=proxy,
                            timeout=DEFAULT_TIMEOUT,
                            allow_redirects=True
                        )

                        if analyze_response(resp, payload):
                            results.append({
                                "url": test_url,
                                "payload": payload,
                                "status": resp.status_code,
                                "evidence": "Payload reflected without sanitization"
                            })
                            console.print(f"[bold red]Potential XSS found![/bold red] → {test_url}")

                except Exception as e:
                    console.print(f"[yellow]Request error: {str(e)[:100]}[/yellow]")

                progress.update(task, advance=1)

        return results