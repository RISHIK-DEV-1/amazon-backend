from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, products, search
from .database import init_db

app = FastAPI(title="Amazon Clone Backend")


@app.on_event("startup")
def startup():
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(products.router, prefix="/products")
app.include_router(search.router)


@app.get("/")
def home():
    return {"message": "Backend is running!"}
