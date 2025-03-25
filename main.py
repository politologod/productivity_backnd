from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.routes_task import router as task_router
from routes.routes_user import router as user_router
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FARM API Tutorial")

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
app.include_router(task_router)
app.include_router(user_router)
logger.info("Routes registered successfully")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FARM API Tutorial of Fazt"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")
    # Aquí puedes agregar cualquier código de inicialización necesario

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")
    # Aquí puedes agregar cualquier código de limpieza necesario



