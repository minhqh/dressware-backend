from pydantic import BaseModel , EmailStr ,Field
from typing import Optional
from app.models import GenderEnum

# Cấu trúc khi user đăng ký
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., max_length=72, description="Bcrypt giới hạn tối đa 72 ký tự")
    gender: Optional[GenderEnum] = None

# Dữ liệu trả về user
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

# Cấu trúc khi đăng nhập thành công
class Token(BaseModel):
    access_token: str
    token_type: str
