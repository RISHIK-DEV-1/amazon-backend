from fastapi import APIRouter, Depends, HTTPException, Body
from ..database import get_connection, to_ist
from ..security import get_current_user, get_current_admin

router = APIRouter(prefix="/orders", tags=["Orders"])

# ----------------------------
# PLACE SINGLE ORDER
# ----------------------------
@router.post("/{product_id}")
def place_order(
    product_id: int,
    data: dict = Body(...),
    user=Depends(get_current_user)
):
    amount = data.get("amount", 0)
    quantity = data.get("quantity", 1)
    payment_mode = data.get("payment_mode", "")

    conn = get_connection()
    cursor = conn.cursor()

    # ✅ FETCH SAVED ADDRESS
    cursor.execute("SELECT address, pincode FROM addresses WHERE user_id=?", (user["user_id"],))
    addr = cursor.fetchone()
    if not addr:
        conn.close()
        raise HTTPException(status_code=400, detail="No saved address found")

    address = addr["address"]
    pincode = addr["pincode"]

    # PRODUCT CHECK
    cursor.execute("SELECT price FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    product_price = row["price"]
    expected_total = product_price * quantity

    if amount != expected_total:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Payment must match ₹{expected_total}")

    # INSERT ORDER
    cursor.execute(
        "INSERT INTO orders (user_id, username, product_id, quantity, status) VALUES (?, ?, ?, ?, 'placed')",
        (user["user_id"], user["name"], product_id, quantity)
    )
    order_id = cursor.lastrowid

    # TIMELINE
    cursor.execute(
        "INSERT INTO order_status_history (order_id, status) VALUES (?, 'placed')",
        (order_id,)
    )

    # INVOICE WITH SAVED ADDRESS
    cursor.execute(
        "INSERT INTO invoices (order_id, user_id, username, address, pincode, total_amount, payment_mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (order_id, user["user_id"], user["name"], address, pincode, amount, payment_mode)
    )
    invoice_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {"message": "Order placed successfully", "invoice_id": invoice_id}


# ----------------------------
# PLACE BULK ORDER
# ----------------------------
@router.post("/bulk")
def place_bulk_order(
    data: dict = Body(...),
    user=Depends(get_current_user)
):
    items = data.get("items", [])
    payment_mode = data.get("payment_mode", "")

    if not items:
        raise HTTPException(status_code=400, detail="No items to order")

    conn = get_connection()
    cursor = conn.cursor()

    # ✅ FETCH SAVED ADDRESS
    cursor.execute("SELECT address, pincode FROM addresses WHERE user_id=?", (user["user_id"],))
    addr = cursor.fetchone()
    if not addr:
        conn.close()
        raise HTTPException(status_code=400, detail="No saved address found")

    address = addr["address"]
    pincode = addr["pincode"]

    total_amount = 0
    order_ids = []

    for item in items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 1)
        amount = item.get("amount", 0)

        cursor.execute("SELECT price FROM products WHERE id=?", (product_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

        product_price = row["price"]
        expected_total = product_price * quantity

        if amount != expected_total:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Payment for product {product_id} must match ₹{expected_total}"
            )

        cursor.execute(
            "INSERT INTO orders (user_id, username, product_id, quantity, status) VALUES (?, ?, ?, ?, 'placed')",
            (user["user_id"], user["name"], product_id, quantity)
        )

        order_id = cursor.lastrowid
        order_ids.append(order_id)
        total_amount += amount

        cursor.execute(
            "INSERT INTO order_status_history (order_id, status) VALUES (?, 'placed')",
            (order_id,)
        )

    # INVOICE
    cursor.execute(
        "INSERT INTO invoices (order_id, user_id, username, address, pincode, total_amount, payment_mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (order_ids[0], user["user_id"], user["name"], address, pincode, total_amount, payment_mode)
    )

    invoice_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {"message": "Bulk order placed successfully", "invoice_id": invoice_id}


# ----------------------------
# GET MY ORDERS
# ----------------------------
@router.get("/my")
def get_my_orders(user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.id, o.status, o.created_at,
               o.username, o.quantity,
               p.title, p.price, p.image,
               i.id as invoice_id, i.address, i.pincode, i.payment_mode
        FROM orders o
        JOIN products p ON o.product_id = p.id
        LEFT JOIN invoices i ON o.id = i.order_id
        WHERE o.user_id=?
        ORDER BY o.created_at DESC
    """, (user["user_id"],))

    orders = cursor.fetchall()
    result = []

    for o in orders:
        order = dict(o)
        order["created_at"] = to_ist(order["created_at"])

        cursor.execute("""
            SELECT status, created_at
            FROM order_status_history
            WHERE order_id=?
            ORDER BY created_at ASC
        """, (o["id"],))

        timeline = [
            dict(h) | {"created_at": to_ist(h["created_at"])}
            for h in cursor.fetchall()
        ]

        order["timeline"] = timeline
        result.append(order)

    conn.close()
    return result


# ----------------------------
# ADMIN ORDERS
# ----------------------------
@router.get("/admin")
def get_all_orders(admin=Depends(get_current_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.id, o.status, o.created_at,
               o.username, o.user_id, o.quantity,
               p.title, p.price, p.image
        FROM orders o
        JOIN products p ON o.product_id = p.id
        ORDER BY o.created_at DESC
    """)

    orders = [
        dict(o) | {"created_at": to_ist(o["created_at"])}
        for o in cursor.fetchall()
    ]

    conn.close()
    return orders


# ----------------------------
# UPDATE STATUS
# ----------------------------
@router.put("/{order_id}")
def update_order_status(order_id: int, status: str, admin=Depends(get_current_admin)):
    if status not in ["placed", "shipped", "delivered", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    cursor.execute(
        "INSERT INTO order_status_history (order_id, status) VALUES (?, ?)",
        (order_id, status)
    )

    conn.commit()
    conn.close()

    return {"message": "Order status updated"}


# ----------------------------
# CANCEL ORDER
# ----------------------------
@router.put("/cancel/{order_id}")
def cancel_order(order_id: int, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM orders WHERE id=? AND user_id=?",
        (order_id, user["user_id"])
    )

    order = cursor.fetchone()

    if not order:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    if order["status"] == "delivered":
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot cancel delivered order")

    cursor.execute("UPDATE orders SET status='cancelled' WHERE id=?", (order_id,))
    cursor.execute(
        "INSERT INTO order_status_history (order_id, status) VALUES (?, 'cancelled')",
        (order_id,)
    )

    conn.commit()
    conn.close()

    return {"message": "Order cancelled"}


# ----------------------------
# DELETE ORDER
# ----------------------------
@router.delete("/{order_id}")
def delete_order(order_id: int, admin=Depends(get_current_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM order_status_history WHERE order_id=?", (order_id,))
    cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    conn.commit()
    conn.close()

    return {"message": "Order deleted"}
