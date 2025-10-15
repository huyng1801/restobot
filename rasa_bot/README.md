# RestoBot - Rasa Chatbot

## Cài đặt Rasa

1. **Tạo virtual environment riêng cho Rasa:**
```bash
cd rasa_bot
python -m venv rasa_env
# Windows
rasa_env\Scripts\activate
# Linux/Mac
source rasa_env/bin/activate
```

2. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

## Huấn luyện model

```bash
# Huấn luyện model
rasa train

# Kiểm tra độ chính xác
rasa test
```

## Chạy Rasa

1. **Chạy Rasa server:**
```bash
rasa run --enable-api --cors "*" --port 5005
```

2. **Chạy action server (terminal khác):**
```bash
rasa run actions --port 5055
```

## Test chatbot

1. **Test trong terminal:**
```bash
rasa shell
```

2. **Test qua API:**
```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "test", "message": "xin chào"}'
```

## Cấu trúc dữ liệu

### Intents được support:
- **greet, goodbye**: Chào hỏi, tạm biệt
- **book_table**: Đặt bàn cho số người, thời gian
- **view_menu**: Xem thực đơn
- **order_food, add_to_order**: Gọi món, thêm món
- **ask_dish_details, ask_dish_price**: Hỏi chi tiết, giá món
- **ask_opening_hours, ask_address, ask_contact**: Thông tin nhà hàng  
- **ask_promotions**: Khuyến mãi
- **recommend_dishes, ask_popular_dishes**: Gợi ý món

### Entities được trích xuất:
- **number_of_people**: Số người đặt bàn
- **date, time**: Ngày, giờ đặt bàn
- **dish_name**: Tên món ăn
- **quantity**: Số lượng món

### Chức năng chính:
- ✅ Đặt bàn với xác nhận thông tin
- ✅ Xem thực đơn theo danh mục
- ✅ Gọi món và quản lý đơn hàng
- ✅ Hỏi thông tin chi tiết món ăn
- ✅ Gợi ý món phổ biến/đặc biệt
- ✅ Trả lời thông tin nhà hàng
- ✅ Quản lý ngữ cảnh hội thoại

## Tích hợp với FastAPI

Chatbot sẽ gọi các API endpoint:
- `/api/v1/menu/categories/` - Lấy danh mục
- `/api/v1/menu/items/` - Lấy món ăn
- `/api/v1/tables/available` - Kiểm tra bàn trống
- `/api/v1/orders/reservations/` - Đặt bàn
- `/api/v1/orders/orders/` - Tạo đơn hàng