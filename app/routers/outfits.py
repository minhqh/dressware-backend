from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Outfit, OutfitItem, Item
from app.schemas import OutfitCreate, OutfitResponse, OutfitItemAdd

router = APIRouter(prefix="/outfits", tags=["Outfit: Bộ trang phục"])

# Tạo bộ trang phục mới
@router.post("/", response_model=OutfitResponse)
def create_outfit(outfit: OutfitCreate, user_id: int, db: Session = Depends(get_db)) -> Outfit:
    """ Hàm tạo bộ trang phục """
    new_outfit = Outfit(name=outfit.name, user_id= user_id)
    db.add(new_outfit)
    db.commit()
    db.refresh(new_outfit)
    return new_outfit

# Lấy danh sách các bộ đồ
@router.get("/", response_model=list[OutfitResponse])
def get_user_outfits(user_id: int, db: Session = Depends(get_db)) -> list[Outfit]:
    outfits = db.query(Outfit).filter(
        Outfit.user_id == user_id,
        Outfit.deleted_at == None
    ).all()

    return outfits

# Thêm item vào outfit
@router.post("/{outfit_id}/add-item")
def add_item_to_outfit(outfit_id: int, payload: OutfitItemAdd, db: Session = Depends(get_db)):
    """ Hàm kiểm tra item, outfit và tồn tại item trong outfit chưa,xong thì tạo link giữa item và outfit"""
    # Kiểm tra item còn tồn tại không 
    item = db.query(Item).filter(Item.id == payload.item_id, Item.deleted_at == None).first()
    if not item :
        raise HTTPException(status_code=404, detail="Không tìm thấy món đồ này")
    
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.deleted_at == None).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ trang phục này")
    
    existing_link = db.query(OutfitItem).filter_by(outfit_id=outfit_id, item_id=payload.item_id).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="Món đồ này đã có trong bộ trang phục")
    
    new_link = OutfitItem(outfit_id=outfit_id, item_id=payload.item_id)
    db.add(new_link)
    db.commit()
    
    return {"message": "Đã thêm thành công vào bộ trang phục!"}