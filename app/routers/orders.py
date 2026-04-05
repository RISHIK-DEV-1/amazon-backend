from fastapi import APIRouter, Depends, HTTPException, Body
from ..database import get_connection, to_ist
from ..security import get_current_user, get_current_admin

router = APIRouter(prefix="/orders", tags=["Orders"])

# ============================
# PLACE BULK ORDER
# ============================
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

    # ADDRESS
    cursor.execute(
        "SELECT address, pincode FROM addresses WHERE user_id=?",
        (user["user_id"],)
    )
    addr = cursor.fetchone()

    if not addr:
        conn.close()
        raise HTTPException(status_code=400, detail="No saved address found")

    address = addr["address"]
    pincode = addr["pincode"]

    total_amount = 0
    order_ids = []

    # CREATE ORDERS
    for item in items:
        product_id = int(item.get("product_id"))
        quantity = int(item.get("quantity", 1))
        amount = float(item.get("amount", 0))

        cursor.execute("SELECT price FROM products WHERE id=?", (product_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Product not found")

        expected_total = row["price"] * quantity

        if amount != expected_total:
            conn.close()
            raise HTTPException(status_code=400, detail="Payment mismatch")

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

    # CREATE SINGLE INVOICE (MASTER ORDER)
    cursor.execute(
        """
        INSERT INTO invoices
        (user_id, username, address, pincode, total_amount, payment_mode)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user["user_id"], user["name"], address, pincode, total_amount, payment_mode)
    )

    invoice_id = cursor.lastrowid

    # LINK ALL ORDERS TO SAME INVOICE
    for oid in order_ids:
        cursor.execute(
            "UPDATE orders SET invoice_id=? WHERE id=?",
            (invoice_id, oid)
        )

    conn.commit()
    conn.close()

    return {"message": "Bulk order placed successfully", "invoice_id": invoice_id}


# ============================
# PLACE SINGLE ORDER
# ============================
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

    # ADDRESS
    cursor.execute(
        "SELECT address, pincode FROM addresses WHERE user_id=?",
        (user["user_id"],)
    )
    addr = cursor.fetchone()

    if not addr:
        conn.close()
        raise HTTPException(status_code=400, detail="No saved address found")

    address = addr["address"]
    pincode = addr["pincode"]

    cursor.execute("SELECT price FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    expected_total = row["price"] * quantity

    if amount != expected_total:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid amount")

    # CREATE ORDER
    cursor.execute(
        "INSERT INTO orders (user_id, username, product_id, quantity, status) VALUES (?, ?, ?, ?, 'placed')",
        (user["user_id"], user["name"], product_id, quantity)
    )

    order_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO order_status_history (order_id, status) VALUES (?, 'placed')",
        (order_id,)
    )

    # CREATE INVOICE
    cursor.execute(
        """
        INSERT INTO invoices
        (user_id, username, address, pincode, total_amount, payment_mode)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user["user_id"], user["name"], address, pincode, amount, payment_mode)
    )

    invoice_id = cursor.lastrowid

    # LINK ORDER
    cursor.execute(
        "UPDATE orders SET invoice_id=? WHERE id=?",
        (invoice_id, order_id)
    )

    conn.commit()
    conn.close()

    return {"message": "Order placed successfully", "invoice_id": invoice_id}


# ============================
# GET MY ORDERS
# ============================
@router.get("/my")
def get_my_orders(user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.id, o.invoice_id, o.status, o.created_at,
               o.username, o.quantity,
               p.title, p.price, p.image,
               i.address, i.pincode, i.payment_mode
        FROM orders o
        JOIN products p ON o.product_id = p.id
        LEFT JOIN invoices i ON o.invoice_id = i.id
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


# ============================
# ADMIN ORDERS (GROUPED BY INVOICE)
# ============================
@router.get("/admin")
def get_all_orders(admin=Depends(get_current_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            o.invoice_id,
            MAX(o.status) as status,
            MAX(o.created_at) as created_at,
            o.username,
            COUNT(o.id) as total_items,
            SUM(o.quantity) as total_qty,
            GROUP_CONCAT(p.title) as titles,
            GROUP_CONCAT(p.image) as images
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.invoice_id IS NOT NULL
        GROUP BY o.invoice_id
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    result = []

    for r in rows:
        data = dict(r)
        data["created_at"] = to_ist(data["created_at"])
        data["title"] = (data["titles"] or "").split(",")[0]
        data["image"] = (data["images"] or "").split(",")[0]
        result.append(data)

    conn.close()
    return result


# ============================
# UPDATE STATUS (ALL PRODUCTS IN INVOICE)
# ============================
@router.put("/{invoice_id}")
def update_order_status(invoice_id: int, status: str, admin=Depends(get_current_admin)):
    if status not in ["placed", "shipped", "delivered", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    conn = get_connection()
    cursor = conn.cursor()

    # UPDATE ALL ORDERS IN THIS INVOICE
    cursor.execute(
        "UPDATE orders SET status=? WHERE invoice_id=?",
        (status, invoice_id)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    # ADD HISTORY FOR ALL ORDERS
    cursor.execute(
        "SELECT id FROM orders WHERE invoice_id=?",
        (invoice_id,)
    )
    order_ids = cursor.fetchall()

    for o in order_ids:
        cursor.execute(
            "INSERT INTO order_status_history (order_id, status) VALUES (?, ?)",
            (o["id"], status)
        )

    conn.commit()
    conn.close()
    return {"message": f"Order status updated to {status} for all items"}


# ============================
# CANCEL ORDER (USER)
# ============================
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

    # CANCEL ALL ORDERS IN SAME INVOICE IF LINKED
    invoice_id = order["invoice_id"]
    if invoice_id:
        cursor.execute(
            "UPDATE orders SET status='cancelled' WHERE invoice_id=?",
            (invoice_id,)
        )

        cursor.execute(
            "SELECT id FROM orders WHERE invoice_id=?",
            (invoice_id,)
        )
        order_ids = cursor.fetchall()

        for o in order_ids:
            cursor.execute(
                "INSERT INTO order_status_history (order_id, status) VALUES (?, 'cancelled')",
                (o["id"],)
            )
    else:
        # Just cancel single order if no invoice
        cursor.execute(
            "UPDATE orders SET status='cancelled' WHERE id=?",
            (order_id,)
        )
        cursor.execute(
            "INSERT INTO order_status_history (order_id, status) VALUES (?, 'cancelled')",
            (order_id,)
        )

    conn.commit()
    conn.close()
    return {"message": "Order cancelled successfully"}


# ============================
# DELETE ORDER (ADMIN)
# ============================
@router.delete("/{invoice_id}")
def delete_order(invoice_id: int, admin=Depends(get_current_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    # DELETE HISTORY FIRST
    cursor.execute("SELECT id FROM orders WHERE invoice_id=?", (invoice_id,))
    order_ids = cursor.fetchall()

    for o in order_ids:
        cursor.execute("DELETE FROM order_status_history WHERE order_id=?", (o["id"],))

    # DELETE ORDERS
    cursor.execute("DELETE FROM orders WHERE invoice_id=?", (invoice_id,))

    # DELETE INVOICE
    cursor.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))

    conn.commit()
    conn.close()
    return {"message": "Order deleted for all items"}
#CHECK IF PRODUCT ORDERED WITH STATUS
@router.get("/check/{product_id}")
def check_order(product_id: int, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT status FROM orders 
        WHERE user_id=? AND product_id=? 
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (user["user_id"], product_id)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"ordered": False}

    status = row["status"]

    # ✅ allow re-buy if delivered or cancelled
    if status in ["delivered", "cancelled"]:
        return {"ordered": False}

    return {"ordered": True}
