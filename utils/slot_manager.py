from database import appointments
from datetime import datetime, timedelta

WORK_START = 9
WORK_END = 18
SLOT_MINUTES = 30

def generate_slots():
    slots = []
    current = datetime.strptime("09:00", "%H:%M")
    end = datetime.strptime("18:00", "%H:%M")

    while current < end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=SLOT_MINUTES)

    return slots


def is_slot_available(date, time):
    existing = appointments.find_one({
        "date": date,
        "time": time,
        "status": "booked"
    })
    return existing is None


def get_next_available_slot(date):
    slots = generate_slots()

    for slot in slots:
        if is_slot_available(date, slot):
            return slot

    return None


def get_period_slot(date, period):
    slots = generate_slots()

    if period == "morning":
        slots = [s for s in slots if int(s.split(":")[0]) < 12]

    elif period == "afternoon":
        slots = [s for s in slots if 12 <= int(s.split(":")[0]) < 16]

    elif period == "evening":
        slots = [s for s in slots if int(s.split(":")[0]) >= 16]

    for slot in slots:
        if is_slot_available(date, slot):
            return slot

    return None