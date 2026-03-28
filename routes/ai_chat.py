from fastapi import APIRouter
from database import appointments, patients
from datetime import datetime
import re

router = APIRouter()

conversation_state = {}

EXIT_WORDS = ["bye", "goodbye", "thank you", "thanks", "ok bye"]

# ---------------- VALIDATORS ----------------

def valid_name(name):
    return len(name) > 2 and name.replace(" ", "").isalpha()

def valid_phone(phone):
    return re.fullmatch(r"[0-9]{10}", phone)

def valid_time(time_text):
    time_text = time_text.lower()
    if "morning" in time_text:
        return "morning"
    elif "afternoon" in time_text:
        return "afternoon"
    elif "evening" in time_text:
        return "evening"
    return None

def valid_date(text):
    invalid_words = ["decide", "later", "not sure", "dont know"]
    for w in invalid_words:
        if w in text:
            return False
    return True

# ---------------- MAIN AI CHAT ----------------

@router.post("/ai-chat")
async def ai_chat(data: dict):
    user_message = data.get("message").lower()
    session_id = data.get("session")

    # Exit call
    if any(word in user_message for word in EXIT_WORDS):
        return {
            "reply": "Thank you for calling. Have a great day. Goodbye.",
            "end_call": True
        }

    # Create session
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
            return {"reply": "Sorry, I didn't get your name properly. Could you please repeat your name?"}

        state["name"] = user_message
        state["step"] = 2
        return {"reply": f"Nice to meet you {user_message}. Could you please tell me your phone number?"}

    # STEP 2 - Phone
    elif step == 2:
        if not valid_phone(user_message):
            return {"reply": "That doesn't look like a valid phone number. Please tell a 10 digit phone number."}

        state["phone"] = user_message
        state["step"] = 3
        return {"reply": "Thank you. What service would you like to book today?"}

    # STEP 3 - Service
    elif step == 3:
        if len(user_message) < 3:
            return {"reply": "Please tell me which treatment or service you need."}

        state["service"] = user_message
        state["step"] = 4
        return {"reply": "Sure. Which date would you prefer for the appointment?"}

    # STEP 4 - Date
    elif step == 4:
        if not valid_date(user_message):
            return {"reply": "Please tell a proper date like tomorrow or 25 March."}

        state["date"] = user_message
        state["step"] = 5
        return {"reply": "What time do you prefer? Morning, afternoon or evening?"}

    # STEP 5 - Time + BOOKING
    elif step == 5:
        time_slot = valid_time(user_message)

        if not time_slot:
            return {"reply": "Please choose morning, afternoon, or evening."}

        state["time"] = time_slot

        # Save appointment
        appointments.insert_one({
            "name": state["name"],
            "phone": state["phone"],
            "service": state["service"],
            "date": state["date"],
            "time": state["time"],
            "status": "booked",
            "created_at": datetime.now()
        })

        # Reset conversation
        state["step"] = 0

        return {
            "reply": f"Your appointment is successfully booked on {state['date']} during {state['time']}. We look forward to seeing you. Thank you.",
            "end_call": True
        }