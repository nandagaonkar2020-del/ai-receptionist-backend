from fastapi import APIRouter
from database import appointments, patients
from utils.slot_checker import is_slot_available
from utils.date_parser import parse_date
from utils.time_parser import parse_time
from datetime import datetime

router = APIRouter()

conversation_state = {}

@router.post("/ai-chat")
async def ai_chat(data: dict):
    user_message = data.get("message")
    session_id = data.get("session")

    if session_id not in conversation_state:
        conversation_state[session_id] = {"step": 0}

    step = conversation_state[session_id]["step"]

    if step == 0:
        conversation_state[session_id]["step"] = 1
        return {"reply": "Welcome to dental clinic. What is your name?"}

    elif step == 1:
        conversation_state[session_id]["name"] = user_message
        conversation_state[session_id]["step"] = 2
        return {"reply": "Please tell me your phone number."}

    elif step == 2:
        conversation_state[session_id]["phone"] = user_message
        conversation_state[session_id]["step"] = 3
        return {"reply": "What service do you need? Cleaning, filling, whitening?"}

    elif step == 3:
        conversation_state[session_id]["service"] = user_message
        conversation_state[session_id]["step"] = 4
        return {"reply": "Which date do you want appointment?"}

    elif step == 4:
        date = parse_date(user_message)
        conversation_state[session_id]["date"] = date
        conversation_state[session_id]["step"] = 5
        return {"reply": "What time do you prefer?"}

    elif step == 5:
        time = parse_time(user_message)

        name = conversation_state[session_id]["name"]
        phone = conversation_state[session_id]["phone"]
        service = conversation_state[session_id]["service"]
        date = conversation_state[session_id]["date"]

        if not is_slot_available(date, time):
            return {"reply": "This time slot is not available. Please choose another time."}

        patients.insert_one({
            "name": name,
            "phone": phone
        })

        appointments.insert_one({
            "name": name,
            "phone": phone,
            "service": service,
            "date": date,
            "time": time,
            "status": "booked",
            "created_at": datetime.now()
        })

        conversation_state[session_id]["step"] = 0

        return {"reply": f"Your appointment is booked on {date} at {time}. Thank you."}