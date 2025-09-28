from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# --- Shared base model ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    balance: float = 0
    vending_code: Optional[str] = ''
    recent_usage: Optional[str] = ''
    auth_type: str  # 'manual' or 'google'


# --- Manual registration input ---
class ManualRegisterCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


# --- Unified user creation input (manual/google) ---
class UserCreate(UserBase):
    id: str  # Firebase UID or UUID
    # Optional password (None for Google sign-up)
    password: Optional[str] = None


# --- Response model for full user data ---
class User(UserBase):
    id: str
    created_at: datetime


# --- Optional: response model for manual reg only ---
class RegisterOut(BaseModel):
    id: int  # because DB is returning an integer
    full_name: str  # match DB column name
    email: EmailStr

