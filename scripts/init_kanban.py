from database.database import collection_kanban_columns
import logging

logger = logging.getLogger(__name__)

async def init_kanban_columns():
    """Inicializa las columnas por defecto del Kanban"""
    try:
        # Verificar si ya existen columnas
        count = await collection_kanban_columns.count_documents({})
        if count > 0:
            logger.info("Las columnas del Kanban ya están inicializadas")
            return

        # Columnas por defecto
        default_columns = [
            {
                "title": "Por Hacer",
                "order": 1,
                "tasks": []
            },
            {
                "title": "En Progreso",
                "order": 2,
                "tasks": []
            },
            {
                "title": "En Revisión",
                "order": 3,
                "tasks": []
            },
            {
                "title": "Completado",
                "order": 4,
                "tasks": []
            }
        ]

        # Insertar columnas
        result = await collection_kanban_columns.insert_many(default_columns)
        logger.info(f"Se inicializaron {len(result.inserted_ids)} columnas del Kanban")
    except Exception as e:
        logger.error(f"Error al inicializar las columnas del Kanban: {str(e)}")
        raise 