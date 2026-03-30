from fastapi import APIRouter, Depends
from ..database import get_connection
from ..security import get_current_user

router = APIRouter(prefix="/address", tags=["Address"])


@router.post("")
def save_address(data: dict, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ CHECK if address exists
    cursor.execute(
        "SELECT id FROM addresses WHERE user_id=?",
        (user["user_id"],)
    )
    existing = cursor.fetchone()

    if existing:
        # ✅ UPDATE instead of REPLACE
        cursor.execute(
            "UPDATE addresses SET address=?, pincode=? WHERE user_id=?",
            (data.get("address", ""), data.get("pincode", ""), user["user_id"])
        )
    else:
        # ✅ INSERT first time
        cursor.execute(
            "INSERT INTO addresses (user_id, address, pincode) VALUES (?, ?, ?)",
            (user["user_id"], data.get("address", ""), data.get("pincode", ""))
        )

    conn.commit()
    conn.close()

    return {"message": "Address saved successfully"}


@router.get("")
def get_address(user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT address, pincode FROM addresses WHERE user_id=?",
        (user["user_id"],)
    )
    addr = cursor.fetchone()
    conn.close()

    if not addr:
        return {"address": "", "pincode": ""}

    return dict(addr)
