# src/auth/service.py
# Logica de usuarios compartida por la API REST (routers/auth.py) y las vistas HTML (routers/views.py)
from typing import Optional

from sqlmodel import Session, select

from src.models.user import Usuario, UsuarioCreate
from src.auth.security import get_password_hash, verify_password


def get_usuario_por_username(session: Session, username: str) -> Optional[Usuario]:
    return session.exec(select(Usuario).where(Usuario.username == username)).first()


def registrar_usuario(session: Session, user_data: UsuarioCreate) -> Usuario:
    """Crea el usuario. Lanza ValueError si el username ya existe."""
    if get_usuario_por_username(session, user_data.username):
        raise ValueError("El nombre de usuario ya esta registrado")

    nuevo_usuario = Usuario(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
    )
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    return nuevo_usuario


def autenticar_usuario(session: Session, username: str, password: str) -> Optional[Usuario]:
    usuario = get_usuario_por_username(session, username)
    if not usuario or not verify_password(password, usuario.hashed_password):
        return None
    return usuario
