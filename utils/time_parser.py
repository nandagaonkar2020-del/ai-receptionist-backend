from datetime import datetime

def parse_time(text):
    try:
        return datetime.strptime(text, "%I %p").strftime("%H:%M")
    except:
        return text