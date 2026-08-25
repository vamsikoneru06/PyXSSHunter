from bs4 import BeautifulSoup
from urllib.parse import urljoin

def find_forms(html: str, base_url: str) -> list:
    """Parse HTML and return submittable forms with their fields, for stored-XSS testing"""
    soup = BeautifulSoup(html, "html.parser")
    forms = []
    for form in soup.find_all("form"):
        action = form.get("action") or base_url
        method = (form.get("method") or "get").strip().lower()
        inputs = []
        for tag in form.find_all(["input", "textarea", "select"]):
            name = tag.get("name")
            if not name:
                continue
            field_type = tag.get("type", "text").lower() if tag.name == "input" else tag.name
            value = tag.get("value", "")
            inputs.append({"name": name, "type": field_type, "value": value})

        forms.append({
            "action": urljoin(base_url, action),
            "method": method if method in ("get", "post") else "get",
            "inputs": inputs,
        })
    return forms
