from fastapi import APIRouter, Depends
from ..database import get_connection
from ..security import get_current_admin

router = APIRouter(prefix="/admin/analytics", tags=["Admin Analytics"])


@router.get("")
def get_analytics(admin=Depends(get_current_admin)):

    conn = get_connection()
    cursor = conn.cursor()

    # ================= BASIC COUNTS =================
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    total_admins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM user_history")
    total_views = cursor.fetchone()[0]

    # ================= ORDERS =================
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    # TOTAL REVENUE
    cursor.execute("""
        SELECT COALESCE(SUM(p.price), 0)
        FROM orders o
        JOIN products p ON o.product_id = p.id
    """)
    total_revenue = cursor.fetchone()[0]

    # ORDER STATUS COUNT
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM orders
        GROUP BY status
    """)
    order_status = [dict(row) for row in cursor.fetchall()]

    # ================= TOP PRODUCTS =================
    cursor.execute("""
        SELECT p.title, COUNT(*) as views
        FROM user_history uh
        JOIN products p ON uh.product_id = p.id
        GROUP BY uh.product_id
        ORDER BY views DESC
        LIMIT 10
    """)
    top_products = [dict(row) for row in cursor.fetchall()]

    # ================= ACTIVE USERS =================
    cursor.execute("""
        SELECT username, COUNT(*) as activity
        FROM user_history
        GROUP BY user_id
        ORDER BY activity DESC
        LIMIT 5
    """)
    active_users = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "total_products": total_products,
        "total_users": total_users,
        "total_admins": total_admins,
        "total_views": total_views,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "order_status": order_status,
        "top_products": top_products,
        "active_users": active_users
    }
