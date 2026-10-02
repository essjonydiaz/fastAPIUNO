# src/config.py
import os

# En produccion definir estas variables de entorno (nunca subir la llave al repositorio)
SECRET_KEY = os.getenv("SECRET_KEY", "CAMBIAR_ESTA_LLAVE_SECRETA_SUPER_SEGURA_EN_PRODUCCION")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# SQLite por defecto; para PostgreSQL: postgresql://usuario:clave@localhost:5432/agenda
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agenda.db")
