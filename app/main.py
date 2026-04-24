from fastapi import FastAPI , Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

from app.routers import users

app = FastAPI(title="DressWare API")

app.include_router(users.router) 

@app.get("/")
def read_root():
    return {"message":"Đây là root"}

@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Kết nối Supabase thành công! Dữ liệu đã sẵn sàng cho AI."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi kết nối: {str(e)}"}

