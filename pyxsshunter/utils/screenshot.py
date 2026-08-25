import base64
from playwright.sync_api import sync_playwright

class ScreenshotCapturer:
    """Reuses a single headless browser instance to capture PoC screenshots for multiple findings.

    Hardening note: capture() follows redirects with no destination restriction, same as any
    browser. A malicious/compromised target could redirect the headless browser to an internal
    address and have that page's content captured and embedded in the report. Review screenshots
    before sharing a report externally; if this matters for your use case, restrict navigation to
    the target's origin or block redirects into private IP ranges before calling page.goto().
    """

    def __enter__(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._browser.close()
        self._playwright.stop()

    def capture(self, url: str, timeout_ms: int = 15000) -> str:
        """Load url and return a base64-encoded PNG screenshot, or None on failure"""
        page = self._browser.new_page()
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
