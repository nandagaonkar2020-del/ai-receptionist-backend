from fastapi import APIRouter
from database import appointments
from datetime import datetime
import re

from routes.slots import generate_slots
from utils.time_parser import normalize_time
from utils.validator import valid_name, valid_phone, valid_service
from utils.date_parser import parse_natural_date

router = APIRouter()

conversation_state = {}

EXIT_WORDS = ["bye", "goodbye", "thank you", "thanks", "ok bye"]

# ---------------- VALIDATORS ----------------

def valid_name(name):
    name = name.strip()
    return len(name) > 2 and name.replace(" ", "").isalpha()

def valid_phone(phone):
    cleaned = re.sub(r"\D", "", phone)
    if len(cleaned) == 10:
        return cleaned
    return None

def valid_service(service):
    return len(service.strip()) > 2

def valid_date(date_text):
    date_text = date_text.lower().strip()

    days = [
        "monday","tuesday","wednesday",
        "thursday","friday","saturday","sunday"
    ]

    if "tomorrow" in date_text:
        return date_text

    for d in days:
        if f"this {d}" in date_text:
            return date_text

    date_patterns = [
        r"\d{1,2}\s[a-zA-Z]+",
        r"\d{1,2}/\d{1,2}/\d{2,4}",
        r"\d{1,2}-\d{1,2}-\d{2,4}"
    ]

    for pattern in date_patterns:
        if re.fullmatch(pattern, date_text):
            return date_text

    return None

# ---------------- AI CHAT ----------------

@router.post("/ai-chat")
async def ai_chat(data: dict):
    user_message = data.get("message", "").lower()
    session_id = data.get("session")

    if any(word in user_message for word in EXIT_WORDS):
        return {"reply": "Thank you for calling. Goodbye.", "end_call": True}

    if session_id not in conversation_state:
        conversation_state[session_id] = {"step": 0}

    state = conversation_state[session_id]
    step = state["step"]

    # STEP 0 - Greeting
    if step == 0:
        state["step"] = 1
        return {"reply": "Hello, welcome to our dental clinic. May I know your name please?"}

    # STEP 1 - Name
    elif step == 1:
        if not valid_name(user_message):
            return {"reply": "Please tell your name properly."}

        state["name"] = user_message
        state["step"] = 2
        return {"reply": f"Nice to meet you {user_message}. Please tell your phone number."}

    # STEP 2 - Phone
    elif step == 2:
        phone = valid_phone(user_message)
        if not phone:
            return {"reply": "Please tell a valid 10 digit phone number."}

        state["phone"] = phone
        state["step"] = 3
        return {"reply": "What service would you like to book?"}

    # STEP 3 - Service
    elif step == 3:
        if not valid_service(user_message):
            return {"reply": "Please tell the treatment name."}

        state["service"] = user_message
        state["step"] = 4
        return {"reply": "Which date would you prefer? You can say tomorrow or this Monday."}

    # STEP 4 - Date
    elif step == 4:
        date = valid_date(user_message)
        if not date:
            return {"reply": "Please tell a valid date."}

        state["date"] = date
        state["step"] = 5
        return {"reply": "Do you prefer morning, afternoon or evening?"}

    # STEP 5 - Session time
    elif step == 5:
        if user_message not in ["morning", "afternoon", "evening"]:
            return {"reply": "Please say morning, afternoon or evening."}

        state["session_time"] = user_message
        slots = generate_slots(user_message)
        state["slots"] = slots
        state["step"] = 6

        slot_text = ", ".join(slots[:5])
        return {"reply": f"Available time slots are {slot_text}. Please choose a time."}

    # STEP 6 - Slot selection
    elif step == 6:
        chosen_time = normalize_time(user_message)

        if chosen_time not in state["slots"]:
            return {"reply": "Please choose a valid slot from available options."}

        state["time"] = chosen_time

        appointments.insert_one({
            "name": state["name"],
            "phone": state["phone"],
            "service": state["service"],
            "date": state["date"],
            "time": state["time"],
            "status": "booked",
            "created_at": datetime.now()
        })

        state["step"] = 0

        return {
            "reply": f"Your appointment is booked on {state['date']} at {state['time']}. Thank you.",
            "end_call": True
        }