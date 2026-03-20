# products.py
from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(tags=["Products"])


# ---------------- GET ALL PRODUCTS ----------------
@router.get("")
def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, price, category, image, description, features
        FROM products
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ---------------- GET PRODUCTS BY CATEGORY ----------------
@router.get("/category/{category}")
def get_products_by_category(category: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, price, category, image, description, features
        FROM products WHERE category=?
    """, (category,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ---------------- GET SINGLE PRODUCT ----------------
@router.get("/{product_id}")
def get_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, price, category, image, description, features
        FROM products WHERE id=?
    """, (product_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    return dict(row)


# ---------------- LOG VIEWED PRODUCT ----------------
@router.post("/view/{user_id}/{product_id}")
def log_view(user_id: int, product_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ Get username from users table
    cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    username = user["name"] if user else "Guest"

    # ✅ Insert with username
    cursor.execute(
        "INSERT INTO user_history (user_id, username, product_id) VALUES (?, ?, ?)",
        (user_id, username, product_id)
    )

    conn.commit()
    conn.close()

    return {"message": "View logged successfully"}


# ---------------- GET USER HISTORY ----------------
@router.get("/history/{user_id}")
def get_history(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.id,
            p.title,
            p.price,
            p.category,
            p.image,
            uh.username,
            uh.viewed_at
        FROM user_history uh
        JOIN products p ON uh.product_id = p.id
        WHERE uh.user_id=?
        ORDER BY uh.rowid DESC
        LIMIT 20
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
