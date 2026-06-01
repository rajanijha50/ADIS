# ____FASTAPI MAIN ENTRY POINT____

from config.config import CLIENT_URL
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth.auth_microsoft import router as microsoft_router
from api.auth.auth_google import router as google_router
from api.auth.auth_email import router as email_router
from api.voice.main import router as voice_router
from api.text.main import router as text_router
from api.user.main import router as user_router
from api.session.main import router as session_router

app = FastAPI()
app.include_router(microsoft_router)
app.include_router(google_router)
app.include_router(email_router)
app.include_router(voice_router)
app.include_router(text_router)
app.include_router(user_router)
app.include_router(session_router)

origins = [
    CLIENT_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def homepage():
    return {"message": "you are on home page!"}
