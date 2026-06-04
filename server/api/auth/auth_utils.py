from datetime import datetime, timedelta
from jose import jwt, JWTError
from config.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES


def create_jwt(user_id: int, email: str) -> str:
    """Create a signed JWT for a user."""
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str) -> dict:
    """Verify a JWT and return its payload. Raises if invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")


def set_auth_cookie(response, token: str):
    """Set the auth_token cookie in the response."""
    from config.config import CLIENT_URL
    is_secure = False
    samesite_val = "lax"
    if CLIENT_URL and CLIENT_URL.startswith("https://"):
        is_secure = True
        samesite_val = "none"

    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        max_age=JWT_EXPIRE_MINUTES * 60,
        expires=JWT_EXPIRE_MINUTES * 60,
        samesite=samesite_val,
        secure=is_secure,
    )


def delete_auth_cookie(response):
    """Remove the auth_token cookie from the response."""
    from config.config import CLIENT_URL
    is_secure = False
    samesite_val = "lax"
    if CLIENT_URL and CLIENT_URL.startswith("https://"):
        is_secure = True
        samesite_val = "none"

    response.delete_cookie(
        key="auth_token",
        httponly=True,
        samesite=samesite_val,
        secure=is_secure,
    )


def get_token_from_cookie(request):
    """Extract the auth_token from the request cookies or Authorization header."""
    token = request.cookies.get("auth_token")
    if token:
        return token
    
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    
    return None