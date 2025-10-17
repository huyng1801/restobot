"""
Advanced Conversation Management for RestoBot
Quản lý hội thoại nâng cao với xử lý ngữ cảnh và tham chiếu
"""
from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import requests
import json
import re
from datetime import datetime

class ActionConversationManager(Action):
    """Action quản lý ngữ cảnh cuộc trò chuyện và xử lý tham chiếu mơ hồ"""

    def name(self) -> Text:
        return "action_conversation_manager"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        latest_message = tracker.latest_message.get('text', '').lower()
        intent_name = tracker.latest_message['intent']['name']
        
        # Lấy thông tin context hiện tại
        conversation_context = tracker.get_slot('conversation_context')
        last_mentioned_dish = tracker.get_slot('last_mentioned_dish')
        last_mentioned_dishes = tracker.get_slot('last_mentioned_dishes') or []
        current_order = tracker.get_slot('current_order') or []
        last_action = tracker.get_slot('last_action_type')
        
        # Phân tích các từ tham chiếu mơ hồ
        contextual_refs = self._detect_contextual_references(latest_message)
        
        if contextual_refs:
            return self._handle_contextual_references(
                dispatcher, tracker, contextual_refs, 
                last_mentioned_dish, last_mentioned_dishes, 
                current_order, intent_name, latest_message
            )
        
        # Xử lý các câu hỏi về thứ tự trong danh sách
        order_ref = self._detect_order_references(latest_message, current_order)
        if order_ref:
            return self._handle_order_references(
                dispatcher, tracker, order_ref, 
                current_order, intent_name, latest_message
            )
        
        # Xử lý câu hỏi dựa vào context của cuộc trò chuyện
        if conversation_context:
            return self._handle_context_based_queries(
                dispatcher, tracker, conversation_context,
                intent_name, latest_message
            )
        
        return []

    def _detect_contextual_references(self, message: str) -> List[str]:
        """Phát hiện các từ tham chiếu mơ hồ trong tin nhắn"""
        contextual_patterns = {
            'món_đó': ['món đó', 'cái đó', 'nó', 'dish đó', 'thứ đó'],
            'món_này': ['món này', 'cái này', 'this', 'dish này', 'thứ này'],
            'món_kia': ['món kia', 'cái kia', 'that', 'dish kia', 'thứ kia'],
            'món_vừa_rồi': ['món vừa rồi', 'món lúc nãy', 'món trước', 'món vừa nói'],
            'tất_cả': ['tất cả', 'toàn bộ', 'all', 'hết', 'mọi thứ']
        }
        
        detected_refs = []
        for ref_type, patterns in contextual_patterns.items():
            if any(pattern in message for pattern in patterns):
                detected_refs.append(ref_type)
        
        return detected_refs

    def _handle_contextual_references(self, dispatcher: CollectingDispatcher,
                                    tracker: Tracker, contextual_refs: List[str],
                                    last_mentioned_dish: str, last_mentioned_dishes: List[str],
                                    current_order: List[Dict], intent_name: str, 
                                    message: str) -> List[Dict[Text, Any]]:
        """Xử lý các tham chiếu mơ hồ dựa vào context"""
        
        # Xử lý "món đó", "món này" - tham chiếu đến món được nhắc gần nhất
        if any(ref in contextual_refs for ref in ['món_đó', 'món_này', 'món_vừa_rôi']):
            if last_mentioned_dish:
                return self._handle_dish_reference(
                    dispatcher, tracker, last_mentioned_dish, 
                    intent_name, message
                )
            elif last_mentioned_dishes:
                latest_dish = last_mentioned_dishes[-1]
                return self._handle_dish_reference(
                    dispatcher, tracker, latest_dish, 
                    intent_name, message
                )
            else:
                dispatcher.utter_message(text="🤔 Bạn đang nói về món nào vậy? Chúng ta chưa nhắc đến món nào cụ thể.")
                return [FollowupAction("action_view_menu")]
        
        # Xử lý "tất cả" - tham chiếu đến toàn bộ đơn hàng
        if 'tất_cả' in contextual_refs and current_order:
            if intent_name == 'cancel_order' or 'hủy' in message or 'xóa' in message:
                dispatcher.utter_message(text="Bạn muốn hủy **toàn bộ đơn hàng** hiện tại phải không?")
                return [SlotSet("conversation_context", "confirm_cancel_all_order"), 
                        SlotSet("pending_confirmation", True)]
            elif 'giá' in message or intent_name == 'ask_dish_price':
                return [FollowupAction("action_view_current_order")]
        
        return []

    def _handle_dish_reference(self, dispatcher: CollectingDispatcher,
                             tracker: Tracker, dish_name: str,
                             intent_name: str, message: str) -> List[Dict[Text, Any]]:
        """Xử lý tham chiếu đến một món ăn cụ thể"""
        
        if intent_name == 'ask_dish_price' or 'giá' in message:
            dispatcher.utter_message(text=f"💰 Bạn hỏi về giá của **{dish_name}** phải không? Để tôi kiểm tra...")
            return [SlotSet("dish_name", dish_name), FollowupAction("action_ask_dish_price")]
        
        elif intent_name == 'ask_dish_details' or any(word in message for word in ['chi tiết', 'thông tin', 'mô tả', 'nguyên liệu']):
            dispatcher.utter_message(text=f"ℹ️ Bạn muốn biết chi tiết về **{dish_name}** phải không?")
            return [SlotSet("dish_name", dish_name), FollowupAction("action_ask_dish_details")]
        
        elif intent_name == 'order_food' or intent_name == 'add_to_order' or any(word in message for word in ['gọi', 'đặt', 'thêm']):
            dispatcher.utter_message(text=f"🍽️ Bạn muốn gọi **{dish_name}** phải không?")
            return [SlotSet("dish_name", dish_name), FollowupAction("action_add_to_order")]
        
        elif intent_name == 'modify_order' or 'xóa' in message or 'bỏ' in message:
            dispatcher.utter_message(text=f"❌ Bạn muốn xóa **{dish_name}** khỏi đơn hàng phải không?")
            return [SlotSet("dish_name", dish_name), FollowupAction("action_remove_from_order")]
        
        else:
            # Cung cấp gợi ý dựa trên món được nhắc đến
            suggestion_msg = f"🍽️ **{dish_name}** - Bạn có thể:\n"
            suggestion_msg += f"• **'Giá {dish_name}'** - Xem giá món\n"
            suggestion_msg += f"• **'Chi tiết {dish_name}'** - Xem thông tin chi tiết\n"
            suggestion_msg += f"• **'Gọi {dish_name}'** - Thêm vào đơn hàng\n"
            suggestion_msg += f"• **'Xóa {dish_name}'** - Bỏ khỏi đơn hàng"
            
            dispatcher.utter_message(text=suggestion_msg)
            return []

    def _detect_order_references(self, message: str, current_order: List[Dict]) -> Optional[Dict]:
        """Phát hiện tham chiếu đến thứ tự trong danh sách (món đầu, món cuối, v.v.)"""
        if not current_order:
            return None
        
        order_patterns = {
            'đầu': {'index': 0, 'aliases': ['đầu', 'đầu tiên', 'first', 'đầu tiền', 'thứ nhất']},
            'thứ_hai': {'index': 1, 'aliases': ['thứ hai', 'second', 'thứ 2', 'số 2']},
            'thứ_ba': {'index': 2, 'aliases': ['thứ ba', 'third', 'thứ 3', 'số 3']},
            'thứ_tư': {'index': 3, 'aliases': ['thứ tư', 'fourth', 'thứ 4', 'số 4']},
            'cuối': {'index': -1, 'aliases': ['cuối', 'cuối cùng', 'last', 'chót']},
            'trước_cuối': {'index': -2, 'aliases': ['trước cuối', 'second last', 'áp chót']}
        }
        
        for order_type, config in order_patterns.items():
            if any(alias in message for alias in config['aliases']):
                index = config['index']
                if index == -1:  # món cuối
                    actual_index = len(current_order) - 1
                elif index == -2:  # món trước cuối
                    actual_index = len(current_order) - 2 if len(current_order) > 1 else 0
                else:
                    actual_index = index
                
                if 0 <= actual_index < len(current_order):
                    return {
                        'type': order_type,
                        'index': actual_index,
                        'dish': current_order[actual_index]
                    }
        
        # Tìm số thứ tự cụ thể (món số 1, món số 2, v.v.)
        number_match = re.search(r'món\s*(?:số\s*)?(\d+)', message)
        if number_match:
            try:
                number = int(number_match.group(1)) - 1  # Chuyển từ 1-based sang 0-based
                if 0 <= number < len(current_order):
                    return {
                        'type': f'số_{number + 1}',
                        'index': number,
                        'dish': current_order[number]
                    }
            except ValueError:
                pass
        
        return None

    def _handle_order_references(self, dispatcher: CollectingDispatcher,
                               tracker: Tracker, order_ref: Dict,
                               current_order: List[Dict], intent_name: str,
                               message: str) -> List[Dict[Text, Any]]:
        """Xử lý tham chiếu đến thứ tự trong danh sách đơn hàng"""
        
        dish = order_ref['dish']
        dish_name = dish.get('dish_name', dish.get('name', 'Món ăn'))
        position_desc = f"món thứ {order_ref['index'] + 1}"
        
        if order_ref['type'] == 'cuối':
            position_desc = "món cuối cùng"
        elif order_ref['type'] == 'đầu':
            position_desc = "món đầu tiên"
        
        if intent_name == 'ask_dish_price' or 'giá' in message:
            price = dish.get('price', 0)
            quantity = dish.get('quantity', 1)
            total_price = price * quantity
            
            response = f"💰 **{dish_name}** ({position_desc}):\n"
            response += f"• Đơn giá: {price:,}đ\n"
            if quantity > 1:
                response += f"• Số lượng: {quantity}\n"
                response += f"• Thành tiền: {total_price:,}đ"
            
            dispatcher.utter_message(text=response)
            return [SlotSet("last_mentioned_dish", dish_name)]
        
        elif intent_name == 'modify_order' or 'xóa' in message or 'bỏ' in message:
            dispatcher.utter_message(text=f"❌ Bạn muốn xóa **{dish_name}** ({position_desc}) khỏi đơn hàng phải không?")
            return [
                SlotSet("dish_name", dish_name),
                SlotSet("conversation_context", "confirm_remove_dish"),
                SlotSet("pending_confirmation", True)
            ]
        
        elif 'chi tiết' in message or 'thông tin' in message:
            dispatcher.utter_message(text=f"ℹ️ Bạn muốn xem chi tiết **{dish_name}** ({position_desc})?")
            return [SlotSet("dish_name", dish_name), FollowupAction("action_ask_dish_details")]
        
        else:
            # Hiển thị thông tin tổng quan về món
            price = dish.get('price', 0)
            quantity = dish.get('quantity', 1)
            total_price = price * quantity
            
            response = f"🍽️ **{dish_name}** ({position_desc}):\n"
            response += f"• Số lượng: {quantity}\n"
            response += f"• Đơn giá: {price:,}đ\n"
            response += f"• Thành tiền: {total_price:,}đ\n\n"
            response += "💡 **Bạn có thể:**\n"
            response += f"• **'Xóa món này'** - Bỏ khỏi đơn hàng\n"
            response += f"• **'Chi tiết món này'** - Xem thông tin chi tiết"
            
            dispatcher.utter_message(text=response)
            return [SlotSet("last_mentioned_dish", dish_name)]

    def _handle_context_based_queries(self, dispatcher: CollectingDispatcher,
                                    tracker: Tracker, conversation_context: str,
                                    intent_name: str, message: str) -> List[Dict[Text, Any]]:
        """Xử lý các câu hỏi dựa vào context của cuộc trò chuyện"""
        
        # Context: đang trong quá trình đặt bàn
        if conversation_context in ["booking_process", "booking_confirmation"]:
            if intent_name == 'ask_dish_price' or 'giá' in message:
                dispatcher.utter_message(text="📋 Bạn đang trong quá trình đặt bàn. Sau khi hoàn tất đặt bàn, tôi sẽ giúp bạn xem thực đơn và giá cả.")
                return []
            elif intent_name == 'view_menu':
                dispatcher.utter_message(text="📋 Hãy hoàn tất đặt bàn trước. Sau đó tôi sẽ giúp bạn xem thực đơn!")
                return []
        
        # Context: đang xem thực đơn
        elif conversation_context == "viewing_menu":
            if intent_name == 'book_table':
                dispatcher.utter_message(text="🍽️ Bạn đã chọn món nào chưa? Tôi có thể giúp bạn gọi món trước, sau đó đặt bàn.")
                return []
            elif 'tất cả' in message and ('giá' in message or intent_name == 'ask_dish_price'):
                dispatcher.utter_message(text="📋 Bạn muốn xem giá của tất cả món trong thực đơn? Để tôi hiển thị...")
                return [FollowupAction("action_view_menu")]
        
        # Context: đang gọi món
        elif conversation_context in ["ordering_process", "order_confirmation"]:
            if intent_name == 'book_table' and not tracker.get_slot('active_table_id'):
                dispatcher.utter_message(text="⚠️ Bạn cần đặt bàn trước khi gọi món. Hãy hoàn tất đặt bàn để tôi có thể lưu đơn hàng này.")
                return [SlotSet("conversation_context", "need_table_booking")]
            elif 'tổng' in message or 'bao nhiêu' in message:
                return [FollowupAction("action_view_current_order")]
        
        return []


