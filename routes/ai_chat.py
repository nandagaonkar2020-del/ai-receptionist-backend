from fastapi import APIRouter
from database import appointments, patients
from datetime import datetime

router = APIRouter()

conversation_state = {}

EXIT_WORDS = ["bye", "goodbye", "thank you", "thanks", "ok bye"]

@router.post("/ai-chat")
async def ai_chat(data: dict):
    user_message = data.get("message").lower()
    session_id = data.get("session")

    if any(word in user_message for word in EXIT_WORDS):
        return {"reply": "Thank you for calling. Have a great day. Goodbye.", "end_call": True}

    if session_id not in conversation_state:
        conversation_state[session_id] = {"step": 0}

    state = conversation_state[session_id]
    step = state["step"]

    # STEP 0
    if step == 0:
        state["step"] = 1
        return {"reply": "Hello, welcome to our dental clinic. May I know your name please?"}

    # STEP 1
    elif step == 1:
        state["name"] = user_message
        state["step"] = 2
        return {"reply": f"Nice to meet you {user_message}. Could you please tell me your phone number?"}

    # STEP 2
    elif step == 2:
        state["phone"] = user_message
        state["step"] = 3
        return {"reply": "Thank you. What service would you like to book today?"}

    # STEP 3
    elif step == 3:
        state["service"] = user_message
        state["step"] = 4
        return {"reply": "Sure. Which date would you prefer for the appointment?"}

    # STEP 4
    elif step == 4:
        state["date"] = user_message
        state["step"] = 5
        return {"reply": "What time do you prefer? Morning, afternoon or evening?"}

    # STEP 5
    elif step == 5:
        state["time"] = user_message

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
            "reply": f"Your appointment is successfully booked on {state['date']} during {state['time']}. We look forward to seeing you. Thank you.",
            "end_call": True
        }