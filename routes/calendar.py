from fastapi import APIRouter
from database import appointments

router = APIRouter()

@router.get("/calendar")
def get_calendar():
    data = list(appointments.find({}, {"_id": 0}))
    return data