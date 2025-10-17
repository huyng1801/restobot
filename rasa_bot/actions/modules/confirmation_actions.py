"""
Confirmation Actions for RestoBot
Xử lý các action liên quan đến xác nhận và chỉnh sửa thông tin
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction


class ActionConfirmBooking(Action):
    """Action để xác nhận thông tin đặt bàn với khả năng chỉnh sửa chi tiết"""

    def name(self) -> Text:
        return "action_confirm_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        num_people = tracker.get_slot('number_of_people')
        reservation_date = tracker.get_slot('reservation_date')
        reservation_time = tracker.get_slot('reservation_time')
        customer_name = tracker.get_slot('customer_name')
        customer_phone = tracker.get_slot('customer_phone')
        
        if all([num_people, reservation_date, reservation_time]):
            confirmation_message = f"""📋 **XÁC NHẬN THÔNG TIN ĐẶT BÀN**

👥 **Số khách:** {int(num_people)} người
📅 **Ngày:** {reservation_date}
🕐 **Thời gian:** {reservation_time}"""

            if customer_name:
                confirmation_message += f"\n👤 **Tên khách hàng:** {customer_name}"
            if customer_phone:
                confirmation_message += f"\n📞 **Số điện thoại:** {customer_phone}"

            confirmation_message += f"""

❓ **Thông tin trên có chính xác không?**

🔹 **"Có"** hoặc **"Đúng rồi"** - Xác nhận đặt bàn
🔹 **"Sửa số người"** - Thay đổi số lượng khách  
🔹 **"Sửa ngày"** - Đổi ngày khác
🔹 **"Sửa giờ"** - Đổi thời gian khác
🔹 **"Sửa tên"** - Đổi tên người đặt
🔹 **"Sửa lại toàn bộ"** - Nhập lại từ đầu"""
            
            dispatcher.utter_message(text=confirmation_message)
            
            return [SlotSet("pending_confirmation", True),
                    SlotSet("conversation_context", "booking_confirmation")]
        else:
            missing_info = []
            if not num_people:
                missing_info.append("số lượng khách")
            if not reservation_date:
                missing_info.append("ngày đặt bàn")
            if not reservation_time:
                missing_info.append("thời gian")
                
            dispatcher.utter_message(
                text=f"⚠️ Thiếu thông tin: **{', '.join(missing_info)}**.\n\n"
                     "Vui lòng cung cấp đầy đủ thông tin để tôi có thể đặt bàn cho bạn.\n\n"
                     "💡 **Ví dụ:** \"Đặt bàn 4 người ngày 25/12/2024 lúc 19:30\""
            )
            return []


class ActionModifyBooking(Action):
    """Action để chỉnh sửa thông tin đặt bàn với hướng dẫn chi tiết"""

    def name(self) -> Text:
        return "action_modify_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        latest_message = tracker.latest_message.get('text', '').lower()
        
        # Xử lý các yêu cầu sửa cụ thể
        if any(word in latest_message for word in ['sửa số người', 'đổi số người', 'thay đổi số người']):
            dispatcher.utter_message(text="""👥 **THAY ĐỔI SỐ LƯỢNG KHÁCH**

Vui lòng cho biết số lượng khách mới:
• **"2 người"**, **"4 người"**, **"6 người"**...
• Hoặc **"Đặt bàn [số] người"**

💡 **Ví dụ:** "Sửa thành 6 người" hoặc "Đặt bàn 8 người" """)
            return [SlotSet("conversation_context", "modify_people_count")]
        
        elif any(word in latest_message for word in ['sửa ngày', 'đổi ngày', 'thay đổi ngày']):
            dispatcher.utter_message(text="""📅 **THAY ĐỔI NGÀY ĐẶT BÀN**

Vui lòng cho biết ngày mới:
• **"Ngày mai"**, **"Thứ 7 này"**, **"Chủ nhật tuần sau"**
• **"25/12/2024"**, **"31/12"**
• **"Ngày 25 tháng 12"**

💡 **Ví dụ:** "Đổi sang ngày 26/12" hoặc "Chủ nhật tuần sau" """)
            return [SlotSet("conversation_context", "modify_date")]
        
        elif any(word in latest_message for word in ['sửa giờ', 'đổi giờ', 'thay đổi giờ', 'sửa thời gian']):
            dispatcher.utter_message(text="""🕐 **THAY ĐỔI THỜI GIAN**

