from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------------- ROUTERS ----------------
from .routers import auth, products, search
from .routers import admin_users, admin_history, admin_analytics
from .routers import orders       # ✅ Orders system
from .routers import invoice      # ✅ Invoice system
from .routers import address      # ✅ Address system

from .database import init_db

app = FastAPI(title="Amazon Clone Backend")


# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup():
    init_db()


# ---------------- CORS CONFIG ----------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://amazongo-store.vercel.app",
    "https://www.amazongo-store.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- ROUTES ----------------

# 🔐 AUTH
app.include_router(auth.router, prefix="/auth")

# 📦 PRODUCTS
app.include_router(products.router, prefix="/products")

# 🔍 SEARCH
app.include_router(search.router, prefix="/search")

# 👑 ADMIN
app.include_router(admin_users.router)
app.include_router(admin_history.router)
app.include_router(admin_analytics.router)

# 🛒 ORDERS
app.include_router(orders.router)

# 🧾 INVOICE
app.include_router(invoice.router)

# 🏠 ADDRESS
app.include_router(address.router)


# ---------------- ROOT ----------------
@app.get("/")
def home():
    return {"message": "Backend is running!"}
