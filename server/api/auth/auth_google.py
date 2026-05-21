# auth_google.py
from models.User import UserModel
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import httpx

from api.auth.auth_utils import create_jwt, set_auth_cookie
from db.connect import get_connection, now

router = APIRouter()

class GoogleTokenRequest(BaseModel):
    token: str

@router.post("/api/auth/google/login")
async def google_login(body: GoogleTokenRequest, response: Response):
    token = body.token
    
    # Verify token with Google
    async with httpx.AsyncClient() as client:
        response_google = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
        
    if response_google.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google token")
        
    user_info = response_google.json()
    profile_pic = user_info.get("picture")
    email = user_info.get("email")
    google_id = user_info.get("sub")
    full_name = user_info.get("name", "")

    # print("success google login ✅✅: ", full_name, email, google_id, profile_pic)
    
    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from Google")
        
    # DB CONNECTION
    try:
        user = UserModel.find_one({"email": email})
        if not user:
            result = UserModel.insert_one({
                "name": full_name,
                "email": email,
                "profile_pic": profile_pic,
                "created_at": now(),
                "updated_at": now()
            })
            user_id = str(result.inserted_id)
        else:
            user_id = str(user["_id"])
    except Exception as e:
        print("Error in google login: ", e)
        raise HTTPException(status_code=500, detail="Database error")
    
    jwt_token = create_jwt(user_id=user_id, email=email)
    set_auth_cookie(response, jwt_token)
    
    return {
        "user": {"email": email, "full_name": full_name, "profile_pic": profile_pic},
        "token": jwt_token
    }
