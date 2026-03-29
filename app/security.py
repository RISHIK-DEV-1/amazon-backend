from jose import jwt, JWTError
from datetime import datetime, timedelta
import hashlib
import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Secret key
SECRET_KEY = os.getenv("SECRET_KEY", "amazon_clone_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

# ---------------- CREATE TOKEN ----------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ---------------- VERIFY TOKEN ----------------
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "user_id" not in payload:
            return None
        return payload
    except JWTError:
        return None

# ---------------- HASH PASSWORD ----------------
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- GET CURRENT USER ----------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

# ---------------- GET CURRENT ADMIN ----------------
def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = get_current_user(credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload
