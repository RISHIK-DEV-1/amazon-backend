from fastapi import APIRouter, HTTPException, Depends
from ..database import get_connection
from ..security import get_current_admin

router = APIRouter(tags=["Products"])


# ---------------- GET ALL PRODUCTS ----------------
@router.get("")
def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    conn.close()
    return [dict(row) for row in rows]


# ---------------- GET PRODUCTS BY CATEGORY (CASE-INSENSITIVE) ----------------
@router.get("/category/{category}")
def get_products_by_category(category: str):
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ CASE-INSENSITIVE MATCH
    cursor.execute(
        "SELECT * FROM products WHERE LOWER(category) = LOWER(?)",
        (category.strip(),)
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ---------------- GET SINGLE PRODUCT ----------------
@router.get("/{product_id}")
def get_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
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

    cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    username = user["name"] if user else "Guest"

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


# ================= ADMIN SECTION =================

# ---------------- ADD PRODUCT ----------------
@router.post("/admin/products")
def add_product(product: dict, admin=Depends(get_current_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ NORMALIZE CATEGORY (important fix)
    category = (product.get("category") or "").strip().lower()

    cursor.execute("""
        INSERT INTO products (title, price, category, image, description, features)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        product.get("title"),
        product.get("price"),
        category,  # ✅ normalized
        product.get("image"),
        product.get("description"),
        product.get("features")
    ))

    conn.commit()
    conn.close()

    return {"message": "Product added successfully"}


# ---------------- UPDATE PRODUCT ----------------
@router.put("/admin/products/{product_id}")
def update_product(product_id: int, product: dict, admin=Depends(get_current_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM products WHERE id=?", (product_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    # ✅ NORMALIZE CATEGORY
    category = (product.get("category") or "").strip().lower()

    cursor.execute("""
        UPDATE products
        SET title=?, price=?, category=?, image=?, description=?, features=?
        WHERE id=?
    """, (
        product.get("title"),
        product.get("price"),
        category,  # ✅ normalized
        product.get("image"),
        product.get("description"),
        product.get("features"),
        product_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Product updated successfully"}


# ---------------- DELETE PRODUCT ----------------
@router.delete("/admin/products/{product_id}")
def delete_product(product_id: int, admin=Depends(get_current_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM products WHERE id=?", (product_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))

    conn.commit()
    conn.close()

    return {"message": "Product deleted successfully"}
