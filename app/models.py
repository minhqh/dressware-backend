import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base

# --- ENUMS ---
class GenderEnum(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNISEX = "UNISEX"
    OTHER = "OTHER"

class SeasonEnum(enum.Enum):
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    AUTUMN = "AUTUMN"
    WINTER = "WINTER"
    ALL = "ALL"

class InteractionEnum(enum.Enum):
    VIEW = "VIEW"
    LIKE = "LIKE"
    WEAR = "WEAR"
    ADD_TO_OUTFIT = "ADD_TO_OUTFIT"
    SHARE = "SHARE"

class ItemCategoryEnum(enum.Enum):
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    OUTERWEAR = "OUTERWEAR"
    FOOTWEAR = "FOOTWEAR"
    ACCESSORY = "ACCESSORY"
    ONE_PIECE = "ONE_PIECE"

# --- CORE MODELS ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    gender = Column(Enum(GenderEnum))
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True) 

    items = relationship("Item", back_populates="owner")
    outfits = relationship("Outfit", back_populates="owner")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String, nullable=False)
    category = Column(Enum(ItemCategoryEnum), nullable=False)
    color = Column(String(30))
    brand = Column(String(50))
    season = Column(Enum(SeasonEnum), default=SeasonEnum.ALL)
    style_tags = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True) 

    owner = relationship("User", back_populates="items")
    outfit_links = relationship("OutfitItem", back_populates="item")

class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True) 

    owner = relationship("User", back_populates="outfits")
    item_links = relationship("OutfitItem", back_populates="outfit")

class OutfitItem(Base):
    __tablename__ = "outfit_items"

    outfit_id = Column(Integer, ForeignKey("outfits.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    outfit = relationship("Outfit", back_populates="item_links")
    item = relationship("Item", back_populates="outfit_links")

# --- GRAPH EDGES MODEL ---
class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True, index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True)
    interaction_type = Column(Enum(InteractionEnum), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "(item_id IS NOT NULL AND outfit_id IS NULL) OR "
            "(item_id IS NULL AND outfit_id IS NOT NULL)",
            name="check_interaction_target"
        ),
    )