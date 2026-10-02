# src/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from src.database import get_session
from src.models.user import Usuario, UsuarioCreate, UsuarioPublic, Token
from src.auth.security import create_access_token
from src.auth.service import registrar_usuario, autenticar_usuario
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# response_model=UsuarioPublic para no devolver el hash de la contraseña
@router.post("/register", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED)
def register(user_data: UsuarioCreate, session: Session = Depends(get_session)):
    try:
        return registrar_usuario(session, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = autenticar_usuario(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioPublic)
def read_me(current_user: Usuario = Depends(get_current_user)):
    """Devuelve el usuario dueño del token (útil para probar el botón Authorize en /docs)."""
    return current_user
