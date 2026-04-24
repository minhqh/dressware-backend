from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token
from app.auth import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)) -> User:
    """ Hàm kiểm tra tồn tại email/username đồng thời tạo mới user và thêm vào db"""
    # Kiểm tra trùng tên username hoặc email
    user_exists = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()

    if user_exists:
        raise HTTPException(status_code=400, detail="Username hoặc Email đã tồn tại")
    
    hashed_pw = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw,
        gender=user.gender
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    """ Hàm lấy vào user, kiểm tra tồn tại/ sai thông tin và tạo token mới"""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(plain_password=form_data.password ,hashed_password= user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
