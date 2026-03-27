from fastapi import FastAPI
from routes.ai_chat import router as ai_router
from routes.calendar import router as calendar_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_router)
app.include_router(calendar_router)

@app.get("/")
def home():
    return {"message": "AI Receptionist Running"}