# src/auth/dependencies.py
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from src.database import get_session
from src.models.user import Usuario
from src.auth.security import decode_access_token
from src.auth.service import get_usuario_por_username

# Apunta al endpoint exacto donde el cliente obtiene el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Nombre de la cookie donde las vistas HTML guardan el JWT
COOKIE_NAME = "access_token"


def _usuario_desde_token(token: Optional[str], session: Session) -> Optional[Usuario]:
    if not token:
        return None
    username = decode_access_token(token)
    if username is None:
        return None
    return get_usuario_por_username(session, username)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Usuario:
    """Para la API REST: lee el JWT del header Authorization: Bearer <token>."""
    usuario = _usuario_desde_token(token, session)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario


def get_current_user_cookie(
    request: Request,
    session: Session = Depends(get_session),
) -> Optional[Usuario]:
    """Para las vistas Jinja2: el navegador envia el JWT en una cookie HttpOnly.
    Devuelve None si no hay sesion, para que la vista redirija al login."""
    return _usuario_desde_token(request.cookies.get(COOKIE_NAME), session)
