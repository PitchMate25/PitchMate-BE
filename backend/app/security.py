from datetime import datetime, timedelta, timezone
from os import getenv
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends, Request

SECRET_KEY = getenv("SECRET_KEY", "dev")
ALGO = "HS256"
EXPIRE_MIN = int(getenv("JWT_EXPIRE_MINUTES", "60"))

def create_jwt(payload: dict) -> str:
    to_encode = payload.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGO)

def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user_claims(request: Request) -> dict:
    token = request.cookies.get("access_token")  # HttpOnly 쿠키에서 읽기
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return verify_jwt(token)