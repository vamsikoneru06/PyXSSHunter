import time
import random

def human_delay(min_delay: float = 0.8, max_delay: float = 3.5, stealth_level: str = "medium"):
    if stealth_level == "low":
        delay = random.uniform(0.1, 0.8)
    elif stealth_level == "high":
        delay = random.uniform(4.0, 12.0)
    else:
        delay = random.uniform(min_delay, max_delay)

    # Occasional longer pause (human thinking)
    if random.random() < 0.12:
        delay += random.uniform(5, 15)

    time.sleep(delay)