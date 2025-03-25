from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from services.service_auth import login, validate_token, create_access_token, get_current_user
from models.model_user import UserCreate
from models.model_auth import LoginForm, CurrentUser
from services.service_user import create_user as create_user_service

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "this_is_the_secret_key_for_seekaap"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/me", response_model=CurrentUser, status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: CurrentUser = Depends(get_current_user)):
    return current_user

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    try:
        result = await create_user_service(user)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login", status_code=status.HTTP_200_OK)
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
            "role": user.get("role", "user"),
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



