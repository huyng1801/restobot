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

        # Import auth functions
        from .auth_helper import get_authenticated_user_from_tracker, get_auth_headers_from_tracker
        
        # Lấy thông tin user đã xác thực từ tracker
        authenticated_user = get_authenticated_user_from_tracker(tracker)
        
        # Nếu không có user đã xác thực, yêu cầu đăng nhập
        if not authenticated_user:
            dispatcher.utter_message(text="""🔐 **ĐĂNG NHẬP YÊU CẦU**
            
Để gọi món, bạn cần đăng nhập vào hệ thống.

📱 **Các bước:**
1. Nhấn **"Đăng nhập"** ở góc trên
2. Nhập tài khoản và mật khẩu
3. Quay lại chat để gọi món

💡 **Tại sao cần đăng nhập?**
• Lưu đơn hàng của bạn
• Xem lịch sử đặt món
• Nhận ưu đãi đặc biệt

🚀 Sau khi đăng nhập, hãy thử lại: "Tôi muốn gọi [tên món]" """)
            return []

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

            # Kiểm tra user có reservation active không
            user_id = authenticated_user.get('id') or authenticated_user.get('user_id')
            
            # Sử dụng auth headers từ user token  
            headers = get_auth_headers_from_tracker(tracker)
            reservations_response = requests.get(
                f"{API_BASE_URL}/orders/reservations/?status=CONFIRMED", 
                headers=headers, 
                timeout=5
            )
            
            active_reservation = None
            if reservations_response.status_code == 200:
                reservations_data = reservations_response.json()
                reservations = reservations_data.get('items', []) if isinstance(reservations_data, dict) else reservations_data
                
                # Tìm reservation của user hiện tại và còn active
                from datetime import datetime, date
                today = date.today()
                
                for reservation in reservations:
                    if (reservation.get('user_id') == user_id and 
                        reservation.get('status') == 'CONFIRMED'):
                        # Kiểm tra ngày đặt bàn có phải hôm nay không
                        reservation_date = reservation.get('reservation_date')
                        if reservation_date and str(reservation_date) == str(today):
                            active_reservation = reservation
                            break
            
            if not active_reservation:
                dispatcher.utter_message(text="""🍽️ **CẦN ĐẶT BÀN TRƯỚC KHI GỌI MÓN**
                
Để gọi món, bạn cần đặt bàn trước.

📋 **Các bước:**
1. Nói **"đặt bàn"** để đặt chỗ
2. Chọn thời gian và số người  
3. Sau khi có bàn, hãy quay lại gọi món

💡 **Ví dụ:** "Tôi muốn đặt bàn 4 người lúc 7h tối"

🔄 Sau khi đặt bàn xong, bạn có thể nói: "Tôi muốn gọi [tên món]" """)
                return []

            # Tìm món trong menu để lấy ID và giá
            response = requests.get(f"{API_BASE_URL}/menu/items/search?q={dish_name}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    item = items[0]  # Lấy kết quả đầu tiên khớp
                    table_id = active_reservation.get('table_id')
                    
                    # Kiểm tra xem đã có order cho bàn này chưa
                    current_order_id = tracker.get_slot("current_order_id")
                    order_response = None
                    
                    if current_order_id:
                        # Kiểm tra order hiện tại có tồn tại không
                        order_response = requests.get(f"{API_BASE_URL}/orders/orders/{current_order_id}", headers=headers, timeout=5)
                    
                    if not current_order_id or (order_response and order_response.status_code != 200):
                        # Tạo order mới cho bàn này
                        order_data = {
                            "table_id": table_id,
                            "notes": f"Đơn hàng cho bàn {table_id} - Từ chatbot",
                            "order_items": []
                        }
                        
                        create_order_response = requests.post(
                            f"{API_BASE_URL}/orders/orders/",
                            headers=headers,
                            json=order_data,
                            timeout=10
                        )
                        
                        if create_order_response.status_code == 201:
                            order_info = create_order_response.json()
                            current_order_id = order_info.get('id')
                        else:
                            dispatcher.utter_message(text="❌ Không thể tạo đơn hàng. Vui lòng thử lại sau.")
                            return []
                    
                    # Thêm món vào order
                    add_item_data = {
                        "menu_item_id": item["id"],
                        "quantity": quantity,
                        "special_instructions": ""
                    }
                    
                    add_item_response = requests.post(
                        f"{API_BASE_URL}/orders/orders/{current_order_id}/items/",
                        headers=headers,
                        json=add_item_data,
                        timeout=10
                    )
                    
                    if add_item_response.status_code in [200, 201]:
                        price_formatted = f"{item['price']:,.0f}đ"
                        total_formatted = f"{item['price'] * quantity:,.0f}đ"
                        table_number = active_reservation.get('table', {}).get('number', table_id)
                        
                        message = f"✅ **ĐÃ THÊM MÓN VÀO ĐƠN HÀNG**\n\n"
                        message += f"🍽️ **Món:** {item['name']}\n"
                        message += f"📊 **Số lượng:** {quantity} phần\n"
                        message += f"💰 **Giá:** {price_formatted} x {quantity} = {total_formatted}\n"
                        message += f"🪑 **Bàn:** {table_number}\n\n"
                        message += f"💡 **Tiếp theo:**\n"
                        message += f"• Gọi thêm món: 'Tôi muốn thêm [tên món]'\n"
                        message += f"• Xem đơn hàng: 'Xem đơn hàng'\n"
                        message += f"• Xác nhận: 'Xác nhận đơn hàng'"
                        
                        dispatcher.utter_message(text=message)
                        return [
                            SlotSet("current_order_id", current_order_id),
                            SlotSet("last_mentioned_dish", item['name']),
                            SlotSet("active_table_id", table_id)
                        ]
                    else:
                        dispatcher.utter_message(text="❌ Không thể thêm món vào đơn hàng. Vui lòng thử lại sau.")
                        return []
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


class ActionRemoveFromOrder(Action):
    """Action để xóa món khỏi đơn hàng"""

    def name(self) -> Text:
        return "action_remove_from_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_order = tracker.get_slot('current_order') or []
        dish_name = None
        
        # Lấy tên món từ entity
        for entity in tracker.latest_message.get('entities', []):
            if entity['entity'] == 'dish_name':
                dish_name = entity['value']
                break
        
        # Nếu không có entity, lấy từ slot last_mentioned_dish
        if not dish_name:
            dish_name = tracker.get_slot('last_mentioned_dish')
        
        if not dish_name:
            dispatcher.utter_message(text="Bạn muốn xóa món nào? Vui lòng cho tôi biết tên món ăn.")
            return []
            
        if not current_order:
            dispatcher.utter_message(text="Đơn hàng của bạn đang trống. Không có món nào để xóa.")
            return []
        
        # Tìm và xóa món
        updated_order = []
        removed_item = None
        
        for item in current_order:
            if dish_name.lower() in item.get('name', '').lower():
                removed_item = item
                # Không thêm vào updated_order (xóa món)
            else:
                updated_order.append(item)
        
        if removed_item:
            price_formatted = f"{removed_item.get('price', 0):,.0f}đ"
            message = f"✅ Đã xóa **{removed_item.get('name')}** khỏi đơn hàng"
            
            if updated_order:
                # Tính lại tổng tiền
                total_amount = sum(item.get('price', 0) * item.get('quantity', 0) for item in updated_order)
                message += f"\n💰 **Tổng còn lại:** {total_amount:,.0f}đ"
                message += "\n\n💡 Nói 'xem đơn hàng' để kiểm tra lại"
            else:
                message += "\n📝 **Đơn hàng hiện tại trống**"
                message += "\n💡 Nói 'xem thực đơn' để gọi món mới"
                
            dispatcher.utter_message(text=message)
            return [SlotSet("current_order", updated_order)]
        else:
            # Hiển thị danh sách món có trong đơn để khách chọn
            if current_order:
                order_list = "❌ **Không tìm thấy món** `" + dish_name + "` **trong đơn hàng**\n\n"
                order_list += "📋 **Các món hiện có:**\n"
                for i, item in enumerate(current_order, 1):
                    order_list += f"{i}. {item.get('name', 'Món không tên')} (x{item.get('quantity', 1)})\n"
                order_list += "\n💡 **Bạn có thể nói:** 'Xóa món [tên món chính xác]'"
                
                dispatcher.utter_message(text=order_list)
            else:
                dispatcher.utter_message(text=f"Không tìm thấy món '{dish_name}' trong đơn hàng.")
                
            return []


class ActionViewCurrentOrder(Action):
    """Action để hiển thị đơn hàng hiện tại"""

    def name(self) -> Text:
        return "action_view_current_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract user info from metadata
        user_info = None
        latest_message = tracker.latest_message
        if latest_message and 'metadata' in latest_message and latest_message['metadata']:
            user_info = latest_message['metadata'].get('user_info', {})
        
        if not user_info or not user_info.get('user_id'):
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để xem đơn hàng của bạn.")
            return []
        
        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []
            
            # Lấy order hiện tại từ slot hoặc tìm order active
            current_order_id = tracker.get_slot("current_order_id")
            
            if not current_order_id:
                dispatcher.utter_message(text="""📝 **CHƯA CÓ ĐƠN HÀNG**
Bạn chưa gọi món nào.

🍽️ **Bắt đầu gọi món:**
• Đặt bàn trước: "Tôi muốn đặt bàn"
• Sau đó gọi món: "Tôi muốn gọi [tên món]"

📋 **Ví dụ:** "Tôi muốn gọi Phở Bò" """)
                return []
            
            # Lấy thông tin order từ API
            response = requests.get(f"{API_BASE_URL}/orders/orders/{current_order_id}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                order_info = response.json()
                
                if not order_info.get('order_items'):
                    dispatcher.utter_message(text="""📝 **ĐƠN HÀNG TRỐNG**
Đơn hàng hiện tại chưa có món nào.

🍽️ **Gọi món:** "Tôi muốn gọi [tên món]" """)
                    return []

                table_id = order_info.get('table_id', 'N/A')
                order_text = f"📋 **ĐƠN HÀNG HIỆN TẠI** (Bàn {table_id})\n\n"
                total_amount = 0.0

                for i, item in enumerate(order_info['order_items'], 1):
                    menu_item = item.get('menu_item', {})
                    quantity = item.get('quantity', 0)
                    unit_price = item.get('unit_price', 0)
                    subtotal = item.get('subtotal', 0)
                    total_amount += subtotal
                    
                    price_formatted = f"{unit_price:,.0f}đ"
                    subtotal_formatted = f"{subtotal:,.0f}đ"

                    order_text += f"{i}. **{menu_item.get('name', 'Món không tên')}**\n"
                    order_text += f"   Số lượng: {quantity} x {price_formatted} = {subtotal_formatted}\n"
                    if item.get('special_instructions'):
                        order_text += f"   📝 Ghi chú: {item['special_instructions']}\n"
                    order_text += "\n"
                                
                total_amount_formatted = f"{total_amount:,.0f}đ"
                order_text += f"💰 **Tổng tiền: {total_amount_formatted}**\n\n"
                order_text += "💡 **Lựa chọn tiếp theo:**\n"
                order_text += "• Gọi thêm món: 'Tôi muốn thêm [tên món]'\n"
                order_text += "• Xác nhận: 'Xác nhận đơn hàng'\n"
                order_text += "• Hủy: 'Hủy đơn hàng'"

                dispatcher.utter_message(text=order_text)
            else:
                dispatcher.utter_message(text="❌ Không thể tải thông tin đơn hàng. Vui lòng thử lại sau.")
        
        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Vui lòng thử lại sau.")
        except Exception as e:
            print(f"Error in ActionViewCurrentOrder: {e}")
            dispatcher.utter_message(text="❌ Có lỗi xảy ra khi xem đơn hàng.")
        
        return []


class ActionConfirmOrder(Action):
    """Action để xác nhận đơn hàng"""

    def name(self) -> Text:
        return "action_confirm_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract user info from metadata
        user_info = None
        latest_message = tracker.latest_message
        if latest_message and 'metadata' in latest_message and latest_message['metadata']:
            user_info = latest_message['metadata'].get('user_info', {})
        
        if not user_info or not user_info.get('user_id'):
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để xác nhận đơn hàng.")
            return []
        
        current_order_id = tracker.get_slot('current_order_id')
        
        if not current_order_id:
            dispatcher.utter_message(text="📝 Bạn chưa có đơn hàng nào để xác nhận. Vui lòng gọi món trước.")
            return []

        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            # Lấy thông tin đơn hàng hiện tại
            order_response = requests.get(f"{API_BASE_URL}/orders/orders/{current_order_id}", headers=headers, timeout=5)
            
            if order_response.status_code != 200:
                dispatcher.utter_message(text="❌ Không tìm thấy đơn hàng để xác nhận.")
                return []
            
            order_info = order_response.json()
            
            if not order_info.get('order_items'):
                dispatcher.utter_message(text="📝 Đơn hàng không có món nào. Vui lòng gọi món trước khi xác nhận.")
                return []
            
            # Cập nhật trạng thái đơn hàng thành CONFIRMED
            update_data = {"status": "CONFIRMED"}
            update_response = requests.put(
                f"{API_BASE_URL}/orders/orders/{current_order_id}",
                headers=headers,
                json=update_data,
                timeout=10
            )
            
            if update_response.status_code == 200:
                # Tính tổng tiền
                total_amount = sum(item.get('subtotal', 0) for item in order_info['order_items'])
                table_id = order_info.get('table_id', 'N/A')
                
                confirmation_message = f"""✅ **ĐƠN HÀNG ĐÃ ĐƯỢC XÁC NHẬN**

📋 **Mã đơn hàng:** #{current_order_id}
🪑 **Bàn:** {table_id}
💰 **Tổng tiền:** {total_amount:,.0f}đ
⏱️ **Thời gian chuẩn bị:** 15-30 phút

📞 **Lưu ý:** 
• Đơn hàng đã được gửi vào bếp
• Món ăn sẽ được phục vụ tại bàn {table_id}
• Liên hệ nhân viên nếu cần hỗ trợ

🍽️ Cảm ơn bạn đã sử dụng dịch vụ! Chúc bạn dùng bữa ngon miệng! """
                
                dispatcher.utter_message(text=confirmation_message)
                
                # Clear current order slots
                return [
                    SlotSet("current_order_id", None),
                    SlotSet("last_order_id", current_order_id),
                    SlotSet("active_table_id", None)
                ]
                
            else:
                dispatcher.utter_message(text="❌ Không thể xác nhận đơn hàng lúc này. Vui lòng thử lại sau.")

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý đơn hàng... Vui lòng đợi.")
        except requests.exceptions.RequestException as e:
            print(f"Order confirmation error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi hệ thống khi xác nhận đơn hàng. Vui lòng liên hệ nhân viên.")
        except Exception as e:
            print(f"Unexpected order confirmation error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi bất ngờ khi xác nhận đơn hàng. Vui lòng liên hệ nhân viên.")

        return []


class ActionCancelOrder(Action):
    """Action để hủy đơn hàng với xác nhận thông tin"""

    def name(self) -> Text:
        return "action_cancel_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract user info from metadata
        user_info = None
        latest_message = tracker.latest_message
        if latest_message and 'metadata' in latest_message and latest_message['metadata']:
            user_info = latest_message['metadata'].get('user_info', {})
        
        if not user_info or not user_info.get('user_id'):
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để hủy đơn hàng.")
            return []
        
        current_order_id = tracker.get_slot('current_order_id')
        
        if not current_order_id:
            dispatcher.utter_message(text="""ℹ️ **KHÔNG CÓ ĐƠN HÀNG ĐỂ HỦY**

Bạn không có đơn hàng nào đang chờ xử lý.

📋 **Để đặt món mới:**
• Đặt bàn trước: "Tôi muốn đặt bàn"  
• Sau đó gọi món: "Tôi muốn gọi [tên món]" """)
            return []
        
        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            # Lấy thông tin đơn hàng hiện tại
            response = requests.get(f"{API_BASE_URL}/orders/orders/{current_order_id}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                order_info = response.json()
                
                if not order_info.get('order_items'):
                    dispatcher.utter_message(text="📝 Đơn hàng hiện tại trống. Không có gì để hủy.")
                    return [SlotSet("current_order_id", None)]
                
                # Hiển thị thông tin đơn hàng và xác nhận
                table_id = order_info.get('table_id', 'N/A')
                order_status = order_info.get('status', 'PENDING')
                total_amount = sum(item.get('subtotal', 0) for item in order_info['order_items'])
                
                confirmation_message = f"""❓ **XÁC NHẬN HỦY ĐƠN HÀNG**

📋 **Thông tin đơn hàng:**
🆔 **Mã đơn:** #{current_order_id}
🪑 **Bàn:** {table_id}
📊 **Trạng thái:** {order_status}
💰 **Tổng tiền:** {total_amount:,.0f}đ

📝 **Các món đã gọi:**"""
                
                for i, item in enumerate(order_info['order_items'], 1):
                    menu_item = item.get('menu_item', {})
                    quantity = item.get('quantity', 0)
                    subtotal = item.get('subtotal', 0)
                    confirmation_message += f"\n{i}. {menu_item.get('name', 'N/A')} x{quantity} = {subtotal:,.0f}đ"
                
                confirmation_message += f"""

⚠️ **Bạn có chắc chắn muốn hủy toàn bộ đơn hàng này không?**

💡 **Chọn:**
• Nói **"Có"** để xác nhận hủy đơn hàng
• Nói **"Không"** để giữ lại đơn hàng
• Nói **"Xóa món [tên]"** để chỉ xóa một món"""
                
                dispatcher.utter_message(text=confirmation_message)
                
                return [SlotSet("pending_cancellation_order_id", current_order_id),
                        SlotSet("conversation_context", "cancel_order_confirmation")]
            else:
                dispatcher.utter_message(text="❌ Không thể tải thông tin đơn hàng. Vui lòng thử lại sau.")
                return []
                
        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Vui lòng thử lại sau.")
        except Exception as e:
            print(f"Error in ActionCancelOrder: {e}")
            dispatcher.utter_message(text="❌ Có lỗi xảy ra khi kiểm tra đơn hàng.")
        
        return []


class ActionConfirmCancelOrder(Action):
    """Action để xác nhận hủy đơn hàng"""

    def name(self) -> Text:
        return "action_confirm_cancel_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        order_id = tracker.get_slot('pending_cancellation_order_id')
        
        if not order_id:
            dispatcher.utter_message(text="❌ Không tìm thấy thông tin đơn hàng cần hủy.")
            return []
        
        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            # Cập nhật trạng thái đơn hàng thành CANCELLED
            update_data = {"status": "CANCELLED"}
            response = requests.put(
                f"{API_BASE_URL}/orders/orders/{order_id}",
                headers=headers,
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                success_message = f"""✅ **ĐÃ HỦY ĐƠN HÀNG THÀNH CÔNG**

📋 **Thông tin:**
🆔 **Mã đơn:** #{order_id}
🗑️ **Trạng thái:** Đã hủy

💡 **Lưu ý:**
• Đơn hàng đã được hủy hoàn toàn
• Không có phí phát sinh
• Bàn vẫn được giữ cho bạn

🔄 **Để gọi món mới:**
• Nói "Tôi muốn gọi [tên món]"
• Hoặc "Xem thực đơn" để chọn món"""
                
                dispatcher.utter_message(text=success_message)
                
                # Clear slots
                return [
                    SlotSet("pending_cancellation_order_id", None),
                    SlotSet("conversation_context", None),
                    SlotSet("current_order_id", None),
                    SlotSet("last_order_id", order_id)
                ]
                
            else:
                dispatcher.utter_message(text="❌ Không thể hủy đơn hàng lúc này. Vui lòng liên hệ nhân viên.")

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý hủy đơn hàng... Vui lòng đợi.")
        except requests.exceptions.RequestException as e:
            print(f"Cancel order error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi hệ thống khi hủy đơn hàng. Vui lòng liên hệ nhân viên.")
        except Exception as e:
            print(f"Unexpected cancel order error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi bất ngờ khi hủy đơn hàng. Vui lòng liên hệ nhân viên.")
        
        return []


class ActionDenyCancellation(Action):
    """Action để từ chối hủy (giữ lại đặt bàn/đơn hàng)"""

    def name(self) -> Text:
        return "action_deny_cancellation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        conversation_context = tracker.get_slot("conversation_context")
        
        if conversation_context == "cancel_reservation_confirmation":
            dispatcher.utter_message(text="""✅ **ĐÃ GIỮ LẠI ĐẶT BÀN**

Đặt bàn của bạn vẫn được giữ nguyên.

💡 **Bạn có thể:**
• Nói "Xem thông tin đặt bàn" 
• Nói "Sửa đặt bàn" để thay đổi thông tin
• Hoặc tiếp tục gọi món: "Tôi muốn gọi [tên món]" """)
        
        elif conversation_context == "cancel_order_confirmation":
            dispatcher.utter_message(text="""✅ **ĐÃ GIỮ LẠI ĐƠN HÀNG**

Đơn hàng của bạn vẫn được giữ nguyên.

💡 **Bạn có thể:**
• Nói "Xem đơn hàng" để kiểm tra lại  
• Nói "Thêm món [tên]" để gọi thêm
• Nói "Xác nhận đơn hàng" để hoàn tất""")
        else:
            dispatcher.utter_message(text="✅ Đã hủy thao tác. Bạn có cần hỗ trợ gì khác không?")
        
        # Clear cancellation context
        return [
            SlotSet("conversation_context", None),
            SlotSet("pending_cancellation_reservation_id", None),
            SlotSet("pending_cancellation_order_id", None)
        ]