from fastapi import APIRouter
from ..models import ProductOut
from ..database import get_connection

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/search", response_model=list[ProductOut])
def search_products(q: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE LOWER(title) LIKE ?",
        ("%" + q.lower() + "%",),
    )

    rows = cursor.fetchall()

    conn.close()

    return rows
