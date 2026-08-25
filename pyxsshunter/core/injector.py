SKIP_FIELD_TYPES = {"submit", "button", "reset", "file", "image"}

def build_form_data(form: dict, payload: str) -> dict:
    """Fill a form's fields with a payload, preserving hidden/checkbox/radio defaults"""
    data = {}
    for field in form["inputs"]:
        if field["type"] in SKIP_FIELD_TYPES:
            continue
        if field["type"] in ("checkbox", "radio"):
            data[field["name"]] = field["value"] or "on"
        elif field["type"] == "hidden":
            data[field["name"]] = field["value"]
        else:
            data[field["name"]] = payload
    return data

def submit_form(session, form: dict, payload: str, headers: dict, proxies, timeout: int):
    """Submit a discovered form with the payload injected into its text-like fields"""
    data = build_form_data(form, payload)
    if form["method"] == "post":
        return session.post(
            form["action"], data=data, headers=headers, proxies=proxies,
            timeout=timeout, allow_redirects=True
        )
    return session.get(
        form["action"], params=data, headers=headers, proxies=proxies,
        timeout=timeout, allow_redirects=True
    )
