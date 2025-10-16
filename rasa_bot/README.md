# 🤖 RestoBot - Rasa Chatbot# RestoBot - Rasa Chatbot



**Trợ lý ảo tiếng Việt cho nhà hàng**  ## Cài đặt Rasa

Vietnamese Conversational AI powered by Rasa

1. **Tạo virtual environment riêng cho Rasa:**

## 🚀 Quick Start```bash

cd rasa_bot

### 1. Cài đặt môi trường Rasapython -m venv rasa_env

# Windows

```bashrasa_env\Scripts\activate

# Di chuyển vào thư mục rasa_bot# Linux/Mac

cd rasa_botsource rasa_env/bin/activate

```

# Tạo virtual environment riêng cho Rasa (khuyến nghị)

python -m venv rasa_env2. **Cài đặt dependencies:**

```bash

# Kích hoạt environmentpip install -r requirements.txt

# Windows```

rasa_env\Scripts\activate

# Linux/macOS## Huấn luyện model

source rasa_env/bin/activate

```bash

# Cài đặt Rasa và dependencies# Huấn luyện model

pip install rasa==3.6.13rasa train

pip install rasa-sdk==3.6.2

pip install requests# Kiểm tra độ chính xác

```rasa test

```

### 2. Huấn luyện Model

## Chạy Rasa

```bash

# Huấn luyện Rasa model với dữ liệu tiếng Việt1. **Chạy Rasa server:**

rasa train```bash

rasa run --enable-api --cors "*" --port 5005

# Kiểm tra độ chính xác model```

rasa test

2. **Chạy action server (terminal khác):**

# Đánh giá cross-validation (tùy chọn)```bash

rasa test nlu --cross-validationrasa run actions --port 5055

``````



### 3. Chạy Rasa Services## Test chatbot



#### Terminal 1 - Rasa Server1. **Test trong terminal:**

```bash```bash

# Khởi động Rasa server với APIrasa shell

rasa run --enable-api --cors "*" --port 5005```

```

2. **Test qua API:**

#### Terminal 2 - Action Server```bash

```bashcurl -X POST http://localhost:5005/webhooks/rest/webhook \

# Khởi động custom actions server  -H "Content-Type: application/json" \

rasa run actions --port 5055  -d '{"sender": "test", "message": "xin chào"}'

``````



### 4. Test Chatbot## Cấu trúc dữ liệu



#### A. Test trong Terminal### Intents được support:

```bash- **greet, goodbye**: Chào hỏi, tạm biệt

# Chat trực tiếp trong terminal- **book_table**: Đặt bàn cho số người, thời gian

rasa shell- **view_menu**: Xem thực đơn

```- **order_food, add_to_order**: Gọi món, thêm món

- **ask_dish_details, ask_dish_price**: Hỏi chi tiết, giá món

#### B. Test qua API- **ask_opening_hours, ask_address, ask_contact**: Thông tin nhà hàng  

```bash- **ask_promotions**: Khuyến mãi

# Test với curl- **recommend_dishes, ask_popular_dishes**: Gợi ý món

curl -X POST http://localhost:5005/webhooks/rest/webhook \

  -H "Content-Type: application/json" \### Entities được trích xuất:

  -d '{- **number_of_people**: Số người đặt bàn

    "sender": "test_user",- **date, time**: Ngày, giờ đặt bàn

    "message": "xin chào"- **dish_name**: Tên món ăn

  }'- **quantity**: Số lượng món



# Test với Python### Chức năng chính:

python -c "- ✅ Đặt bàn với xác nhận thông tin

import requests- ✅ Xem thực đơn theo danh mục

resp = requests.post('http://localhost:5005/webhooks/rest/webhook', - ✅ Gọi món và quản lý đơn hàng

                    json={'sender': 'test', 'message': 'xin chào'})- ✅ Hỏi thông tin chi tiết món ăn

print(resp.json())- ✅ Gợi ý món phổ biến/đặc biệt