Vui lòng cho biết thời gian mới:
• **"19:30"**, **"20:00"**, **"12:30"**
• **"7 giờ 30 tối"**, **"8 giờ tối"**  
• **"12 giờ 30 trua"**, **"1 giờ chiều"**

💡 **Ví dụ:** "Đổi sang 8 giờ tối" hoặc "Sửa thành 19:30" """)
            return [SlotSet("conversation_context", "modify_time")]
        
        elif any(word in latest_message for word in ['sửa tên', 'đổi tên', 'thay đổi tên']):
            dispatcher.utter_message(text="""👤 **THAY ĐỔI TÊN NGƯỜI ĐẶT**

Vui lòng cho biết tên mới:
• **"Tên tôi là Nguyễn Văn A"**
• **"Đổi tên thành Trần Thị B"** 
• **"Sửa tên: Lê Văn C"**

💡 **Ví dụ:** "Tên tôi là Nguyễn Minh Khoa" """)
            return [SlotSet("conversation_context", "modify_name")]
        
        elif any(word in latest_message for word in ['đặt lại', 'nhập lại', 'làm lại', 'bắt đầu lại']):
            dispatcher.utter_message(text="""🔄 **BẮT ĐẦU LẠI QUÁ TRÌNH ĐẶT BÀN**

Tôi đã xóa toàn bộ thông tin cũ. Hãy cho tôi biết:

👥 **Số lượng khách:** Bao nhiêu người?
📅 **Ngày:** Ngày nào?  
🕐 **Thời gian:** Mấy giờ?

💡 **Ví dụ:** "Đặt bàn 4 người ngày 25/12 lúc 19:30" """)
            return [
                SlotSet("number_of_people", None),
                SlotSet("reservation_date", None), 
                SlotSet("reservation_time", None),
                SlotSet("customer_name", None),
                SlotSet("customer_phone", None),
                SlotSet("conversation_context", "booking_process"),
                SlotSet("pending_confirmation", False)
            ]
        
        else:
            # Hiển thị menu chỉnh sửa tổng quát
            dispatcher.utter_message(text="""🔧 **CHỈNH SỬA THÔNG TIN ĐẶT BÀN**

Bạn muốn thay đổi thông tin nào?

👥 **"Sửa số người"** - Thay đổi số lượng khách
📅 **"Sửa ngày"** - Thay đổi ngày đặt bàn  
🕐 **"Sửa giờ"** - Thay đổi thời gian
👤 **"Sửa tên"** - Đổi tên người đặt
🔄 **"Đặt lại từ đầu"** - Nhập lại toàn bộ

Hoặc nói trực tiếp: **"Đặt bàn 6 người ngày 26/12 lúc 20:00"**""")
        
        return [SlotSet("pending_confirmation", False),
                SlotSet("conversation_context", "booking_modification")]


class ActionConfirmOrder(Action):
    """Action để xác nhận đơn hàng với nhiều tùy chọn chỉnh sửa"""

    def name(self) -> Text:
        return "action_confirm_order_final"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_order = tracker.get_slot('current_order') or []
        active_table_id = tracker.get_slot('active_table_id')
        
        if current_order:
            order_summary = "📋 **XÁC NHẬN ĐƠN HÀNG**\n\n"
            total_price = 0
            
            for i, item in enumerate(current_order, 1):
                dish_name = item.get('dish_name', item.get('name', 'Món ăn'))
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                item_total = price * quantity
                total_price += item_total
                
                order_summary += f"**{i}.** {quantity}x **{dish_name}**\n"
                order_summary += f"     💰 {price:,}đ × {quantity} = {item_total:,}đ\n\n"
            
            order_summary += f"💵 **TỔNG CỘNG: {total_price:,}đ**"
            
            if active_table_id:
                order_summary += f"\n🏷️ **Bàn số:** {active_table_id}"
            else:
                order_summary += "\n⚠️ **Lưu ý:** Cần đặt bàn để lưu đơn hàng"

            order_summary += """

❓ **Xác nhận đơn hàng này?**

