# Sistema de Agenda con FastAPI

API modular con **FastAPI**, **SQLModel** (SQLite), autenticación **OAuth2 + JWT**, middlewares (CORS y tiempo de respuesta) y vistas HTML con **Jinja2**.

## Estructura

```
├── main.py                 # Punto de entrada
├── requirements.txt
├── static/                 # CSS
└── src/
    ├── config.py           # Llave secreta, algoritmo, URL de la BD
    ├── database.py         # Engine y sesión de SQLModel
    ├── models/             # Usuario y Contacto
    ├── auth/               # Hash de contraseñas, JWT y dependencias
    ├── routers/            # auth, agenda (API REST) y views (HTML)
    ├── middlewares/        # X-Process-Time
    └── templates/          # Plantillas Jinja2
```

## Instalación

```powershell
python -m venv fastAPI
.\fastAPI\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar

```powershell
uvicorn main:app --reload
```

- Panel web: http://127.0.0.1:8000/views/register
- Documentación Swagger: http://127.0.0.1:8000/docs

## Endpoints

| Método | Ruta | Protegida | Descripción |
|---|---|---|---|
| POST | `/auth/register` | No | Registrar usuario |
| POST | `/auth/token` | No | Login, devuelve el JWT |
| GET | `/auth/me` | Sí | Usuario dueño del token |
| GET | `/agenda` | Sí | Contactos del usuario |
| GET | `/agenda/{id}` | Sí | Un contacto propio |
| POST | `/agenda` | Sí | Crear contacto |
| PUT | `/agenda/{id}` | Sí | Actualizar contacto |
| DELETE | `/agenda/{id}` | Sí | Eliminar contacto |

## Retos resueltos

1. **Swagger con OAuth2:** en `/docs` se registra un usuario, se pulsa *Authorize* con su usuario y contraseña, y las rutas protegidas responden sin error 401.
2. **Relación de tablas:** `Contacto.user_id` es llave foránea a `usuario.id`; cada usuario solo ve, edita y elimina sus propios contactos.
3. **Formulario Jinja2:** `/views/agenda/nuevo` permite agregar contactos desde el navegador (con login por cookie y validación).

## Notas

- La llave secreta se puede definir con la variable de entorno `SECRET_KEY` (ver `src/config.py`).
- Si se cambian los modelos, borrar `agenda.db` para que las tablas se vuelvan a crear.
