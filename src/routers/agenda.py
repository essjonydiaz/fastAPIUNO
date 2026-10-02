# src/routers/agenda.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.database import get_session
from src.models.agenda import Contacto, ContactoCreate, ContactoPublic, ContactoUpdate
from src.models.user import Usuario
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/agenda", tags=["Agenda CRUD"])


def _get_contacto_propio(id: int, session: Session, usuario: Usuario) -> Contacto:
    """Busca el contacto y verifica que pertenezca al usuario autenticado.
    Si es de otro usuario respondemos 404 (no 403) para no revelar que existe."""
    contacto = session.get(Contacto, id)
    if not contacto or contacto.user_id != usuario.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")
    return contacto


@router.get("", response_model=List[ContactoPublic])
def get_contactos(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return session.exec(select(Contacto).where(Contacto.user_id == current_user.id)).all()


@router.get("/{id}", response_model=ContactoPublic)
def get_contacto(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return _get_contacto_propio(id, session, current_user)


@router.post("", response_model=ContactoPublic, status_code=status.HTTP_201_CREATED)
def crear_contacto(
    contacto_in: ContactoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),  # Ruta protegida con JWT
):
    # Reto 2: el dueño del contacto es el usuario del token
    nuevo = Contacto.model_validate(contacto_in, update={"user_id": current_user.id})
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=ContactoPublic)
def actualizar_contacto(
    id: int,
    contacto_in: ContactoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),  # Ruta protegida con JWT
):
    contacto_db = _get_contacto_propio(id, session, current_user)

    update_data = contacto_in.model_dump(exclude_unset=True)
    contacto_db.sqlmodel_update(update_data)

    session.add(contacto_db)
    session.commit()
    session.refresh(contacto_db)
    return contacto_db


@router.delete("/{id}")
def eliminar_contacto(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),  # Ruta protegida con JWT
):
    contacto = _get_contacto_propio(id, session, current_user)
    session.delete(contacto)
    session.commit()
    return {"mensaje": f"Contacto {id} eliminado correctamente por @{current_user.username}"}
