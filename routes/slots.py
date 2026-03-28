from datetime import datetime, timedelta

def generate_slots(session_time):
    slots = []

    if session_time == "morning":
        start = datetime.strptime("09:00", "%H:%M")
        end = datetime.strptime("12:30", "%H:%M")

    elif session_time == "afternoon":
        start = datetime.strptime("13:00", "%H:%M")
        end = datetime.strptime("16:30", "%H:%M")

    elif session_time == "evening":
        start = datetime.strptime("16:30", "%H:%M")
        end = datetime.strptime("18:30", "%H:%M")

    while start < end:
        slots.append(start.strftime("%I:%M %p"))
        start += timedelta(minutes=30)

    return slots