✅ **"Có"** hoặc **"Xác nhận"** - Gửi đơn hàng
🔧 **"Sửa [tên món]"** - Chỉnh sửa món cụ thể
➕ **"Thêm [tên món]"** - Gọi thêm món
➖ **"Xóa món [số]"** - Bỏ món theo số thứ tự
🔄 **"Xem lại đơn"** - Hiển thị lại danh sách"""
            
            dispatcher.utter_message(text=order_summary)
            
            return [SlotSet("pending_confirmation", True),
                    SlotSet("conversation_context", "order_confirmation")]
        else:
            dispatcher.utter_message(
                text="🛍️ **Đơn hàng trống!**\n\n"
                     "Bạn chưa gọi món nào. Hãy:\n"
                     "• **'Xem thực đơn'** - Duyệt các món ăn\n"
                     "• **'Gọi [tên món]'** - Thêm món vào đơn\n"
                     "• **'Món đặc biệt'** - Xem món nổi bật\n\n"
                     "💡 **Ví dụ:** \"Gọi phở bò\" hoặc \"Thêm cơm rang\""
            )
            return [SlotSet("conversation_context", "menu_browsing")]


class ActionHandleContextualQuery(Action):
    """Action để xử lý các câu hỏi dựa vào context"""

    def name(self) -> Text:
        return "action_handle_contextual_query"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        last_mentioned_dish = tracker.get_slot('last_mentioned_dish')
        conversation_context = tracker.get_slot('conversation_context')
        current_order = tracker.get_slot('current_order') or []
        latest_message_text = tracker.latest_message.get('text', '').lower()
        intent_name = tracker.latest_message['intent']['name']
        
        # Xử lý các từ chỉ định không rõ ràng như "món đó", "cái này", "nó"
        contextual_references = ['món đó', 'cái này', 'cái đó', 'nó', 'món này', 'dish', 'this', 'that', 'it']
        has_contextual_ref = any(ref in latest_message_text for ref in contextual_references)
        
        # Nếu có tham chiếu không rõ và có món được nhắc đến gần đây
        if has_contextual_ref and last_mentioned_dish:
            if intent_name == 'ask_dish_price' or 'giá' in latest_message_text:
                dispatcher.utter_message(text=f"Bạn hỏi về giá của **{last_mentioned_dish}** phải không? Để tôi kiểm tra...")
                return [FollowupAction("action_ask_dish_price")]
            elif intent_name == 'ask_dish_details' or any(word in latest_message_text for word in ['chi tiết', 'thông tin', 'mô tả']):
                dispatcher.utter_message(text=f"Bạn muốn biết chi tiết về **{last_mentioned_dish}** phải không?")
                return [FollowupAction("action_ask_dish_details")]
            elif intent_name == 'order_food' or any(word in latest_message_text for word in ['gọi', 'đặt', 'muốn ăn']):
                dispatcher.utter_message(text=f"Bạn muốn gọi **{last_mentioned_dish}** phải không?")
                return [FollowupAction("action_add_to_order"), SlotSet("dish_name", last_mentioned_dish)]
        
        # Xử lý context đặt bàn
        if conversation_context == "booking_confirmation":
            if intent_name == 'affirm' or any(word in latest_message_text for word in ['có', 'đúng', 'ok', 'được']):
                return [FollowupAction("action_book_table")]
            elif intent_name == 'deny' or any(word in latest_message_text for word in ['không', 'sai', 'sửa']):
                return [FollowupAction("action_modify_booking")]
            else:
                dispatcher.utter_message(text="Bạn đang trong quá trình xác nhận đặt bàn. Vui lòng nói:\n• **'Có'** để xác nhận\n• **'Sửa lại'** để chỉnh sửa")
                return []
        
        # Xử lý context hủy đặt bàn
        if conversation_context == "cancel_reservation_confirmation":
            if intent_name == 'affirm' or any(word in latest_message_text for word in ['có', 'đúng', 'ok', 'xác nhận']):
                return [FollowupAction("action_confirm_cancel_reservation")]
            elif intent_name == 'deny' or any(word in latest_message_text for word in ['không', 'thôi', 'giữ lại']):
                return [FollowupAction("action_deny_cancellation")]
            else:
                dispatcher.utter_message(text="Bạn đang xác nhận hủy đặt bàn. Vui lòng nói:\n• **'Có'** để xác nhận hủy\n• **'Không'** để giữ lại")
                return []
        
        # Xử lý context hủy đơn hàng  
        if conversation_context == "cancel_order_confirmation":
            if intent_name == 'affirm' or any(word in latest_message_text for word in ['có', 'đúng', 'ok', 'xác nhận']):
                return [FollowupAction("action_confirm_cancel_order")]
            elif intent_name == 'deny' or any(word in latest_message_text for word in ['không', 'thôi', 'giữ lại']):
                return [FollowupAction("action_deny_cancellation")]
            else:
                dispatcher.utter_message(text="Bạn đang xác nhận hủy đơn hàng. Vui lòng nói:\n• **'Có'** để xác nhận hủy\n• **'Không'** để giữ lại")
                return []
        
        # Xử lý context đơn hàng
        if conversation_context == "order_confirmation":
            if intent_name == 'affirm' or any(word in latest_message_text for word in ['có', 'đúng', 'ok', 'xác nhận']):
                return [FollowupAction("action_confirm_order")]
            elif intent_name == 'deny' or any(word in latest_message_text for word in ['không', 'sửa', 'thay đổi']):
                dispatcher.utter_message(text="Bạn có thể:\n• **'Thêm [tên món]'** để gọi thêm\n• **'Xóa [tên món]'** để bỏ món\n• **'Xem đơn hàng'** để kiểm tra lại")
                return [SlotSet("conversation_context", None), SlotSet("pending_confirmation", False)]
            else:
                dispatcher.utter_message(text="Bạn đang trong quá trình xác nhận đơn hàng. Vui lòng nói:\n• **'Có'** để xác nhận\n• **'Sửa lại'** để chỉnh sửa đơn")
                return []
        
        # Xử lý các câu hỏi về số lượng trong đơn hàng
        if current_order and any(word in latest_message_text for word in ['bao nhiêu', 'tổng', 'tiền', 'giá']):
            return [FollowupAction("action_view_current_order")]
        
        # Xử lý các từ chỉ thứ tự như "món đầu", "món cuối", "món thứ hai"
        order_references = {
            'đầu': 0, 'đầu tiên': 0, 'first': 0, '1': 0,
            'thứ hai': 1, 'second': 1, '2': 1, 
            'thứ ba': 2, 'third': 2, '3': 2,
            'cuối': -1, 'cuối cùng': -1, 'last': -1
        }
        
        for ref, index in order_references.items():
            if ref in latest_message_text and current_order:
                if 0 <= index < len(current_order) or index == -1:
                    target_dish = current_order[index].get('dish_name', current_order[index].get('name', 'Món ăn'))
                    if intent_name == 'ask_dish_price' or 'giá' in latest_message_text:
                        dispatcher.utter_message(text=f"Bạn hỏi về giá của **{target_dish}** (món thứ {index + 1 if index >= 0 else len(current_order)}) phải không?")
                        return [SlotSet("last_mentioned_dish", target_dish), FollowupAction("action_ask_dish_price")]
                    break
        
        # Default response với gợi ý dựa vào context
        if last_mentioned_dish:
            suggestion_msg = f"🤔 Tôi không rõ ý bạn về **{last_mentioned_dish}**. "
        elif current_order:
            suggestion_msg = "📝 Bạn đang có đơn hàng chờ xử lý. "
        else:
            suggestion_msg = "😊 Tôi chưa hiểu câu hỏi của bạn. "
            
        suggestion_msg += "\n\n💡 **Hãy thử:**\n"
        suggestion_msg += "• **'Xem thực đơn'** - Duyệt món ăn\n"
        suggestion_msg += "• **'Giá [tên món]'** - Hỏi giá món\n"
        suggestion_msg += "• **'Đặt bàn [số người] người'** - Đặt chỗ\n"
        if current_order:
            suggestion_msg += "• **'Xem đơn hàng'** - Kiểm tra đơn\n"
            suggestion_msg += "• **'Xác nhận đơn'** - Hoàn tất gọi món"
        if last_mentioned_dish:
            suggestion_msg += f"• **'Chi tiết {last_mentioned_dish}'** - Xem thông tin món"
        
        dispatcher.utter_message(text=suggestion_msg)
        return []


class ActionModifyOrderItem(Action):
    """Action để chỉnh sửa món trong đơn hàng"""

    def name(self) -> Text:
        return "action_modify_order_item"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_order = tracker.get_slot('current_order') or []
        latest_message = tracker.latest_message.get('text', '').lower()
        
        if not current_order:
            dispatcher.utter_message(text="📝 Đơn hàng trống. Vui lòng gọi món trước khi chỉnh sửa.")
            return []
        
        # Phân tích loại chỉnh sửa từ tin nhắn
        if any(word in latest_message for word in ['xóa món', 'bỏ món', 'hủy món']):
            # Tìm số thứ tự hoặc tên món cần xóa
            import re
            number_match = re.search(r'(?:món\s*)?(?:số\s*)?(\d+)', latest_message)
            if number_match:
                item_index = int(number_match.group(1)) - 1
                if 0 <= item_index < len(current_order):
                    item_to_remove = current_order[item_index]
                    dish_name = item_to_remove.get('dish_name', item_to_remove.get('name', 'Món ăn'))
                    
                    dispatcher.utter_message(
                        text=f"❌ **Xác nhận xóa món**\n\n"
                             f"Bạn muốn xóa: **{dish_name}** (món số {item_index + 1})\n"
                             f"Số lượng: {item_to_remove.get('quantity', 1)}\n"
                             f"Giá: {item_to_remove.get('price', 0):,}đ\n\n"
                             "**'Có'** để xác nhận xóa | **'Không'** để giữ lại"
                    )
                    
                    return [
                        SlotSet("item_to_modify", item_index),
                        SlotSet("conversation_context", "confirm_remove_item"),
                        SlotSet("pending_confirmation", True)
                    ]
        
        elif any(word in latest_message for word in ['thêm', 'gọi thêm', 'order thêm']):
            dispatcher.utter_message(
                text="➕ **Gọi thêm món**\n\n"
                     "Bạn muốn gọi thêm món gì?\n\n"
                     "💡 **Ví dụ:**\n"
                     "• **'Thêm phở bò'**\n"
                     "• **'Gọi thêm 2 cơm rang'**\n"
                     "• **'Order thêm salad'**"
            )
            return [SlotSet("conversation_context", "adding_more_items")]
        
        elif any(word in latest_message for word in ['sửa số lượng', 'đổi số lượng', 'thay đổi số lượng']):
            order_list = "🔢 **CHỈNH SỬA SỐ LƯỢNG**\n\n"
            for i, item in enumerate(current_order, 1):
                dish_name = item.get('dish_name', item.get('name', 'Món ăn'))
                quantity = item.get('quantity', 1)
                order_list += f"**{i}.** {dish_name} - Hiện tại: {quantity}\n"
            
            order_list += "\n💡 **Cách sử dụng:**\n"
            order_list += "• **'Món 1 thành 3 phần'** - Đổi số lượng món số 1\n"
            order_list += "• **'Sửa phở bò thành 2 tô'** - Đổi theo tên món"
            
            dispatcher.utter_message(text=order_list)
            return [SlotSet("conversation_context", "modify_quantity")]
        
        else:
            # Hiển thị menu chỉnh sửa tổng quát
            order_summary = "🔧 **CHỈNH SỬA ĐƠN HÀNG**\n\n"
            for i, item in enumerate(current_order, 1):
                dish_name = item.get('dish_name', item.get('name', 'Món ăn'))
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                order_summary += f"**{i}.** {quantity}x {dish_name} - {price:,}đ\n"
            
            order_summary += """

🛠️ **Tùy chọn chỉnh sửa:**
➖ **"Xóa món [số]"** - Bỏ món theo số thứ tự
➕ **"Thêm [tên món]"** - Gọi thêm món mới  
🔢 **"Sửa số lượng"** - Thay đổi số lượng món
🔄 **"Xem lại đơn"** - Hiển thị đơn hàng hiện tại

💡 **Ví dụ:** "Xóa món 2" hoặc "Thêm salad" """
            
            dispatcher.utter_message(text=order_summary)
            return [SlotSet("conversation_context", "order_modification")]


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