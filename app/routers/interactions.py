from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Interaction, Item, Outfit
from app.schemas import InteractionCreate, InteractionResponse

router = APIRouter(prefix="/interactions", tags=["Interactions (Thu thập dữ liệu cho AI)"])

@router.post("/", response_model=InteractionResponse)
def log_interaction(payload: InteractionCreate, user_id: int, db: Session = Depends(get_db)):
    # 1. Kiểm tra chống mơ hồ (Không được trống cả 2, cũng không được điền cả 2)
    if (payload.item_id is None and payload.outfit_id is None) or \
       (payload.item_id is not None and payload.outfit_id is not None):
        raise HTTPException(
            status_code=400, 
            detail="Tương tác phải trỏ đến MỘT Item HOẶC MỘT Outfit (không được cả 2 hoặc rỗng)."
        )

    # 2. Kiểm tra xem Item/Outfit đó có tồn tại không (và chưa bị xóa)
    if payload.item_id:
        item = db.query(Item).filter(Item.id == payload.item_id, Item.deleted_at == None).first()
        if not item:
            raise HTTPException(status_code=404, detail="Không tìm thấy Item này.")
            
    if payload.outfit_id:
        outfit = db.query(Outfit).filter(Outfit.id == payload.outfit_id, Outfit.deleted_at == None).first()
        if not outfit:
            raise HTTPException(status_code=404, detail="Không tìm thấy Outfit này.")

    # 3. Ghi log tương tác vào DB (Tạo cạnh Graph)
    new_interaction = Interaction(
        user_id=user_id,
        item_id=payload.item_id,
        outfit_id=payload.outfit_id,
        interaction_type=payload.interaction_type
    )
    
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    
    return new_interaction