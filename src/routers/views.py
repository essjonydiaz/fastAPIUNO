# src/routers/views.py
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlmodel import Session, select

from src.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.database import get_session
from src.models.agenda import Contacto, ContactoCreate
from src.models.user import Usuario, UsuarioCreate
from src.auth.security import create_access_token
from src.auth.service import autenticar_usuario, registrar_usuario
from src.auth.dependencies import COOKIE_NAME, get_current_user_cookie

# Ruta absoluta: funciona sin importar desde qué carpeta se lance uvicorn
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")
router = APIRouter(prefix="/views", tags=["Vistas Web (Jinja2)"])


def _redirect(url: str) -> RedirectResponse:
    # 303 See Other: después de un POST el navegador hace GET a la nueva URL
    return RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)


def _errores(e: ValidationError) -> list[str]:
    return [f"{err['loc'][-1]}: {err['msg']}" for err in e.errors()]


# ---------- Login / Registro / Logout ----------

@router.get("/login")
def login_form(request: Request, registrado: bool = False):
    # Starlette 1.x exige la firma TemplateResponse(request, nombre, contexto)
    return templates.TemplateResponse(request, "login.html", {"registrado": registrado})


@router.post("/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    usuario = autenticar_usuario(session, username, password)
    if not usuario:
        return templates.TemplateResponse(
            request, "login.html",
            {"error": "Usuario o contraseña incorrectos", "username": username},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    response = _redirect("/views/agenda")
    # El JWT viaja en una cookie HttpOnly (JavaScript no puede leerla)
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_access_token(data={"sub": usuario.username}),
        httponly=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse(request, "register.html", {"errores": [], "datos": {}})


@router.post("/register")
def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    datos = {"username": username, "email": email}
    try:
        registrar_usuario(session, UsuarioCreate(username=username, email=email, password=password))
    except ValidationError as e:
        errores = _errores(e)
    except ValueError as e:
        errores = [str(e)]
    else:
        return _redirect("/views/login?registrado=true")

    return templates.TemplateResponse(
        request, "register.html", {"errores": errores, "datos": datos},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@router.get("/logout")
def logout():
    response = _redirect("/views/login")
    response.delete_cookie(COOKIE_NAME)
    return response


# ---------- Agenda ----------

@router.get("/agenda")
def render_agenda_view(
    request: Request,
    session: Session = Depends(get_session),
    usuario: Optional[Usuario] = Depends(get_current_user_cookie),
):
    if usuario is None:
        return _redirect("/views/login")

    # Reto 2: solo los contactos del usuario logueado
    contactos = session.exec(select(Contacto).where(Contacto.user_id == usuario.id)).all()
    return templates.TemplateResponse(
        request, "agenda.html", {"contactos": contactos, "usuario": usuario}
    )


# Reto 3: formulario HTML para agregar contactos desde el navegador
@router.get("/agenda/nuevo")
def nuevo_contacto_form(
    request: Request,
    usuario: Optional[Usuario] = Depends(get_current_user_cookie),
):
    if usuario is None:
        return _redirect("/views/login")
    return templates.TemplateResponse(
        request, "contacto_form.html", {"usuario": usuario, "errores": [], "datos": {}}
    )


@router.post("/agenda/nuevo")
def nuevo_contacto_submit(
    request: Request,
    nombre: str = Form(...),
    telefono: str = Form(...),
    mail: str = Form(...),
    session: Session = Depends(get_session),
    usuario: Optional[Usuario] = Depends(get_current_user_cookie),
):
    if usuario is None:
        return _redirect("/views/login")

    datos = {"nombre": nombre, "telefono": telefono, "mail": mail}
    try:
        # Reutilizamos el mismo esquema de validación que la API REST
        contacto_in = ContactoCreate(**datos)
    except ValidationError as e:
        return templates.TemplateResponse(
            request, "contacto_form.html",
            {"usuario": usuario, "errores": _errores(e), "datos": datos},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    session.add(Contacto.model_validate(contacto_in, update={"user_id": usuario.id}))
    session.commit()
    return _redirect("/views/agenda")


@router.post("/agenda/{id}/eliminar")
def eliminar_contacto_view(
    id: int,
    session: Session = Depends(get_session),
    usuario: Optional[Usuario] = Depends(get_current_user_cookie),
):
    if usuario is None:
        return _redirect("/views/login")

    contacto = session.get(Contacto, id)
    if contacto and contacto.user_id == usuario.id:
        session.delete(contacto)
        session.commit()
    return _redirect("/views/agenda")
