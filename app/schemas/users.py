# app/esquemas/user.py
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str | None = None  # opcional para actualizar

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True
