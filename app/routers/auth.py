from fastapi import APIRouter, HTTPException

from ..models import UserCreate, ResetPassword
from ..database import get_connection
from ..security import create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("")
def auth_user(user: UserCreate):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, password FROM users WHERE email=?",
        (user.email,),
    )

    db_user = cursor.fetchone()

    if db_user:

        if hash_password(user.password) != db_user["password"]:
            conn.close()
            raise HTTPException(status_code=401, detail="Incorrect password")

        user_data = {
            "id": db_user["id"],
            "name": db_user["name"],
            "email": db_user["email"],
        }

    else:

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (user.name or "Amazon Customer", user.email, hash_password(user.password)),
        )

        conn.commit()

        user_data = {
            "id": cursor.lastrowid,
            "name": user.name or "Amazon Customer",
            "email": user.email,
        }

    conn.close()

    token = create_access_token(
        {
            "user_id": user_data["id"],
            "name": user_data["name"],
            "email": user_data["email"],
        }
    )

    return {"user": user_data, "token": token}


@router.post("/reset-password")
def reset_password(data: ResetPassword):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email=?", (data.email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Email not registered")

    cursor.execute(
        "UPDATE users SET password=? WHERE email=?",
        (hash_password(data.new_password), data.email),
    )

    conn.commit()
    conn.close()

    return {"message": "Password updated successfully"}
