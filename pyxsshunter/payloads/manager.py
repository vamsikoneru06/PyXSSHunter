import random
from .base_payloads import BASE_PAYLOADS
from .evasion import EVASION

class PayloadManager:
    def __init__(self, max_payloads: int = 50):
        self.max_payloads = max_payloads

    def get_payloads(self):
        all_payloads = BASE_PAYLOADS + EVASION
        random.shuffle(all_payloads)
        return all_payloads[:self.max_payloads]