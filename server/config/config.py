# config.py
from dotenv import load_dotenv
import os

load_dotenv()

MAP_API_KEY = os.getenv("GMAP_DEMO_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

JWT_SECRET_KEY      = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM       = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES  = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
CLIENT_URL = os.getenv("CLIENT_URL")

# Chatbot API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")