from fastapi import APIRouter, Depends, HTTPException
from ..database import get_connection, to_ist
from ..security import get_current_user

router = APIRouter(prefix="/invoice", tags=["Invoice"])


@router.get("/{invoice_id}")
def get_invoice(invoice_id: int, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    # ============================
    # GET INVOICE
    # ============================
    cursor.execute(
        "SELECT * FROM invoices WHERE id=? AND user_id=?",
        (invoice_id, user["user_id"])
    )
    invoice = cursor.fetchone()

    if not invoice:
        conn.close()
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice_data = dict(invoice)

    # FORMAT DATE
    invoice_data["created_at"] = to_ist(invoice_data.get("created_at"))

    # FALLBACK USERNAME
    invoice_data["username"] = invoice_data.get("username") or user["name"]

    # SAFE DEFAULTS
    invoice_data["address"] = invoice_data.get("address") or "N/A"
    invoice_data["pincode"] = invoice_data.get("pincode") or "N/A"
    invoice_data["payment_mode"] = invoice_data.get("payment_mode") or "N/A"
    invoice_data["total_amount"] = invoice_data.get("total_amount") or 0

    # ============================
    # ✅ GET ALL PRODUCTS USING invoice_id
    # ============================
    cursor.execute("""
        SELECT 
            o.id AS order_id,
            o.product_id,
            o.quantity,
            p.title,
            p.price,
            p.image
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.invoice_id = ?
    """, (invoice_id,))

    rows = cursor.fetchall()

    products = []

    for row in rows:
        item = dict(row)

        # SAFE VALUES
        price = item.get("price") or 0
        qty = item.get("quantity") or 0

        item["subtotal"] = price * qty

        products.append(item)

    # ============================
    # FINAL RESPONSE
    # ============================
    invoice_data["products"] = products
    # ✅ FIX: HANDLE ORDER IDS
    if invoice_data.get("order_id"):
        invoice_data["order_ids"] = [invoice_data["order_id"]]
    else:
        invoice_data["order_ids"] = [p["order_id"] for p in products]

    conn.close()
    return invoice_data
