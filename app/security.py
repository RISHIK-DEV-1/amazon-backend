from jose import jwt, JWTError
from datetime import datetime, timedelta
import hashlib
import os

# Secret key (use environment variable in production)
SECRET_KEY = os.getenv("SECRET_KEY", "amazon_clone_secret_key")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


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

        # Ensure required fields exist
        if "user_id" not in payload:
            return None

        return payload

    except JWTError:
        return None


# ---------------- HASH PASSWORD ----------------

def hash_password(password: str):

    return hashlib.sha256(password.encode()).hexdigest()
