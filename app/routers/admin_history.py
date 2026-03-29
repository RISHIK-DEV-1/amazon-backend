from fastapi import APIRouter, Depends, HTTPException, Query
from ..database import get_connection, to_ist   # ✅ UPDATED
from ..security import get_current_admin

router = APIRouter(prefix="/admin/history", tags=["Admin History"])


# ================= GET ALL HISTORY =================
@router.get("")
def get_all_histories(
    limit: int = Query(50, le=200),
    offset: int = 0,
    admin=Depends(get_current_admin)
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            uh.id,
            uh.user_id,
            uh.username,
            uh.product_id,
            uh.viewed_at,
            p.title AS product_title,
            p.price AS product_price,
            p.category AS product_category
        FROM user_history uh
        JOIN products p ON uh.product_id = p.id
        ORDER BY uh.viewed_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    # ✅ FIX TIME
    result = []
    for row in rows:
        item = dict(row)
        item["viewed_at"] = to_ist(item["viewed_at"])
        result.append(item)

    return result


# ================= DELETE SINGLE =================
@router.delete("/{history_id}")
def delete_history(history_id: int, admin=Depends(get_current_admin)):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM user_history WHERE id=?", (history_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="History not found")

    cursor.execute("DELETE FROM user_history WHERE id=?", (history_id,))
    conn.commit()
    conn.close()

    return {"message": "History deleted successfully"}


# ================= CLEAR ALL =================
@router.delete("")
def clear_all_history(admin=Depends(get_current_admin)):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM user_history")

    conn.commit()
    conn.close()

    return {"message": "All history cleared"}
