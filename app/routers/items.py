from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Item, User
from app.schemas import ItemCreate, ItemResponse
from app.auth import get_current_user

router = APIRouter(prefix="/items", tags=["Items Management"])

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate,
                db: Session = Depends(get_db), 
                current_user: User = Depends(get_current_user)
    ) -> Item:
    """ Hàm tạo và thêm đồ mới vào db """
    new_item = Item(**item.model_dump(), user_id=current_user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/", response_model=List[ItemResponse])
def get_my_item(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[Item]:
    """ Hàm lấy toàn bộ item của user hiện tại """
    items = db.query(Item).filter(
        Item.user_id == current_user.id,
        Item.deleted_at == None
    ).all()

    return items

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.user_id == current_user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy món đồ này trong tủ đồ của bạn")
    
    item.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Đã xóa món đồ thành công"}