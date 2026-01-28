from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import JWT_SECRET, JWT_ALG, JWT_EXPIRES_MIN, DISABLE_AUTH
from . import models
from .db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_password(pw: str, pw_hash: str) -> bool:
    return pwd_context.verify(pw, pw_hash)

def create_token(user: models.User) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": user.id,
        "usr": user.username,
        "adm": bool(user.is_admin),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRES_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    if DISABLE_AUTH:
        # Return first user if exists; otherwise treat as admin-less mode.
        u = db.query(models.User).first()
        if u:
            return u
        raise HTTPException(status_code=401, detail="Auth disabled but no users exist. Run /api/setup first.")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=401, detail="User not found")
    return u

def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if DISABLE_AUTH:
        return user
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user
