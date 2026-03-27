from datetime import datetime, timedelta

def parse_date(text):
    text = text.lower()

    if "today" in text:
        return datetime.today().strftime("%Y-%m-%d")

    if "tomorrow" in text:
        return (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    return text