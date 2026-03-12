from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, products, search
from .database import init_db

app = FastAPI(title="Amazon Clone Backend")

# Initialize database when server starts
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(search.router)


@app.get("/")
def home():
    return {"message": "Backend is running!"}
