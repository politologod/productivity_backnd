from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from services.service_auth import (
    login as login_service,
    get_current_user,
    create_access_token
)
from models.model_auth import LoginForm, CurrentUser
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "No encontrado"}}
)

@router.post(
    "/login",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Inicia sesión y devuelve un token de acceso",
    responses={
        200: {
            "description": "Login exitoso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Credenciales inválidas",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Credenciales incorrectas"
                    }
                }
            }
        }
    }
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await login_service(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        
        access_token = create_access_token(
            data={"sub": str(user["id"]), "email": user["email"]}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/me",
    response_model=CurrentUser,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario actual",
    description="Obtiene la información del usuario autenticado",
    responses={
        200: {
            "description": "Usuario obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "usuario@ejemplo.com",
                        "username": "usuario",
                        "role": "user",
                        "is_active": True
                    }
                }
            }
        }
    }
)
async def get_current_user_info(current_user: CurrentUser = Depends(get_current_user)):
    return current_user 