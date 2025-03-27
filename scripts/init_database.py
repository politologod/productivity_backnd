from database.database import collection_tasks, collection_users, collection_kanban_columns
from services.service_auth import get_password_hash
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def init_database():
    """Inicializa todas las colecciones de la base de datos"""
    try:
        # Inicializar usuarios
        users_count = await collection_users.count_documents({})
        if users_count == 0:
            # Crear usuario administrador por defecto
            admin_user = {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "password": get_password_hash("Admin123!"),
                "phone": "+1234567890",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            await collection_users.insert_one(admin_user)
            logger.info("Usuario administrador creado exitosamente")

        # Inicializar columnas del Kanban
        columns_count = await collection_kanban_columns.count_documents({})
        if columns_count == 0:
            # Columnas por defecto
            default_columns = [
                {
                    "id": 1,
                    "title": "Por Hacer",
                    "order": 1,
                    "tasks": [],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
                {
                    "id": 2,
                    "title": "En Progreso",
                    "order": 2,
                    "tasks": [],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
                {
                    "id": 3,
                    "title": "En Revisión",
                    "order": 3,
                    "tasks": [],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
                {
                    "id": 4,
                    "title": "Completado",
                    "order": 4,
                    "tasks": [],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            ]
            await collection_kanban_columns.insert_many(default_columns)
            logger.info(f"Se inicializaron {len(default_columns)} columnas del Kanban")

        # Inicializar tareas
        tasks_count = await collection_tasks.count_documents({})
        if tasks_count == 0:
            # Crear algunas tareas de ejemplo
            sample_tasks = [
                {
                    "id": 1,
                    "title": "Configurar el proyecto",
                    "description": "Configurar el entorno de desarrollo y las dependencias",
                    "due_date": datetime.now() + timedelta(days=7),
                    "priority": "alta",
                    "status": "pendiente",
                    "column_id": 1,
                    "created_by": 1,
                    "assigned_to": 1,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
                {
                    "id": 2,
                    "title": "Implementar autenticación",
                    "description": "Implementar el sistema de autenticación con JWT",
                    "due_date": datetime.now() + timedelta(days=14),
                    "priority": "alta",
                    "status": "en_progreso",
                    "column_id": 2,
                    "created_by": 1,
                    "assigned_to": 1,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            ]
            await collection_tasks.insert_many(sample_tasks)
            logger.info(f"Se crearon {len(sample_tasks)} tareas de ejemplo")

        logger.info("Inicialización de la base de datos completada exitosamente")

    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        raise 