"- ✅ Trả lời thông tin nhà hàng

```- ✅ Quản lý ngữ cảnh hội thoại



## 📊 Cấu trúc dữ liệu## Tích hợp với FastAPI



### Intents được hỗ trợ:Chatbot sẽ gọi các API endpoint:

- **🗣️ Chào hỏi**: `greet`, `goodbye` - Chào hỏi, tạm biệt- `/api/v1/menu/categories/` - Lấy danh mục

- **🪑 Đặt bàn**: `book_table`, `ask_available_tables`, `cancel_reservation`- `/api/v1/menu/items/` - Lấy món ăn

- **🍽️ Xem menu**: `view_menu`, `ask_menu_categories`, `ask_featured_dishes`- `/api/v1/tables/available` - Kiểm tra bàn trống

- **🍜 Gọi món**: `order_food`, `add_to_order`, `view_current_order`, `confirm_order`- `/api/v1/orders/reservations/` - Đặt bàn

- **💰 Hỏi giá**: `ask_dish_price`, `ask_dish_details`- `/api/v1/orders/orders/` - Tạo đơn hàng
- **ℹ️ Thông tin**: `ask_opening_hours`, `ask_address`, `ask_contact`, `ask_promotions`
- **🎯 Gợi ý**: `recommend_dishes`, `ask_popular_dishes`, `ask_special_dishes`

### Entities được trích xuất:
- **👥 number_of_people**: Số người đặt bàn (1-20)
- **📅 date**: Ngày đặt bàn ("hôm nay", "ngày mai", "thứ 7")
- **🕐 time**: Giờ đặt bàn ("7 giờ tối", "19:30")
- **🍽️ dish_name**: Tên món ăn ("phở bò", "cà phê sữa đá")
- **🔢 quantity**: Số lượng món (1-10)
- **🪑 table_type**: Loại bàn ("VIP", "gần cửa sổ")
- **📍 location**: Vị trí bàn ("tầng 1", "sân vườn")

### Slots quản lý trạng thái:
- **number_of_people**: Lưu số người đặt bàn
- **reservation_date**: Ngày đặt bàn
- **reservation_time**: Giờ đặt bàn
- **table_type**: Loại bàn yêu cầu
- **current_order**: Đơn hàng hiện tại (list)
- **last_mentioned_dish**: Món ăn vừa nhắc đến

## 🎯 Chức năng chính

### ✅ Đặt bàn thông minh
```
User: "Tôi muốn đặt bàn cho 4 người tối nay 7 giờ"
Bot:  "Tôi sẽ đặt bàn cho 4 người vào lúc 7 giờ tối hôm nay. Bạn có xác nhận không?"
User: "Có"
Bot:  "Đã đặt bàn thành công! Mã đặt bàn: #RB001"
```

### ✅ Xem thực đơn theo danh mục
```
User: "Cho tôi xem thực đơn"
Bot:  "🍽️ THỰC ĐƠN NHÀ HÀNG
       📂 Món chính:
       • Phở Bò Tái - 85,000đ
       • Bún Bò Huế - 90,000đ
       ..."
```

### ✅ Gọi món và quản lý đơn hàng
```
User: "Tôi muốn gọi 2 phần phở bò"
Bot:  "Đã thêm 2 phần Phở Bò Tái vào đơn hàng. Bạn có muốn gọi thêm món nào không?"
User: "Xem đơn hàng hiện tại"
Bot:  "Đơn hàng của bạn: 2x Phở Bò Tái - 170,000đ"
```

### ✅ Hỏi thông tin chi tiết
```
User: "Phở bò có gì?"
Bot:  "Phở Bò Tái: Phở bò truyền thống với thịt bò tái, nước dùng được ninh từ xương bò..."
User: "Giá bao nhiêu?"
Bot:  "Phở Bò Tái có giá 85,000đ"
```

### ✅ Gợi ý món ăn
```
User: "Gợi ý món ngon"
Bot:  "Những món được yêu thích nhất:
       🌟 Phở Bò Tái - Đặc sản nhà hàng
       🌟 Bún Bò Huế - Cay nồng đậm đà"