class ActionUpdateConversationContext(Action):
    """Action cập nhật context cuộc trò chuyện"""

    def name(self) -> Text:
        return "action_update_conversation_context"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        latest_action = tracker.latest_action_name
        intent_name = tracker.latest_message['intent']['name']
        
        # Xác định context dựa vào action/intent
        new_context = None
        action_type = None
        
        if latest_action in ['action_view_menu', 'action_ask_menu_categories']:
            new_context = "viewing_menu"
            action_type = "menu_browsing"
        elif latest_action in ['action_book_table', 'action_confirm_booking']:
            new_context = "booking_process"
            action_type = "table_booking"
        elif latest_action in ['action_add_to_order', 'action_order_food']:
            new_context = "ordering_process"
            action_type = "food_ordering"
        elif intent_name in ['ask_dish_price', 'ask_dish_details']:
            action_type = "dish_inquiry"
        
        # Lưu lại món vừa được nhắc đến
        dish_name = tracker.get_slot('dish_name')
        last_mentioned_dishes = tracker.get_slot('last_mentioned_dishes') or []
        
        events = []
        if new_context:
            events.append(SlotSet("conversation_context", new_context))
        if action_type:
            events.append(SlotSet("last_action_type", action_type))
        if dish_name:
            events.append(SlotSet("last_mentioned_dish", dish_name))
            # Cập nhật danh sách các món đã nhắc đến
            if dish_name not in last_mentioned_dishes:
                last_mentioned_dishes.append(dish_name)
                # Giữ tối đa 5 món gần nhất
                if len(last_mentioned_dishes) > 5:
                    last_mentioned_dishes = last_mentioned_dishes[-5:]
                events.append(SlotSet("last_mentioned_dishes", last_mentioned_dishes))
        
        return events


