from fastapi.routing import APIRouter
from pydantic import BaseModel
from db.mongoDB import UserModel
from db.sqliteDB import get_connection, get_user, get_user_preferences, upsert_user_preferences, update_user

router = APIRouter()

def helper(success: bool, message: str, data=None):
    return {
        "success": success,
        "message": message,
        "data": data
    }

class UserPreferences(BaseModel):
    email: str
    llm_provider: str
    llm_model: str
    api_key: str
    tone: str
    language: str
    max_tokens: int = 512
    temperature: float = 0.5
    system_prompt: str

class UserProfile(BaseModel):
    email: str
    name: str
    contact: str = None

@router.get("/api/user/profile/{email}")
async def get_user_profile(email: str):
    """Gets the user profile"""
    try:
        conn = get_connection()
        user = get_user(conn, email)
        return helper(True, "User profile retrieved successfully", user)
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return helper(False, "An error occurred while getting the user profile")

@router.get("/api/user/{email}/preferences")
async def get_preferences(email: str):
    """Gets the user preferences"""
    try:
        conn = get_connection()
        preferences = get_user_preferences(conn, email)
        return helper(True, "User preferences retrieved successfully", preferences)
    except Exception as e:
        print(f"Error getting user preferences: {e}")
        return helper(False, "An error occurred while getting user preferences")

@router.patch("/api/user/preferences")
async def save_preferences(preferences: UserPreferences):
    try:
        conn = get_connection()
        # Extract email directly from the Pydantic model
        email = preferences.email
        # Convert the model to a plain dict and remove email before passing
        pref_dict = preferences.dict()
        pref_dict.pop("email", None)
        upsert_user_preferences(
            conn,
            email,
            **pref_dict
        )
        return helper(True, "Preferences saved successfully")
    except Exception as e:
        print(f"Error saving user preferences: {e}")
        return helper(False, "An error occurred while saving user preferences")

@router.patch("/api/user/profile")
async def save_profile(profile: UserProfile):
    # update in mongoDB: don't update email as it's the unique identifier, only update name and contact
    try:
        existing_user = UserModel.find_one({"email": profile.email})
        if existing_user:
            UserModel.update_one({"email": profile.email}, {"$set": {"name": profile.name, "contact": profile.contact}})
            update_user(conn=get_connection(), email=profile.email, name=profile.name, contact=profile.contact)  # update in sqliteDB as well
            return helper(True, "Profile saved successfully")
        else:
            return helper(False, "User not found!")
    except Exception as e:
        print(f"Error saving profile: {e}")
        return helper(False, "An error occurred while saving the profile")