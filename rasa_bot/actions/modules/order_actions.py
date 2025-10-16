"""
Order Management Actions for RestoBot
Xử lý các action liên quan đến đặt món và quản lý đơn hàng
"""
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .auth_helper import auth_helper

# URL của FastAPI backend
API_BASE_URL = "http://localhost:8000/api/v1"


class ActionAddToOrder(Action):
    """Action để thêm món vào đơn hàng"""

    def name(self) -> Text:
        return "action_add_to_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        dish_name = None
        quantity = 1 # Default quantity

        try:
            # Lấy thông tin món từ entities
            for entity in tracker.latest_message.get('entities', []):
                if entity['entity'] == 'dish_name':
                    dish_name = entity['value']
                elif entity['entity'] == 'quantity':
                    try:
                        quantity = int(entity['value'])
                    except ValueError:
                        quantity = 1 # Fallback if quantity is not a valid number
            
            if not dish_name:
                dispatcher.utter_message(text="Bạn muốn gọi món gì? Vui lòng cho tôi biết tên món ăn.")
                return []
            
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            # Tìm món trong menu để lấy ID và giá
            response = requests.get(f"{API_BASE_URL}/menu/items/search?q={dish_name}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    item = items[0]  # Lấy kết quả đầu tiên khớp
                    
                    # Lấy đơn hàng hiện tại từ slot
                    current_order = tracker.get_slot("current_order") or []
                    
                    # Thêm món vào đơn hoặc cập nhật số lượng
                    found = False
                    for existing_item in current_order:
                        if existing_item["menu_item_id"] == item["id"]:
                            existing_item["quantity"] += quantity
                            existing_item["total"] = existing_item["price"] * existing_item["quantity"]
                            found = True
                            break
                    
                    if not found:
                        order_item = {
                            "menu_item_id": item["id"],
                            "name": item["name"],
                            "price": item["price"],
                            "quantity": quantity,
                            "total": item["price"] * quantity
                        }
                        current_order.append(order_item)
                    
                    price_formatted = f"{item['price']:,.0f}đ"
                    total_formatted = f"{item['price'] * quantity:,.0f}đ"
                    
                    message = f"✅ Đã thêm **{quantity} phần {item['name']}** vào đơn hàng\n"
                    message += f"💰 Giá: {price_formatted} x {quantity} = {total_formatted}"
                    
                    dispatcher.utter_message(text=message)
                    return [SlotSet("current_order", current_order), SlotSet("last_mentioned_dish", item['name'])]
                else:
                    message = f"Xin lỗi, không tìm thấy món '{dish_name}' trong thực đơn. Bạn có thể xem thực đơn để chọn món khác."
                    dispatcher.utter_message(text=message)
                    return []
                    
            else:
                message = "Không thể tìm kiếm món ăn. Vui lòng thử lại sau."
                dispatcher.utter_message(text=message)
                return []
                
        except requests.exceptions.Timeout:
            message = "⏱️ Kết nối chậm. Vui lòng thử lại sau."
            dispatcher.utter_message(text=message)
        except requests.exceptions.RequestException as e:
            message = f"❌ Có lỗi xảy ra khi thêm món vào đơn hàng."
            print(f"Error in ActionAddToOrder: {e}")
            dispatcher.utter_message(text=message)
        except Exception as e:
            message = f"❌ Có lỗi bất ngờ xảy ra khi thêm món vào đơn hàng."
            print(f"Unexpected error in ActionAddToOrder: {e}")
            dispatcher.utter_message(text=message)
        
        return []


class ActionViewCurrentOrder(Action):
    """Action để hiển thị đơn hàng hiện tại"""

    def name(self) -> Text:
        return "action_view_current_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_order = tracker.get_slot('current_order') or []
        
        if not current_order:
            dispatcher.utter_message(text="""📝 **ĐƠN HÀNG TRỐNG**
Bạn chưa gọi món nào.

🍽️ **Bắt đầu gọi món:**
• Nói "xem thực đơn" để xem danh sách
• Nói "tôi muốn gọi [tên món]"

📋 **Ví dụ:** "Tôi muốn gọi Phở Bò""")
            return []

        order_text = "📋 **ĐƠN HÀNG HIỆN TẠI**\n\n"
        total_amount = 0.0

        for i, item in enumerate(current_order, 1):
            item_total = item.get('price', 0) * item.get('quantity', 0)
            total_amount += item_total
            
            price_formatted = f"{item.get('price', 0):,.0f}đ"
            item_total_formatted = f"{item_total:,.0f}đ"

            order_text += f"{i}. **{item.get('name', 'Món không tên')}**\n"
            order_text += f"   Số lượng: {item.get('quantity', 0)} x {price_formatted} = {item_total_formatted}\n\n"
                        
        total_amount_formatted = f"{total_amount:,.0f}đ"
        order_text += f"💰 **Tổng tiền: {total_amount_formatted}**\n\n"
        order_text += "💡 **Lựa chọn tiếp theo:**\n"
        order_text += "• Nói 'xác nhận đơn hàng' để hoàn tất\n"
        order_text += "• Nói 'thêm món [tên món]' để gọi thêm\n"
        order_text += "• Nói 'xóa món [tên món]' để bỏ món"

        dispatcher.utter_message(text=order_text)
        return []


class ActionConfirmOrder(Action):
    """Action để xác nhận đơn hàng"""

    def name(self) -> Text:
        return "action_confirm_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_order = tracker.get_slot('current_order') or []
        
        if not current_order:
            dispatcher.utter_message(text="📝 Bạn chưa có món nào trong đơn hàng. Vui lòng gọi món trước khi xác nhận.")
            return []

        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            # Tạo đơn hàng qua API
            order_data = {
                "customer_name": "Khách hàng chatbot",
                "customer_phone": "0000000000",
                "items": [
                    {
                        "menu_item_id": item["menu_item_id"],
                        "quantity": item["quantity"],
                        "special_instructions": ""
                    }
                    for item in current_order
                ],
                "special_requests": ""
            }
            
            response = requests.post(
                f"{API_BASE_URL}/orders/",
                headers=headers,
                json=order_data,
                timeout=10
            )
            
            if response.status_code == 201:
                order_info = response.json()
                total_amount = sum(item.get('price', 0) * item.get('quantity', 0) for item in current_order)
                
                confirmation_message = f"""✅ **ĐƠN HÀNG ĐÃ ĐƯỢC XÁC NHẬN**

📋 **Mã đơn hàng:** #{order_info.get('id', 'N/A')}
💰 **Tổng tiền:** {total_amount:,.0f}đ
⏱️ **Thời gian chuẩn bị:** 15-30 phút

📞 **Lưu ý:** 
• Đơn hàng sẽ được chuyển vào bếp ngay
• Bạn có thể theo dõi tiến độ qua mã đơn hàng
• Liên hệ: 0901234567 nếu cần hỗ trợ

🍽️ Cảm ơn bạn đã sử dụng dịch vụ!"""
                
                dispatcher.utter_message(text=confirmation_message)
                
                # Clear current order and store order ID
                return [
                    SlotSet("current_order", []),
                    SlotSet("last_order_id", order_info.get('id'))
                ]
                
            else:
                dispatcher.utter_message(text=f"❌ Không thể xác nhận đơn hàng lúc này. Vui lòng thử lại sau. (Mã lỗi: {response.status_code})")

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý đơn hàng... Vui lòng đợi.")
        except requests.exceptions.RequestException as e:
            print(f"Order confirmation error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi hệ thống khi xác nhận đơn hàng. Vui lòng liên hệ nhân viên: 0123-456-789.")
        except Exception as e:
            print(f"Unexpected order confirmation error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi bất ngờ khi xác nhận đơn hàng. Vui lòng liên hệ nhân viên: 0123-456-789.")

        return []


class ActionCancelOrder(Action):
    """Action để hủy đơn hàng"""

    def name(self) -> Text:
        return "action_cancel_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_order = tracker.get_slot('current_order') or []
        last_order_id = tracker.get_slot('last_order_id')
        
        if current_order:
            # Hủy đơn hàng chưa xác nhận (chỉ xóa khỏi slot)
            dispatcher.utter_message(text="""🗑️ **ĐÃ HỦY ĐƠN HÀNG**

Đã xóa tất cả món khỏi đơn hàng hiện tại.

🔄 **Để bắt đầu lại:**
• Nói "xem thực đơn" để chọn món mới
• Hoặc nói trực tiếp "tôi muốn gọi [tên món]" """)
            
            return [SlotSet("current_order", [])]
            
        elif last_order_id:
            # Hủy đơn hàng đã xác nhận qua API
            try:
                headers = auth_helper.get_headers()
                if not headers.get("Authorization"):
                    dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                    return []

                response = requests.delete(f"{API_BASE_URL}/orders/{last_order_id}", headers=headers, timeout=5)
                
                if response.status_code == 200:
                    dispatcher.utter_message(text=f"""✅ **ĐÃ HỦY ĐƠN HÀNG THÀNH CÔNG**

Đơn hàng #{last_order_id} đã được hủy.

💰 **Hoàn tiền:** Sẽ được xử lý trong 1-3 ngày làm việc
📞 **Xác nhận:** Nhân viên có thể gọi lại để xác nhận

🔄 **Đặt mới:** Nói "xem thực đơn" để bắt đầu lại""")
                    
                    return [SlotSet("last_order_id", None)]
                    
                elif response.status_code == 404:
                    dispatcher.utter_message(text=f"❌ Không tìm thấy đơn hàng #{last_order_id}. Có thể đã được hủy trước đó.")
                else:
                    dispatcher.utter_message(text="❌ Không thể hủy đơn hàng lúc này. Vui lòng liên hệ nhân viên.")

            except requests.exceptions.Timeout:
                dispatcher.utter_message(text="⏱️ Kết nối chậm. Vui lòng thử lại sau.")
            except requests.exceptions.RequestException as e:
                print(f"Cancel order error: {e}")
                dispatcher.utter_message(text="🔧 Lỗi hệ thống khi hủy đơn hàng. Vui lòng liên hệ nhân viên.")
            except Exception as e:
                print(f"Unexpected cancel order error: {e}")
                dispatcher.utter_message(text="🔧 Lỗi bất ngờ khi hủy đơn hàng. Vui lòng liên hệ nhân viên.")
                
        else:
            dispatcher.utter_message(text="""ℹ️ **KHÔNG CÓ ĐƠN HÀNG ĐỂ HỦY**

Bạn không có đơn hàng nào đang chờ xử lý.

📋 **Để đặt món mới:**
• Nói "xem thực đơn"
• Hoặc "tôi muốn gọi [tên món]" """)

        return []