import requests
from urllib.parse import urlparse, parse_qs, urlencode, urljoin
from rich.console import Console
from rich.progress import Progress
from ..stealth.headers import get_random_headers
from ..stealth.delay import human_delay
from ..stealth.proxy import ProxyManager
from ..payloads.manager import PayloadManager
from .analyzer import analyze_response
from .crawler import find_forms
from .injector import submit_form, build_form_data
from ..config import DEFAULT_TIMEOUT, STEALTH_DELAYS
from ..utils.helpers import build_curl_command

console = Console()

class StealthScanner:
    def __init__(self, stealth_level: str = "medium", proxies: list = None, max_payloads: int = 50):
        self.stealth_level = stealth_level
        self.session = requests.Session()
        self.proxy_manager = ProxyManager(proxies)
        self.payload_manager = PayloadManager(max_payloads=max_payloads)
        self.min_delay, self.max_delay = STEALTH_DELAYS.get(stealth_level, STEALTH_DELAYS["medium"])
        self.total_attempts = 0
        self.failed_attempts = 0

    def scan(self, target_url: str):
        results = []
        payloads = self.payload_manager.get_payloads()

        console.print(f"[cyan]Testing {len(payloads)} payloads with {self.stealth_level} stealth...[/cyan]")

        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning...", total=len(payloads))

            for payload in payloads:
                self.total_attempts += 1
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
                                "type": "Reflected",
                                "url": test_url,
                                "payload": payload,
                                "status": resp.status_code,
                                "evidence": "Payload reflected without sanitization",
                                "curl_command": build_curl_command(test_url, headers)
                            })
                            console.print(f"[bold red]Potential XSS found![/bold red] -> {test_url}")

                except Exception as e:
                    self.failed_attempts += 1
                    console.print(f"[yellow]Request error: {str(e)[:100]}[/yellow]")

                progress.update(task, advance=1)

        return results

    def scan_stored(self, target_url: str):
        """Submit payloads to forms on the page and check whether they persist and
        reflect back unsanitized on a later page load (stored/persistent XSS)."""
        results = []

        self.total_attempts += 1
        try:
            resp = self.session.get(
                target_url, headers=get_random_headers(),
                proxies=self.proxy_manager.get_proxy(), timeout=DEFAULT_TIMEOUT
            )
        except Exception as e:
            self.failed_attempts += 1
            console.print(f"[red]Failed to fetch {target_url}: {str(e)[:100]}[/red]")
            return results

        forms = find_forms(resp.text, target_url)
        if not forms:
            console.print("[yellow]No forms found on page — nothing to test for stored XSS.[/yellow]")
            return results

        payloads = self.payload_manager.get_payloads()
        console.print(f"[cyan]Testing {len(forms)} form(s) with {len(payloads)} payloads for stored XSS...[/cyan]")

        with Progress() as progress:
            task = progress.add_task("[cyan]Testing forms...", total=len(forms) * len(payloads))

            for form in forms:
                for payload in payloads:
                    self.total_attempts += 1
                    try:
                        human_delay(self.min_delay, self.max_delay, self.stealth_level)
                        submit_headers = get_random_headers()
                        proxy = self.proxy_manager.get_proxy()

                        submit_form(self.session, form, payload, submit_headers, proxy, DEFAULT_TIMEOUT)

                        # Revisit the page on a separate request to check whether the
                        # payload persisted server-side, rather than just being echoed
                        # back in the immediate submission response.
                        human_delay(self.min_delay, self.max_delay, self.stealth_level)
                        verify_resp = self.session.get(
                            target_url, headers=get_random_headers(),
                            proxies=proxy, timeout=DEFAULT_TIMEOUT
                        )

                        if analyze_response(verify_resp, payload):
                            results.append({
                                "type": "Stored",
                                "url": target_url,
                                "payload": payload,
                                "status": verify_resp.status_code,
                                "evidence": f"Payload persisted after submission to {form['action']} and reflected on page reload",
                                "curl_command": build_curl_command(
                                    form["action"], submit_headers,
                                    method=form["method"].upper(),
                                    data=build_form_data(form, payload)
                                )
                            })
                            console.print(f"[bold red]Potential Stored XSS found![/bold red] -> {form['action']}")

                    except Exception as e:
                        self.failed_attempts += 1
                        console.print(f"[yellow]Request error: {str(e)[:100]}[/yellow]")

                    progress.update(task, advance=1)

        return results