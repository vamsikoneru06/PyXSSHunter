def analyze_response(response, payload: str) -> bool:
    """Basic detection logic — improve this significantly in production"""
    text = response.text.lower()
    payload_lower = payload.lower()

    # Simple checks
    if payload_lower in text and "<script>" in payload_lower:
        return True
    if "alert(" in payload_lower and "alert(" in text:
        return True
    if response.status_code == 200 and payload_lower in text:
        return True  # Reflected

    return False