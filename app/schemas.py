from pydantic import BaseModel , EmailStr ,Field
from typing import Optional
from app.models import GenderEnum ,ItemCategoryEnum ,SeasonEnum

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

# Cấu trúc cho Item được tạo
class ItemCreate(BaseModel):
    image_url: str
    category: ItemCategoryEnum
    color: Optional[str] = None
    brand: Optional[str] = None
    season: Optional[SeasonEnum] = SeasonEnum.ALL
    style_tags: Optional[list] = []

# Cấu trúc item được trả về
class ItemResponse(BaseModel):
    id: int
    user_id: int
    image_url: str
    category: ItemCategoryEnum
    color: Optional[str]
    brand: Optional[str]
    season: SeasonEnum
    style_tags: list

    class Config:
        from_attributes = True