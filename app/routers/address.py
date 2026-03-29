from fastapi import APIRouter, Depends, HTTPException
from ..database import get_connection
from ..security import get_current_user

router = APIRouter(prefix="/address", tags=["Address"])

@router.post("")
def save_address(data: dict, user=Depends(get_current_user)):
    """
    data example:
    {
        "address": "123 Main Street",
        "pincode": "560001"
    }
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO addresses (user_id, address, pincode) VALUES (?, ?, ?)",
        (user["user_id"], data.get("address", ""), data.get("pincode", ""))
    )

    conn.commit()
    conn.close()
    return {"message": "Address saved successfully"}

@router.get("")
def get_address(user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM addresses WHERE user_id=?", (user["user_id"],))
    addr = cursor.fetchone()
    conn.close()

    if not addr:
        raise HTTPException(status_code=404, detail="Address not found")

    return dict(addr)
