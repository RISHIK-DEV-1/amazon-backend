from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, products, search
from .database import init_db

app = FastAPI(title="Amazon Clone Backend")


# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup():
    init_db()


# ---------------- CORS CONFIG ----------------
origins = [
   # "http://localhost:3000",   # local frontend
    #"http://127.0.0.1:3000",  # local frontend alt
    "http://localhost:5173",     # ✅ ADD THIS
    "http://127.0.0.1:5173",    # ✅ ADD THIS

    "https://amazongo-store.vercel.app"   # 🔥 REPLACE with your actual Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # ✅ secure & correct
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- ROUTES ----------------
app.include_router(auth.router, prefix="/auth")
app.include_router(products.router, prefix="/products")
app.include_router(search.router)


@app.get("/")
def home():
    return {"message": "Backend is running!"}
