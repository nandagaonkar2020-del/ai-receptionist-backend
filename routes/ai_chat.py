from fastapi import APIRouter
from database import appointments
from datetime import datetime
import re

router = APIRouter()

conversation_state = {}

EXIT_WORDS = ["bye", "goodbye", "thank you", "thanks", "ok bye"]
GREET_WORDS = ["hi", "hello", "hey", "good morning", "good afternoon"]

# ---------------- VALIDATORS ----------------

def valid_name(name):
    name = name.strip()
    return len(name) > 2 and name.replace(" ", "").isalpha()

def valid_phone(phone):
    cleaned = re.sub(r"\s+", "", phone)
    if re.fullmatch(r"[0-9]{10}", cleaned):
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

def valid_time(time_text):
    time_text = time_text.lower()
    if "morning" in time_text:
        return "morning"
    elif "afternoon" in time_text:
        return "afternoon"
    elif "evening" in time_text:
        return "evening"
    return None


# ---------------- AI CHAT ----------------

@router.post("/ai-chat")
async def ai_chat(data: dict):
    user_message = data.get("message", "")
    session_id = data.get("session")

    user_message = user_message.lower()

    # Exit call
    if any(word in user_message for word in EXIT_WORDS):
        return {
            "reply": "Thank you for calling. Have a great day. Goodbye.",
            "end_call": True
        }

    # New session
    if session_id not in conversation_state:
        conversation_state[session_id] = {"step": 0}

    state = conversation_state[session_id]
    step = state["step"]

    # Greeting trigger
    if any(word in user_message for word in GREET_WORDS) and step == 0:
        state["step"] = 1
        return {"reply": "Hello, welcome to our dental clinic. May I know your name please?"}

    # STEP 0
    if step == 0:
        state["step"] = 1
        return {"reply": "Hello, welcome to our dental clinic. May I know your name please?"}

    # STEP 1 - Name
    elif step == 1:
        if not valid_name(user_message):
            return {"reply": "Sorry, I didn't get your name properly. Could you please repeat your name?"}

        state["name"] = user_message
        state["step"] = 2
        return {"reply": f"Nice to meet you {user_message}. Could you please tell me your phone number?"}

    # STEP 2 - Phone
    elif step == 2:
        phone_clean = valid_phone(user_message)

        if not phone_clean:
            return {"reply": "That doesn't look like a valid phone number. Please tell a 10 digit phone number."}

        state["phone"] = phone_clean
        state["step"] = 3
        return {"reply": "Thank you. What service would you like to book today?"}

    # STEP 3 - Service
    elif step == 3:
        if not valid_service(user_message):
            return {"reply": "Please tell me which treatment or service you need."}

        state["service"] = user_message
        state["step"] = 4
        return {"reply": "Sure. Which date would you prefer for the appointment?"}

    # STEP 4 - Date
    elif step == 4:
        date_valid = valid_date(user_message)

        if not date_valid:
            return {"reply": "Please tell a proper date like tomorrow, this Monday, or 25 March."}

        state["date"] = date_valid
        state["step"] = 5
        return {"reply": "What time do you prefer? Morning, afternoon or evening?"}

    # STEP 5 - Time
    elif step == 5:
        time_slot = valid_time(user_message)

        if not time_slot:
            return {"reply": "Please choose morning, afternoon, or evening."}

        state["time"] = time_slot
        state["step"] = 6

        return {
            "reply": f"Please confirm your appointment for {state['service']} on {state['date']} during {state['time']}. Should I book it?"
        }

    # STEP 6 - Confirm Booking
    elif step == 6:
        if "yes" in user_message or "confirm" in user_message or "book" in user_message:

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
                "reply": "Your appointment is successfully booked. Thank you for calling.",
                "end_call": True
            }
        else:
            state["step"] = 4
            return {"reply": "Okay, let's change the date. Which date would you prefer?"}