# src/database.py
from sqlmodel import SQLModel, create_engine, Session
from src.config import DATABASE_URL

# connect_args={"check_same_thread": False} es requerido solo para SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables():
    """Crea las tablas definidas si no existen al iniciar la app."""
    import src.models  # noqa: F401  registra todos los modelos en SQLModel.metadata
    SQLModel.metadata.create_all(engine)


def get_session():
    """Generador de sesion inyectable mediante Depends() de FastAPI."""
    with Session(engine) as session:
        yield session
