from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import routes_auth, routes_user, routes_task, routes_kanban
from routes.statistics_route import router as statistics_router
from scripts.init_kanban import init_kanban_columns
import logging


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Gestión de Tareas",
    description="API para gestionar tareas y usuarios",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
logger.info("Registering routes...")
app.include_router(routes_auth.router)
app.include_router(routes_user.router)
app.include_router(routes_task.router)
app.include_router(routes_kanban.router)
app.include_router(statistics_router)
logger.info("Routes registered successfully")

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Gestión de Tareas"}

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    try:
        # Inicializar columnas del Kanban
        await init_kanban_columns()
        logger.info("Aplicación iniciada exitosamente")
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")
    # Aquí puedes agregar cualquier código de limpieza necesario



