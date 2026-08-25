import shlex
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def build_curl_command(url: str, headers: dict, method: str = "GET", data: dict = None) -> str:
    """Build an equivalent curl command for a request, for PoC/report purposes"""
    parts = ["curl", "-i", "-X", method, shlex.quote(url)]
    for key, value in headers.items():
        parts.append("-H")
        parts.append(shlex.quote(f"{key}: {value}"))
    if data:
        for key, value in data.items():
            parts.append("-d")
            parts.append(shlex.quote(f"{key}={value}"))
    return " ".join(parts)