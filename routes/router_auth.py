from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from services.service_auth import login, validate_token, create_access_token
from models.model_user import UserCreate
from models.model_auth import LoginForm
from services.service_user import create_user as create_user_service

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "this_is_the_secret_key_for_seekaap"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    try:
        result = await create_user_service(user)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login")
async def login_user(login_data: LoginForm):
    try:
        user = await login(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Crear el token con más información del usuario
        token_data = {
            "sub": str(user["id"]),
            "email": user["email"],
            "username": user["username"],
            "role": user.get("role", "user"),  # Si no tiene rol, por defecto es "user"
            "is_active": user.get("is_active", True)
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "role": user.get("role", "user"),
                "is_active": user.get("is_active", True)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )



