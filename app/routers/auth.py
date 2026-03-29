from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models import UserCreate, ResetPassword
from ..database import get_connection
from ..security import create_access_token, hash_password, verify_token

router = APIRouter(tags=["Auth"])
security = HTTPBearer()

# ---------------- LOGIN / SIGNUP ----------------
@router.post("")
def auth_user(user: UserCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, password, role FROM users WHERE email=?", (user.email,))
    db_user = cursor.fetchone()

    if db_user:
        if hash_password(user.password) != db_user["password"]:
            conn.close()
            raise HTTPException(status_code=401, detail="Incorrect password")
        user_data = {"id": db_user["id"], "name": db_user["name"], "email": db_user["email"], "role": db_user["role"]}
    else:
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (user.name or "Amazon Customer", user.email, hash_password(user.password), "user")
        )
        conn.commit()
        user_data = {"id": cursor.lastrowid, "name": user.name or "Amazon Customer", "email": user.email, "role": "user"}

    conn.close()
    token = create_access_token({"user_id": user_data["id"], "name": user_data["name"], "email": user_data["email"], "role": user_data["role"]})
    return {"user": user_data, "token": token}

# ---------------- RESET PASSWORD ----------------
@router.post("/reset-password")
def reset_password(data: ResetPassword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email=?", (data.email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Email not registered")

    cursor.execute("UPDATE users SET password=? WHERE email=?", (hash_password(data.new_password), data.email))
    conn.commit()
    conn.close()
    return {"message": "Password updated successfully"}

# ---------------- CURRENT USER ----------------
@router.get("/me")
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"id": payload["user_id"], "name": payload["name"], "email": payload["email"], "role": payload["role"]}

# ---------------- ADMIN DEPENDENCY ----------------
def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload
