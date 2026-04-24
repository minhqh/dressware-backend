import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

def get_password_hash(password: str) -> CryptContext:
    """ Hàm băm mật khẩu """ 
    return pwd_context.hash(password[:72])

def verify_password(plain_password:str, hashed_password:str) -> bool:
    """ Hàm so sánh mật khẩu đã hash """
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict) -> str:
    """Tạo JWT access token với thời gian hết hạn."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt