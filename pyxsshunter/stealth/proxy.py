import random

class ProxyManager:
    def __init__(self, proxy_list: list = None):
        self.proxies = proxy_list or []

    def get_proxy(self) -> dict | None:
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {"http": proxy, "https": proxy}