from fastapi import APIRouter, Depends, HTTPException
from ..database import get_connection
from ..security import get_current_admin

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


# ---------------- GET ALL USERS ----------------
@router.get("")
def get_all_users(admin=Depends(get_current_admin)):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, role FROM users")
    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ---------------- MAKE USER ADMIN ----------------
@router.put("/{user_id}/make-admin")
def make_admin(user_id: int, admin=Depends(get_current_admin)):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return {"message": "User promoted to admin"}


# ---------------- REMOVE ADMIN ROLE ----------------
@router.put("/{user_id}/remove-admin")
def remove_admin(user_id: int, admin=Depends(get_current_admin)):

    # 🚫 Prevent self-demotion
    if admin["user_id"] == user_id:
        raise HTTPException(status_code=400, detail="You cannot remove your own admin access")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("UPDATE users SET role='user' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return {"message": "Admin role removed"}


# ---------------- DELETE USER ----------------
@router.delete("/{user_id}")
def delete_user(user_id: int, admin=Depends(get_current_admin)):

    # 🚫 Prevent deleting yourself
    if admin["user_id"] == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return {"message": "User deleted successfully"}
