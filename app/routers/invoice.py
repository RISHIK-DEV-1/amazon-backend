from fastapi import APIRouter, Depends, HTTPException
from ..database import get_connection, to_ist
from ..security import get_current_user

router = APIRouter(prefix="/invoice", tags=["Invoice"])

@router.get("/{invoice_id}")
def get_invoice(invoice_id: int, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM invoices WHERE id=? AND user_id=?", (invoice_id, user["user_id"]))
    invoice = cursor.fetchone()
    if not invoice:
        conn.close()
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice_data = dict(invoice)
    invoice_data["created_at"] = to_ist(invoice_data["created_at"])
    invoice_data["username"] = invoice_data.get("username") or user["name"]

    cursor.execute("""
        SELECT o.id AS order_id, o.product_id, o.quantity, p.title, p.price, p.image
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.user_id=? AND o.id IN (SELECT order_id FROM invoices WHERE id=?)
    """, (user["user_id"], invoice_id))
    products = [dict(p) for p in cursor.fetchall()]

    for p in products:
        p["subtotal"] = p["quantity"] * p["price"]

    invoice_data["products"] = products
    invoice_data["address"] = invoice_data.get("address") or "N/A"
    invoice_data["pincode"] = invoice_data.get("pincode") or "N/A"
    invoice_data["payment_mode"] = invoice_data.get("payment_mode") or "N/A"

    conn.close()
    return invoice_data
