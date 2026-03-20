from pydantic import BaseModel, EmailStr
from typing import Optional


# -------- USER MODELS --------

class UserCreate(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class EmailCheck(BaseModel):
    email: EmailStr


# -------- PASSWORD RESET --------

class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str


# -------- PRODUCT MODEL --------

class ProductOut(BaseModel):
    id: int
    title: str
    price: int
    category: str
    image: str

    class Config:
        from_attributes = True


# -------- HISTORY MODEL --------

class HistoryItem(BaseModel):
    product_id: int
