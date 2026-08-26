SKIP_FIELD_TYPES = {"button", "reset", "file", "image"}

def build_form_data(form: dict, payload: str) -> dict:
    """Fill a form's fields with a payload, preserving hidden/checkbox/radio defaults.

    Includes the first submit button's name/value, mimicking a real submit click —
    servers commonly branch on which submit button was pressed (e.g. isset($_POST['btnSign']))
    and silently ignore the request if it's missing entirely.
    """
    data = {}
    submit_included = False
    for field in form["inputs"]:
        if field["type"] in SKIP_FIELD_TYPES:
            continue
        if field["type"] == "submit":
            if not submit_included:
                data[field["name"]] = field["value"] or field["name"]
                submit_included = True
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