class ActionSmartSuggestion(Action):
    """Action đưa ra gợi ý thông minh dựa vào context"""

    def name(self) -> Text:
        return "action_smart_suggestion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        conversation_context = tracker.get_slot('conversation_context')
        current_order = tracker.get_slot('current_order') or []
        has_table = tracker.get_slot('active_table_id') is not None
        last_mentioned_dish = tracker.get_slot('last_mentioned_dish')
        
        suggestions = []
        
        # Gợi ý dựa vào context hiện tại
        if conversation_context == "viewing_menu":
            suggestions.extend([
                "• **'Gọi [tên món]'** - Thêm món vào đơn hàng",
                "• **'Giá [tên món]'** - Xem giá món ăn",
                "• **'Món đặc biệt'** - Xem món nổi bật"
            ])
        
        elif conversation_context == "ordering_process":
            suggestions.extend([
                "• **'Xem đơn hàng'** - Kiểm tra những gì đã gọi",
                "• **'Thêm [tên món]'** - Gọi thêm món",
                "• **'Xác nhận đơn'** - Hoàn tất đơn hàng"
            ])
            
            if not has_table:
                suggestions.append("• **'Đặt bàn'** - Cần có bàn để lưu đơn hàng")
        
        elif conversation_context == "booking_process":
            suggestions.extend([
                "• **'Xác nhận'** - Hoàn tất đặt bàn",
                "• **'Sửa lại'** - Thay đổi thông tin đặt bàn"
            ])
        
        else:
            # Gợi ý chung
            suggestions.extend([
                "• **'Xem thực đơn'** - Duyệt các món ăn",
                "• **'Đặt bàn'** - Đặt chỗ ngồi",
                "• **'Giờ mở cửa'** - Xem thời gian hoạt động"
            ])
        
        # Gợi ý dựa vào món vừa nhắc đến
        if last_mentioned_dish:
            suggestions.insert(0, f"• **'Chi tiết {last_mentioned_dish}'** - Xem thông tin chi tiết")
        
        # Gợi ý dựa vào đơn hàng hiện tại
        if current_order:
            suggestions.insert(0, "• **'Món đó giá bao nhiêu?'** - Hỏi về món trong đơn hàng")
        
        if suggestions:
            suggestion_text = "💡 **Gợi ý cho bạn:**\n" + "\n".join(suggestions)
            dispatcher.utter_message(text=suggestion_text)
        
        return []