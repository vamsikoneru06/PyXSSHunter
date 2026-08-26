import shlex
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def parse_cookie_string(cookie_str: str) -> dict:
    """Parse a 'k1=v1; k2=v2' Cookie header string into a dict"""
    cookies = {}
    if not cookie_str:
        return cookies
    for part in cookie_str.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        cookies[key.strip()] = value.strip()
    return cookies

def parse_header_list(headers: list) -> dict:
    """Parse a list of 'Name: Value' strings into a dict"""
    parsed = {}
    for h in headers or []:
        if ":" not in h:
            continue
        key, value = h.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed

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