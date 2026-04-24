import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Dữ liệu mẫu để test
test_user = {
    "username": "testuser_qa",
    "email": "qa@dressware.com",
    "password": "securepassword123",
    "gender": "MALE"
}

# Biến toàn cục để lưu Token và IDs dùng cho các bước sau
state = {
    "token": None,
    "item_id": None,
    "outfit_id": None
}
client.post("/auth/register", json=test_user)
# --- 1. TEST ĐĂNG NHẬP (Lấy Token) ---
def test_login():
    # Giả định user đã được tạo từ trước qua API register
    response = client.post("/auth/login", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    state["token"] = data["access_token"]

# --- 2. TEST TẠO ITEM MỚI ---
def test_create_item():
    headers = {"Authorization": f"Bearer {state['token']}"}
    item_data = {
        "image_url": "https://storage.supabase.com/shirt.jpg",
        "category": "TOP",
        "color": "White",
        "brand": "DressWare Original",
        "season": "SUMMER",
        "style_tags": ["minimalist", "office"]
    }
    # Lưu ý: Truyền user_id=1 để test nhanh (trong thực tế sẽ lấy từ token)
    response = client.post("/items/?user_id=1", json=item_data, headers=headers)
    assert response.status_code == 200
    state["item_id"] = response.json()["id"]

# --- 3. TEST TẠO OUTFIT & CONNECT ITEM ---
def test_outfit_workflow():
    headers = {"Authorization": f"Bearer {state['token']}"}
    
    # Tạo Outfit
    outfit_data = {"name": "Bộ đồ đi làm sáng thứ 2"}
    res_outfit = client.post("/outfits/?user_id=1", json=outfit_data, headers=headers)
    assert res_outfit.status_code == 200
    state["outfit_id"] = res_outfit.json()["id"]

    # Kết nối Item vào Outfit (Connect)
    connect_data = {"item_id": state["item_id"]}
    res_connect = client.post(
        f"/outfits/{state['outfit_id']}/add-item", 
        json=connect_data, 
        headers=headers
    )
    assert res_connect.status_code == 200
    assert res_connect.json()["message"] == "Đã thêm thành công vào bộ trang phục!"

# --- 4. TEST TƯƠNG TÁC (Interaction - Graph Edge) ---
def test_log_interaction():
    headers = {"Authorization": f"Bearer {state['token']}"}
    interaction_data = {
        "item_id": state["item_id"],
        "outfit_id": None,
        "interaction_type": "LIKE"
    }
    response = client.post("/interactions/?user_id=1", json=interaction_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["interaction_type"] == "LIKE"

# --- 5. TEST XÓA ITEM (Soft Delete) ---
def test_delete_item():
    headers = {"Authorization": f"Bearer {state['token']}"}
    response = client.delete(f"/items/{state['item_id']}", headers=headers)
    assert response.status_code == 200
    
    # Kiểm tra lại xem Item đã bị ẩn chưa
    res_get = client.get("/items/?user_id=1", headers=headers) # Giả sử lấy list của user 1
    assert res_get.status_code == 200
    items = res_get.json()
    assert all(item["id"] != state["item_id"] for item in items)