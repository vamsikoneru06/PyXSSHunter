import base64
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

class ScreenshotCapturer:
    """Reuses a single headless browser instance to capture PoC screenshots for multiple findings.

    Hardening note: capture() follows redirects with no destination restriction, same as any
    browser. A malicious/compromised target could redirect the headless browser to an internal
    address and have that page's content captured and embedded in the report. Review screenshots
    before sharing a report externally; if this matters for your use case, restrict navigation to
    the target's origin or block redirects into private IP ranges before calling page.goto().
    """

    def __init__(self, extra_headers: dict = None, cookies: dict = None):
        self.extra_headers = extra_headers or {}
        self.cookies = cookies or {}

    def __enter__(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch()
        self._context = self._browser.new_context(extra_http_headers=self.extra_headers)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._browser.close()
        self._playwright.stop()

    def capture(self, url: str, timeout_ms: int = 15000) -> str:
        """Load url and return a base64-encoded PNG screenshot, or None on failure"""
        if self.cookies:
            domain = urlparse(url).hostname
            self._context.add_cookies([
                {"name": name, "value": value, "domain": domain, "path": "/"}
                for name, value in self.cookies.items()
            ])
        page = self._context.new_page()
        try:
            page.on("dialog", lambda dialog: dialog.dismiss())
            page.goto(url, timeout=timeout_ms, wait_until="load")
            page.wait_for_timeout(500)
            png_bytes = page.screenshot()
            return base64.b64encode(png_bytes).decode("ascii")
        except Exception:
            return None
        finally:
            page.close()
