from fastapi import APIRouter
from database import appointments
from datetime import datetime
import re
from utils.slots import generate_slots

router = APIRouter()

conversation_state = {}

EXIT_WORDS = ["bye", "goodbye", "thank you", "thanks", "ok bye"]
GREET_WORDS = ["hi", "hello", "hey", "good morning", "good afternoon"]

# ---------------- VALIDATORS ----------------

def valid_name(name):
    return len(name.strip()) > 2

def valid_phone(phone):
    cleaned = re.sub(r"\D", "", phone)
    if len(cleaned) >= 10:
        return cleaned[-10:]
    return None

def valid_service(service):
    return len(service.strip()) > 2

def valid_time(text):
    text = text.lower()
    if "morning" in text:
        return "morning"
    if "afternoon" in text:
        return "afternoon"
    if "evening" in text:
        return "evening"
    return None

# ---------------- SLOT LOGIC ----------------

def get_available_slots(date, session):
    all_slots = generate_slots(session)

    booked = appointments.find({
        "date": date,
        "session": session
    })

    booked_slots = [b["slot"] for b in booked]

    return [s for s in all_slots if s not in booked_slots]


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

    # Greeting
    if step == 0:
        state["step"] = 1
        return {"reply": "Hello, welcome to our dental clinic. May I know your name?"}

    # NAME
    elif step == 1:
        if not valid_name(user_message):
            return {"reply": "Please tell me your correct name."}

        state["name"] = user_message
        state["step"] = 2
        return {"reply": "Please tell me your phone number."}

    # PHONE
    elif step == 2:
        phone = valid_phone(user_message)
        if not phone:
            return {"reply": "Please tell a valid 10 digit phone number."}

        state["phone"] = phone
        state["step"] = 3
        return {"reply": "What service do you want to book?"}

    # SERVICE
    elif step == 3:
        state["service"] = user_message
        state["step"] = 4
        return {"reply": "Which date do you prefer?"}

    # DATE
    elif step == 4:
        state["date"] = user_message
        state["step"] = 5
        return {"reply": "Morning, afternoon or evening?"}

    # SESSION → SHOW SLOTS
    elif step == 5:
        session_time = valid_time(user_message)
        if not session_time:
            return {"reply": "Please choose morning, afternoon or evening."}

        state["session"] = session_time

        slots = get_available_slots(state["date"], session_time)

        if not slots:
            return {"reply": "No slots available. Please choose another session."}

        state["slots"] = slots
        state["step"] = 6

        return {"reply": f"Available slots are {', '.join(slots[:5])}. Which time do you want?"}

    # SELECT SLOT
    elif step == 6:
        if user_message not in state["slots"]:
            return {"reply": "Please choose a valid slot from available options."}

        state["slot"] = user_message
        state["step"] = 7

        return {"reply": f"Confirm appointment on {state['date']} at {state['slot']}?"}

    # CONFIRM
    elif step == 7:
        if "yes" in user_message or "confirm" in user_message:

            appointments.insert_one({
                "name": state["name"],
                "phone": state["phone"],
                "service": state["service"],
                "date": state["date"],
                "session": state["session"],
                "slot": state["slot"],
                "status": "booked",
                "created_at": datetime.now()
            })

            state["step"] = 0

            return {
                "reply": f"Your appointment is booked at {state['slot']}. Thank you.",
                "end_call": True
            }

        else:
            state["step"] = 5
            return {"reply": "Okay, choose another time session."}