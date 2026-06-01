from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
from bson import ObjectId
from api.auth.auth_utils import create_jwt, set_auth_cookie, verify_jwt, get_token_from_cookie
from db.sqliteDB import create_user, get_connection
from db.mongoDB import UserModel
from db.utils import hash_password, now


router = APIRouter()

@router.get("/api/auth/me")
def get_me(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated, no token found")
    
    try:
        payload = verify_jwt(token)
        user_id = payload.get("sub")
        user = UserModel.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "email": user.get("email"),
            "full_name": user.get("name"),
            "profile_pic": user.get("profile_pic")
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

class EmailSignupRequest(BaseModel):
    full_name: str
    email: str
    password: str

class EmailLoginRequest(BaseModel):
    email: str
    password: str

@router.post("/api/auth/email/signup")
def signup(body: EmailSignupRequest, response: Response):
    existingUser = UserModel.find_one({"email": body.email})
    if existingUser:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    pwd_hash = hash_password(body.password)
    
    # add into mongoDB
    result = UserModel.insert_one({
        "name": body.full_name,
        "email": body.email,
        "password": pwd_hash,
        "created_at": now(),
        "updated_at": now()
    })

    # add into sqliteDB
    conn = get_connection()
    create_user(conn, body.full_name, body.email)
    
    user_id = str(result.inserted_id)
    
    jwt_token = create_jwt(user_id=user_id, email=body.email)
    set_auth_cookie(response, jwt_token)
    return {
        "message": "Signup successful",
        "user": {"email": body.email, "full_name": body.full_name, "profile_pic": None},
        "token": jwt_token
    }

@router.post("/api/auth/email/login")
def login(body: EmailLoginRequest, response: Response):
    user = UserModel.find_one({"email": body.email})
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    stored_hash = user.get('password')
    if not stored_hash or hash_password(body.password) != stored_hash:
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    jwt_token = create_jwt(user_id=str(user['_id']), email=body.email)
    set_auth_cookie(response, jwt_token)
    return {
        "message": "Login successful",
        "user": {"email": user.get("email"), "full_name": user.get("name"), "profile_pic": user.get("profile_pic")},
        "token": jwt_token
    }

@router.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(key="auth_token")
    return {"message": "Logged out"}

class SetTokenRequest(BaseModel):
    token: str

@router.post("/api/auth/set-token")
def set_token(body: SetTokenRequest, response: Response):
    try:
        verify_jwt(body.token)
        set_auth_cookie(response, body.token)
        return {"message": "Cookie set successfully"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
