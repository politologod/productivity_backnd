from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database.database import collection_users
from passlib.context import CryptContext
from typing import Annotated
from models.model_user import User
from models.model_auth import CurrentUser
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de seguridad
SECRET_KEY = "this_is_the_secret_key_for_seekaap"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def login(email: str, password: str):
    try:
        # Usamos el username como email ya que OAuth2PasswordRequestForm usa username
        user = await collection_users.find_one({"email": email})
        if not user:
            return None
        if not verify_password(password, user["password"]):
            return None
        return user
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise

async def validate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Crear el objeto CurrentUser con la información del token
        current_user = CurrentUser(
            id=int(user_id),
            email=payload.get("email"),
            username=payload.get("username"),
            role=payload.get("role", "user"),
            is_active=payload.get("is_active", True)
        )
        
        return current_user
    except JWTError:
        raise credentials_exception
