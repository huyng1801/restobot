"""
Enhanced Order Confirmation Action for RestoBot
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import requests
from .auth_helper import get_authenticated_user_from_tracker, get_auth_headers_from_tracker

API_BASE_URL = "http://api:8000/api/v1"


class ActionConfirmOrderItem(Action):
    """Action để xác nhận món ăn trước khi thêm vào đơn hàng"""

    def name(self) -> Text:
        return "action_confirm_order_item"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        pending_item = tracker.get_slot("pending_order_item")
        
        if not pending_item:
            dispatcher.utter_message(text="❌ Không có món nào để xác nhận.")
            return []
        
        # Get user confirmation from latest message
        latest_intent = tracker.latest_message['intent']['name']
        
        if latest_intent == 'affirm':
            # User confirmed, proceed to add item
            dispatcher.utter_message(text=f"✅ Đã xác nhận: **{pending_item['dish_name']}**\nĐang thêm vào đơn hàng...")
            
            return [
                SlotSet("dish_name", pending_item['dish_name']),
                SlotSet("current_dish_quantity", pending_item.get('quantity', 1)),
                SlotSet("pending_order_item", None),
                SlotSet("conversation_context", None),
                FollowupAction("action_add_to_order")
            ]
        
        elif latest_intent == 'deny':
            # User denied, ask for correct dish name
            dispatcher.utter_message(text="❌ Đã hủy. Vui lòng cho biết tên món chính xác bạn muốn gọi.")
            return [
                SlotSet("pending_order_item", None),
                SlotSet("conversation_context", None)
            ]
        
        else:
            # Unclear response, ask again
            dispatcher.utter_message(text=f"🤔 Bạn có muốn gọi **{pending_item['dish_name']}** không?\n💡 Nói 'Có' hoặc 'Không'.")
            return []


class ActionSelectDishByNumber(Action):
    """Action để chọn món từ danh sách gợi ý bằng số"""

    def name(self) -> Text:
        return "action_select_dish_by_number"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        suggested_dishes = tracker.get_slot("suggested_dishes") or []
        latest_message = tracker.latest_message.get('text', '')
        
        if not suggested_dishes:
            dispatcher.utter_message(text="❌ Không có danh sách món nào để chọn.")
            return []
        
        # Extract number from message
        import re
        number_match = re.search(r'món số (\d+)|số (\d+)|(\d+)', latest_message.lower())
        
        if number_match:
            try:
                number = int(number_match.group(1) or number_match.group(2) or number_match.group(3))
                
                if 1 <= number <= len(suggested_dishes):
                    selected_dish = suggested_dishes[number - 1]
                    dispatcher.utter_message(text=f"✅ Bạn đã chọn: **{selected_dish}**\nĐang thêm vào đơn hàng...")
                    
                    return [
                        SlotSet("dish_name", selected_dish),
                        SlotSet("suggested_dishes", None),
                        FollowupAction("action_add_to_order")
                    ]
                else:
                    dispatcher.utter_message(text=f"❌ Số {number} không hợp lệ. Vui lòng chọn từ 1 đến {len(suggested_dishes)}.")
                    return []
                    
            except ValueError:
                pass
        
        dispatcher.utter_message(text="❌ Không hiểu số bạn chọn. Vui lòng nói 'Món số [1-5]' hoặc tên món chính xác.")
        return []