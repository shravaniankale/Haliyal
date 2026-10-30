import hashlib
import hmac
import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import SECRET_KEY
from .database import get_db
from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    """Secure SHA-256 hash with salt for local development without external compiled binaries."""
    salt = "krishi_mitra_salt_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict) -> str:
    """Creates a token string payload."""
    payload = data.copy()
    user_id = str(payload.get("sub"))
    role = str(payload.get("role", "farmer"))
    timestamp = str(int(datetime.datetime.utcnow().timestamp()))
    signature = hmac.new(SECRET_KEY.encode(), f"{user_id}:{role}:{timestamp}".encode(), hashlib.sha256).hexdigest()
    return f"{user_id}:{role}:{timestamp}:{signature}"

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    """Dependency to retrieve authenticated user from bearer token."""
    if not token:
        return None
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return None
        user_id, role, timestamp, sig = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), f"{user_id}:{role}:{timestamp}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except Exception:
        return None

def require_current_user(user: Optional[User] = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
