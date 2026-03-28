import re
from datetime import datetime

def valid_name(name):
    return len(name) > 2 and name.isalpha()

def valid_phone(phone):
    return re.fullmatch(r"[0-9]{10}", phone)

def valid_service(service):
    return len(service) > 2

def valid_date(date_text):
    # simple check
    invalid_words = ["decide", "later", "not sure"]
    for w in invalid_words:
        if w in date_text:
            return False
    return True

def valid_time(time_text):
    allowed = ["morning", "afternoon", "evening"]
    for a in allowed:
        if a in time_text:
            return True
    return False