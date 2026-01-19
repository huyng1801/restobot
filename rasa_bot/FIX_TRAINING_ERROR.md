# 🔧 RASA MODEL TRAINING ERROR - FIXED

## ❌ VẤN ĐỀ
Model training bị lỗi do **conflicting rules** khi có hai rules khác nhau predict actions khác nhau với cùng intent trigger:

```
- rule 'Confirm cancel reservation' predict action 'action_confirm_cancel_reservation'
- rule 'Confirm cancel order' predict action 'action_confirm_cancel_order'
```

Rasa không biết nên chọn action nào khi user nói "Có" (affirm).

## ✅ GIẢI PHÁP ĐÃ THỰC HIỆN

### 1. **Xóa Conflicting Rules**
- Xóa các rules confirmation vì chúng gây conflict
- Thay thế bằng **stories** (stories linh hoạt hơn rules)

### 2. **Thêm Confirmation Stories**
Stories đã thêm vào `data/stories.yml`:

```yaml
- story: cancel order
  steps:
  - intent: cancel_order
  - action: action_cancel_order
  - intent: affirm
  - action: action_confirm_cancel_order

- story: cancel order and deny
  steps:
  - intent: cancel_order
  - action: action_cancel_order
  - intent: deny
  - action: action_deny_cancellation

- story: cancel reservation
  steps:
  - intent: cancel_reservation
  - action: action_cancel_reservation
  - intent: affirm
  - action: action_confirm_cancel_reservation

- story: cancel reservation and deny
  steps:
  - intent: cancel_reservation
  - action: action_cancel_reservation
  - intent: deny
  - action: action_deny_cancellation
```

### 3. **Thêm Slots vào Domain**
Thêm vào `domain.yml`:

```yaml
pending_cancellation_reservation_id:
  type: text
  initial_value: null
  influence_conversation: true
  mappings:
  - type: custom

pending_cancellation_order_id:
  type: text
  initial_value: null
  influence_conversation: true
  mappings:
  - type: custom
```

## 📋 FILES ĐÃ THAY ĐỔI

1. **data/rules.yml**
   - ✅ Xóa conflicting confirmation rules
   - ✅ Giữ lại rules cơ bản (menu, booking, order)

2. **data/stories.yml**
   - ✅ Thêm cancel order confirmation workflows
   - ✅ Thêm cancel reservation confirmation workflows
   - ✅ Thêm deny/reject workflows

3. **domain.yml**
   - ✅ Thêm `pending_cancellation_reservation_id` slot
   - ✅ Thêm `pending_cancellation_order_id` slot

## 🚀 CÁC BƯỚC TIẾP THEO

### 1. **Train Model**
```bash
cd D:\Outsourcing\Python\Web\RestoBot\rasa_bot
rasa train --force
```

### 2. **Restart Action Server**
```bash
# Terminal mới
cd D:\Outsourcing\Python\Web\RestoBot\rasa_bot
rasa run actions
```

### 3. **Test Conversation**
```bash
# Terminal mới
cd D:\Outsourcing\Python\Web\RestoBot\rasa_bot
rasa shell
```

Test workflows:
- "Hủy đơn hàng" -> "Có"
- "Hủy đơn hàng" -> "Không"
- "Hủy đặt bàn" -> "Có"
- "Hủy đặt bàn" -> "Không"

## 💡 TẠI SAO STORIES TỐTTER RULES?

| Aspect | Rules | Stories |
|--------|-------|---------|
| **Specificity** | Rigid - phải match chính xác | Flexible - học từ examples |
| **Conflict** | Dễ conflict khi có multiple options | Rarer conflicts, NLU giúp disambiguate |
| **Maintenance** | Cắt nngắn nhưng dễ gây issue | Dài hơn nhưng rõ ràng hơn |
| **Learning** | Không học patterns | Learns dialog patterns |

## 🔍 CHẾ ĐỘ DEBUG

Nếu vẫn có lỗi, kiểm tra:

1. **Syntax validation**
```bash
rasa data validate --data data/
```

2. **Check stories
```bash
rasa data validate-stories --stories data/stories.yml
```

3. **Full verbose output**
```bash
rasa train --force -vv
```

## ✨ KỲ VỌNG SAU KHI FIX

✅ Model training thành công
✅ Chatbot can handle cancel operations smoothly
✅ Users can confirm/deny cancellations
✅ Clear user feedback cho mỗi step
✅ Proper slot management throughout flow