```

## 🔧 Custom Actions

### Actions tích hợp với FastAPI Backend:
- **action_show_menu**: Lấy thực đơn từ database
- **action_show_available_tables**: Kiểm tra bàn trống
- **action_book_table**: Đặt bàn thông qua API
- **action_add_to_order**: Thêm món vào đơn hàng
- **action_show_current_order**: Hiển thị đơn hàng hiện tại
- **action_confirm_order**: Xác nhận và lưu đơn hàng
- **action_show_popular_dishes**: Lấy món phổ biến
- **action_ask_dish_details**: Chi tiết món ăn từ database

### Authentication với Backend:
- Tự động login với admin credentials
- Refresh token khi hết hạn
- Fallback graceful khi backend offline

## 📈 Training Data (Vietnamese)

### Ví dụ training data:
```yaml
- intent: book_table
  examples: |
    - tôi muốn đặt bàn
    - đặt bàn cho [2](number_of_people) người
    - đặt bàn [hôm nay](date) lúc [7 giờ tối](time)
    - tôi cần bàn [VIP](table_type)

- intent: view_menu
  examples: |
    - xem thực đơn
    - cho tôi xem menu
    - có món gì
    - thực đơn như thế nào

- intent: order_food
  examples: |
    - tôi muốn gọi [phở bò](dish_name)
    - cho tôi [2](quantity) phần [bò bít tết](dish_name)
    - gọi [1](quantity) ly [cà phê](dish_name)
```

## 🔧 Configuration

### config.yml - NLP Pipeline:
```yaml
language: vi  # Vietnamese language support

pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
    constrain_similarities: true
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100
  - name: FallbackClassifier
    threshold: 0.3
```

### endpoints.yml - Service Connections:
```yaml
action_endpoint:
  url: "http://localhost:5055/webhook"  # Custom actions

rest:
  url: "http://localhost:5005/webhooks/rest/webhook"  # REST API
```

## 🚀 Tích hợp với RestoBot System

### Khi chạy từ main system:
```bash
# Từ root directory
python restobot.py  # Tự động start Rasa + Actions
```

### Manual testing trong development:
```bash
# Terminal 1: Actions server
cd rasa_bot
rasa run actions

# Terminal 2: Rasa server  
rasa run --enable-api

# Terminal 3: Test
rasa shell
```

## 📊 Performance Tuning

### Optimized Settings:
- **DIETClassifier epochs**: 100 (balance accuracy/training time)
- **Fallback threshold**: 0.3 (reduce false positives)
- **Character n-grams**: 1-4 (good for Vietnamese)
- **Memory**: ~300MB per model

### Training Tips:
- Thêm nhiều biến thể câu hỏi tiếng Việt
- Sử dụng synonyms cho entities
- Regular retraining với real user data
- Cross-validation để tránh overfitting

## 🐛 Troubleshooting

### Common Issues:
1. **Training fails**: Kiểm tra YAML syntax trong data files
2. **Actions không connect**: Verify port 5055 available
3. **Vietnamese không hiểu**: Thêm training examples
4. **Memory issues**: Giảm epochs hoặc tăng RAM

### Debug Commands:
```bash
# Kiểm tra model components
rasa test nlu --model models/

# Debug conversation flow
rasa run --debug

# Validate training data
rasa data validate
```

## 📚 Resources

- **Rasa Documentation**: https://rasa.com/docs/
- **Vietnamese NLP**: Custom tokenization for Vietnamese
- **Training Best Practices**: Iterative improvement workflow
- **Production Deployment**: Docker-ready configuration

---

**Vietnamese Chatbot**: Restaurant Virtual Assistant  
**Powered by**: Rasa 3.6.13 + Custom Actions  
**Language**: Vietnamese (Tiếng Việt) + Fallback English