from database import appointments

def is_slot_available(date, time):
    existing = appointments.find_one({
        "date": date,
        "time": time,
        "status": "booked"
    })

    return existing is None