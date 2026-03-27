from fastapi import APIRouter
import openai
import os
from dotenv import load_dotenv
from database import appointments, patients

load_dotenv()

router = APIRouter()

openai.api_key = os.getenv("OPENAI_API_KEY")

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
        return {"reply": "Hello, welcome to dental clinic. What is your name?"}

    elif step == 1:
        conversation_state[session_id]["name"] = user_message
        conversation_state[session_id]["step"] = 2
        return {"reply": "Please tell me your phone number."}

    elif step == 2:
        conversation_state[session_id]["phone"] = user_message
        conversation_state[session_id]["step"] = 3
        return {"reply": "What date do you want appointment?"}

    elif step == 3:
        conversation_state[session_id]["date"] = user_message
        conversation_state[session_id]["step"] = 4
        return {"reply": "What time do you prefer?"}

    elif step == 4:
        name = conversation_state[session_id]["name"]
        phone = conversation_state[session_id]["phone"]
        date = conversation_state[session_id]["date"]
        time = user_message

        patients.insert_one({
            "name": name,
            "phone": phone
        })

        appointments.insert_one({
            "name": name,
            "phone": phone,
            "date": date,
            "time": time
        })

        conversation_state[session_id]["step"] = 0

        return {"reply": "Your appointment is booked. Thank you."}