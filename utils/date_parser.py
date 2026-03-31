from datetime import datetime, timedelta

def parse_natural_date(text):
    text = text.lower().strip()

    today = datetime.today()

    days_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    if text == "today":
        return today.strftime("%Y-%m-%d")

    if text == "tomorrow":
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    if text.startswith("this "):
        day_name = text.split("this ")[1]
        if day_name in days_map:
            today_weekday = today.weekday()
            target_day = days_map[day_name]
            days_ahead = target_day - today_weekday
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # try exact date
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except:
        return None