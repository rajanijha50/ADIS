from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import httpx
import base64
from api.auth.auth_utils import create_jwt, set_auth_cookie
from db.sqliteDB import create_user, get_connection
from db.mongoDB import UserModel
from db.utils import now


router = APIRouter()

USER_INFO_URL = "https://graph.microsoft.com/v1.0/me"
PHOTO_URL = "https://graph.microsoft.com/v1.0/me/photo/$value"

class MicrosoftTokenRequest(BaseModel):
    access_token: str

@router.post("/api/auth/microsoft/login")
async def microsoft_login(body: MicrosoftTokenRequest, response: Response):
    access_token = body.access_token

    # validate the access token and fetch user profile from Microsoft Graph API
    async with httpx.AsyncClient() as client:
        profile_response = await client.get(
            USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # attempt to fetch profile photo, but don't fail if it doesn't work (some accounts may not have a photo)
        photo_response = await client.get(
            PHOTO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if profile_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user profile from Microsoft")

    profile   = profile_response.json()
    ms_id     = profile.get("id")
    email     = profile.get("mail") or profile.get("userPrincipalName")
    full_name = profile.get("displayName", "")
    
    # Process profile picture if available
    profile_pic = None
    if photo_response.status_code == 200:
        encoded_string = base64.b64encode(photo_response.content).decode("utf-8")
        mime_type = photo_response.headers.get("Content-Type", "image/jpeg")
        profile_pic = f"data:{mime_type};base64,{encoded_string}"
    
    # print("success microsoft login ✅✅: ", {full_name, email, profile_pic})

    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from Microsoft")

    try:
        user = UserModel.find_one({"email": email})
        if not user:
            # new user, insert into mongoDB
            result = UserModel.insert_one({
                "name": full_name,
                "email": email,
                "profile_pic": profile_pic,
                "created_at": now(),
                "updated_at": now()
            })
            user_id = str(result.inserted_id)

            # add into sqliteDB
            conn = get_connection()
            create_user(conn, full_name, email)
        else:
            user_id = str(user["_id"])
    except Exception as e:
        print("Error in microsoft login: ", e)
        raise HTTPException(status_code=500, detail="Database error")
    
    jwt_token = create_jwt(user_id=user_id, email=email)
    set_auth_cookie(response, jwt_token)

    return {
        "user": {"email": email, "full_name": full_name, "profile_pic": profile_pic},
        "token": jwt_token
    }
