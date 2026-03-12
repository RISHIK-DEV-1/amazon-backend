from fastapi import APIRouter, HTTPException
from ..models import ProductOut
from ..database import get_connection

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductOut])
def get_all_products():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    conn.close()

    return rows


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()

    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    return row


@router.get("/category/{category}", response_model=list[ProductOut])
def get_by_category(category: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE category=?", (category,))
    rows = cursor.fetchall()

    conn.close()

    return rows
