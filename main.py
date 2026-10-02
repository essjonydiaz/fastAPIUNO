# main.py
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.database import create_db_and_tables
from src.middlewares.timer import response_time_middleware
from src.routers.auth import router as auth_router
from src.routers.agenda import router as agenda_router
from src.routers.views import router as views_router


# Lifespan: gestiona inicio y apagado de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar base de datos y crear tablas al arrancar
    create_db_and_tables()
    yield


app = FastAPI(
    title="Sistema de Agenda Empresarial",
    description="API Modular con SQLModel, OAuth2/JWT, Middlewares y Jinja2",
    version="2.0.0",
    lifespan=lifespan,
)

# 1. Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(response_time_middleware)

# Archivos estáticos (CSS/JS) en /static
app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "static"), name="static")

# 2. Routers Modulares
app.include_router(auth_router)
app.include_router(agenda_router)
app.include_router(views_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "docs": "/docs",
        "panel_web": "/views/agenda",
    }
