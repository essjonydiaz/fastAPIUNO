# src/models/user.py
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=3)
    email: EmailStr
    hashed_password: str


class UsuarioCreate(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    # bcrypt solo usa los primeros 72 bytes de la contrasena
    password: str = Field(min_length=6, max_length=72)


class UsuarioPublic(SQLModel):
    """Lo que la API devuelve de un usuario: nunca exponemos hashed_password."""
    id: int
    username: str
    email: EmailStr


class Token(SQLModel):
    access_token: str
    token_type: str
