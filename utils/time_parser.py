import re
from datetime import datetime

def normalize_time(text):
    text = text.lower().strip()

    text = text.replace(".", "")
    text = text.replace(" ", "")

    try:
        if "am" in text or "pm" in text:
            return datetime.strptime(text, "%I%p").strftime("%I:00 %p")
    except:
        pass

    try:
        return datetime.strptime(text, "%I:%M%p").strftime("%I:%M %p")
    except:
        pass

    return text