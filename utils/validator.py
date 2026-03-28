import re
from datetime import datetime

# -------- NAME --------
def valid_name(name):
    name = name.strip()
    return len(name) > 2 and name.replace(" ", "").isalpha()


# -------- PHONE --------
def valid_phone(phone):
    # Remove spaces
    cleaned = re.sub(r"\s+", "", phone)

    # Check 10 digits
    if re.fullmatch(r"[0-9]{10}", cleaned):
        return cleaned   # return cleaned number
    return None


# -------- SERVICE --------
def valid_service(service):
    return len(service.strip()) > 2


# -------- DATE --------
def valid_date(date_text):
    date_text = date_text.lower().strip()

    days = [
        "monday","tuesday","wednesday",
        "thursday","friday","saturday","sunday"
    ]

    # Allow: tomorrow
    if "tomorrow" in date_text:
        return date_text

    # Allow: this monday, this tuesday...
    for d in days:
        if f"this {d}" in date_text:
            return date_text

    # Allow formats like 25 March or 25/03/2026
    date_patterns = [
        r"\d{1,2}\s[a-zA-Z]+",
        r"\d{1,2}/\d{1,2}/\d{2,4}",
        r"\d{1,2}-\d{1,2}-\d{2,4}"
    ]

    for pattern in date_patterns:
        if re.fullmatch(pattern, date_text):
            return date_text

    return None


# -------- TIME --------
def valid_time(time_text):
    time_text = time_text.lower()

    if "morning" in time_text:
        return "morning"
    elif "afternoon" in time_text:
        return "afternoon"
    elif "evening" in time_text:
        return "evening"

    return None