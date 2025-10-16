"""
Confirmation Actions for RestoBot
Xử lý các action liên quan đến xác nhận và chỉnh sửa thông tin
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction


class ActionConfirmBooking(Action):
    """Action để xác nhận thông tin đặt bàn"""

    def name(self) -> Text:
        return "action_confirm_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        num_people = tracker.get_slot('number_of_people')
        reservation_date = tracker.get_slot('reservation_date')
        reservation_time = tracker.get_slot('reservation_time')
        
        if all([num_people, reservation_date, reservation_time]):
            confirmation_message = f"""📋 **XÁC NHẬN THÔNG TIN ĐẶT BÀN**

👥 **Số người:** {int(num_people)} người
📅 **Ngày:** {reservation_date}
🕐 **Giờ:** {reservation_time}

❓ **Thông tin này có chính xác không?**
Nói "có" để xác nhận hoặc "sửa lại" để chỉnh sửa."""
            
            dispatcher.utter_message(text=confirmation_message)
            
            return [SlotSet("pending_confirmation", True),
                    SlotSet("conversation_context", "booking_confirmation")]
        else:
            dispatcher.utter_message(text="Thiếu thông tin đặt bàn. Vui lòng cung cấp đầy đủ số người, ngày và giờ.")
            return []


class ActionModifyBooking(Action):
    """Action để chỉnh sửa thông tin đặt bàn"""

    def name(self) -> Text:
        return "action_modify_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="""🔧 **CHỈNH SỬA THÔNG TIN**

Bạn muốn thay đổi thông tin gì?
• 👥 **"Đổi số người"** - Thay đổi số lượng khách
• 📅 **"Đổi ngày"** - Thay đổi ngày đặt bàn  
• 🕐 **"Đổi giờ"** - Thay đổi giờ đặt bàn
• 🔄 **"Đặt lại từ đầu"** - Nhập lại toàn bộ thông tin

Hoặc bạn có thể nói trực tiếp: "Đặt bàn [số người] người ngày [dd/mm/yyyy] lúc [hh:mm]" """)
        
        return [SlotSet("pending_confirmation", False),
                SlotSet("conversation_context", "booking_modification")]


class ActionConfirmOrder(Action):
    """Action để xác nhận đơn hàng"""

    def name(self) -> Text:
        return "action_confirm_order_final"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_order = tracker.get_slot('current_order') or []
        
        if current_order:
            order_summary = "📋 **XÁC NHẬN ĐƠN HÀNG**\n\n"
            total_price = 0
            
            for item in current_order:
                order_summary += f"• {item.get('quantity', 1)}x {item.get('dish_name', 'Món ăn')} - {item.get('price', 0):,}đ\n"
                total_price += item.get('price', 0) * item.get('quantity', 1)
            
            order_summary += f"\n💰 **Tổng cộng:** {total_price:,}đ"
            order_summary += "\n\n❓ **Xác nhận đơn hàng này?**\nNói 'có' để xác nhận hoặc 'sửa lại' để chỉnh sửa."
            
            dispatcher.utter_message(text=order_summary)
            
            return [SlotSet("pending_confirmation", True),
                    SlotSet("conversation_context", "order_confirmation")]
        else:
            dispatcher.utter_message(text="Đơn hàng trống. Vui lòng gọi món trước khi xác nhận.")
            return []


class ActionHandleContextualQuery(Action):
    """Action để xử lý các câu hỏi dựa vào context"""

    def name(self) -> Text:
        return "action_handle_contextual_query"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        last_mentioned_dish = tracker.get_slot('last_mentioned_dish')
        conversation_context = tracker.get_slot('conversation_context')
        
        # Nếu có món ăn được nhắc đến gần đây
        if last_mentioned_dish:
            intent = tracker.latest_message['intent']['name']
            
            if intent == 'ask_dish_price':
                # Redirect to dish details action with context
                return [FollowupAction("action_ask_dish_details")]
            elif intent == 'ask_dish_details':
                # Redirect to dish details action with context
                return [FollowupAction("action_ask_dish_details")]
        
        # Nếu đang trong quá trình đặt bàn và có câu hỏi chung
        if conversation_context == "booking_confirmation":
            dispatcher.utter_message(text="Bạn đang trong quá trình xác nhận đặt bàn. Vui lòng nói 'có' để xác nhận hoặc 'sửa lại' để chỉnh sửa.")
            return []
        
        # Default fallback
        dispatcher.utter_message(text="Tôi không hiểu câu hỏi trong ngữ cảnh hiện tại. Bạn có thể nói rõ hơn được không?")
        return []


class ActionResetContext(Action):
    """Action để reset context khi bắt đầu cuộc trò chuyện mới"""

    def name(self) -> Text:
        return "action_reset_context"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [
            SlotSet("conversation_context", None),
            SlotSet("pending_confirmation", False),
            SlotSet("last_mentioned_dish", None),
            SlotSet("current_step", None)
        ]