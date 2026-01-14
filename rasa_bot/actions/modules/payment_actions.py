"""
Payment Actions for RestoBot
Xử lý các action liên quan đến thanh toán
"""
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .auth_helper import auth_helper, get_authenticated_user_from_tracker, get_auth_headers_from_tracker

# URL của FastAPI backend
API_BASE_URL = "http://api:8000/api/v1"


class ActionInitiatePayment(Action):
    """Action để bắt đầu quá trình thanh toán"""

    def name(self) -> Text:
        return "action_initiate_payment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract user info from metadata
        authenticated_user = get_authenticated_user_from_tracker(tracker)
        
        if not authenticated_user:
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để thanh toán.")
            return []
        
        current_order_id = tracker.get_slot('current_order_id') or tracker.get_slot('last_order_id')
        
        if not current_order_id:
            dispatcher.utter_message(text="""💳 **CHƯA CÓ ĐƠN HÀNG ĐỂ THANH TOÁN**

Bạn chưa có đơn hàng nào để thanh toán.

📝 **Để tạo đơn hàng:**
• Đặt bàn trước: "Tôi muốn đặt bàn"
• Gọi món: "Tôi muốn gọi [tên món]"
• Xác nhận đơn hàng: "Xác nhận đơn hàng" """)
            return []

        try:
            # Lấy auth headers từ tracker
            headers = get_auth_headers_from_tracker(tracker)

            # Lấy thông tin đơn hàng
            response = requests.get(f"{API_BASE_URL}/orders/orders/{current_order_id}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                order_info = response.json()
                
                # Kiểm tra trạng thái đơn hàng
                if order_info.get('payment_status') == 'paid':
                    dispatcher.utter_message(text=f"""✅ **ĐÃ THANH TOÁN**

Đơn hàng #{current_order_id} đã được thanh toán.
💰 Tổng tiền: {order_info.get('total_amount', 0):,.0f}đ
📅 Phương thức: {order_info.get('payment_method', 'N/A')}

🍽️ Cảm ơn bạn đã sử dụng dịch vụ! """)
                    return []
                
                # Kiểm tra trạng thái đơn hàng có thể thanh toán không
                if order_info.get('status') not in ['confirmed', 'ready', 'served']:
                    dispatcher.utter_message(text=f"""⚠️ **CHƯA THỂ THANH TOÁN**

Đơn hàng #{current_order_id} chưa thể thanh toán.
📊 **Trạng thái hiện tại:** {order_info.get('status', 'unknown')}

✅ **Đơn hàng cần được xác nhận trước khi thanh toán**
💡 Nói: "Xác nhận đơn hàng" """)
                    return []

                # Hiển thị thông tin thanh toán
                table_id = order_info.get('table_id', 'N/A')
                total_amount = order_info.get('total_amount', 0)
                
                payment_message = f"""💳 **THANH TOÁN ĐƠN HÀNG**

📋 **Mã đơn hàng:** #{current_order_id}
🪑 **Bàn:** {table_id}
💰 **Tổng tiền:** {total_amount:,.0f}đ

🔄 **Đang mở giao diện thanh toán...**

💡 **Các phương thức thanh toán:**
• 💵 Tiền mặt
• 💳 Thẻ tín dụng/ghi nợ
• 🏦 Chuyển khoản ngân hàng
• 📱 QR Code / Mobile Payment

Vui lòng chọn phương thức thanh toán phù hợp! """

                dispatcher.utter_message(text=payment_message)
                
                return [
                    SlotSet("payment_order_id", current_order_id),
                    SlotSet("payment_amount", total_amount)
                ]
                
            else:
                dispatcher.utter_message(text="❌ Không tìm thấy đơn hàng. Vui lòng kiểm tra lại.")
                return []

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Vui lòng thử lại sau.")
            return []
        except Exception as e:
            print(f"Error in ActionInitiatePayment: {e}")
            dispatcher.utter_message(text="❌ Có lỗi xảy ra. Vui lòng liên hệ nhân viên.")
            return []


class ActionProcessPayment(Action):
    """Action để xử lý thanh toán"""

    def name(self) -> Text:
        return "action_process_payment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract user info from metadata
        authenticated_user = get_authenticated_user_from_tracker(tracker)
        
        if not authenticated_user:
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để thanh toán.")
            return []

        payment_order_id = tracker.get_slot('payment_order_id')
        payment_amount = tracker.get_slot('payment_amount')
        
        # Get payment method from entities
        payment_method = None
        entities = tracker.latest_message.get('entities', [])
        for entity in entities:
            if entity['entity'] == 'payment_method':
                payment_method = entity['value']
                break
        
        # Default payment method if not specified
        if not payment_method:
            payment_method = 'cash'  # Default to cash
        
        if not payment_order_id:
            dispatcher.utter_message(text="❌ Không tìm thấy thông tin đơn hàng để thanh toán.")
            return []

        try:
            # Lấy auth headers từ tracker
            headers = get_auth_headers_from_tracker(tracker)

            # Gửi yêu cầu thanh toán
            payment_data = {
                "payment_method": payment_method,
                "amount": payment_amount,
                "transaction_id": f"CHAT-{payment_order_id}-{tracker.sender_id}"
            }

            response = requests.post(
                f"{API_BASE_URL}/orders/orders/{payment_order_id}/payment",
                headers=headers,
                json=payment_data,
                timeout=10
            )
            
            if response.status_code == 200:
                order_info = response.json()
                
                payment_success_message = f"""✅ **THANH TOÁN THÀNH CÔNG**

📋 **Mã đơn hàng:** #{payment_order_id}
💰 **Số tiền:** {payment_amount:,.0f}đ
💳 **Phương thức:** {payment_method}
📅 **Thời gian:** Vừa xong

🎉 **Cảm ơn bạn đã sử dụng dịch vụ!**
🍽️ Chúc bạn dùng bữa ngon miệng!

📧 **Hóa đơn điện tử đã được gửi qua email**
📞 **Liên hệ:** Nếu cần hỗ trợ, vui lòng gọi 0123-456-789 """
                
                dispatcher.utter_message(text=payment_success_message)
                
                # Clear payment slots
                return [
                    SlotSet("payment_order_id", None),
                    SlotSet("payment_amount", None),
                    SlotSet("current_order_id", None)
                ]
                
            else:
                error_detail = "Lỗi không xác định"
                try:
                    error_response = response.json()
                    error_detail = error_response.get('detail', error_detail)
                except:
                    pass
                    
                dispatcher.utter_message(text=f"""❌ **THANH TOÁN THẤT BẠI**

{error_detail}

🔄 **Vui lòng thử lại với phương thức khác hoặc liên hệ nhân viên**
📞 **Hotline:** 0123-456-789 """)
                return []

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý thanh toán... Vui lòng đợi.")
            return []
        except Exception as e:
            print(f"Error in ActionProcessPayment: {e}")
            dispatcher.utter_message(text="🔧 Lỗi hệ thống thanh toán. Vui lòng liên hệ nhân viên ngay.")
            return []


class ActionCheckPaymentStatus(Action):
    """Action để kiểm tra trạng thái thanh toán"""

    def name(self) -> Text:
        return "action_check_payment_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract user info from metadata
        authenticated_user = get_authenticated_user_from_tracker(tracker)
        
        if not authenticated_user:
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để kiểm tra thanh toán.")
            return []

        # Get order ID from slot or last order
        order_id = tracker.get_slot('current_order_id') or tracker.get_slot('last_order_id')
        
        if not order_id:
            dispatcher.utter_message(text="❌ Không tìm thấy đơn hàng để kiểm tra.")
            return []

        try:
            # Lấy auth headers từ tracker
            headers = get_auth_headers_from_tracker(tracker)

            # Lấy thông tin đơn hàng
            response = requests.get(f"{API_BASE_URL}/orders/orders/{order_id}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                order_info = response.json()
                payment_status = order_info.get('payment_status', 'pending')
                payment_method = order_info.get('payment_method', 'N/A')
                total_amount = order_info.get('total_amount', 0)
                
                if payment_status == 'paid':
                    status_message = f"""✅ **ĐÃ THANH TOÁN**

📋 **Đơn hàng:** #{order_id}
💰 **Số tiền:** {total_amount:,.0f}đ
💳 **Phương thức:** {payment_method}
✅ **Trạng thái:** Đã thanh toán thành công

🍽️ Cảm ơn bạn! """
                else:
                    status_message = f"""⏳ **CHƯA THANH TOÁN**

📋 **Đơn hàng:** #{order_id}
💰 **Số tiền:** {total_amount:,.0f}đ
❌ **Trạng thái:** Chưa thanh toán

💡 **Để thanh toán:** Nói "Tôi muốn thanh toán" """
                
                dispatcher.utter_message(text=status_message)
                return []
                
            else:
                dispatcher.utter_message(text="❌ Không tìm thấy thông tin đơn hàng.")
                return []

        except Exception as e:
            print(f"Error in ActionCheckPaymentStatus: {e}")
            dispatcher.utter_message(text="❌ Có lỗi khi kiểm tra trạng thái thanh toán.")
            return []