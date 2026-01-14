"""
Utility Actions for RestoBot
Các action tiện ích
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionDenyRequest(Action):
    """Action để xử lý từ chối"""

    def name(self) -> Text:
        return "action_deny_request"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(response="utter_deny_request")
        return []


class ActionHandleError(Action):
    """Action để xử lý lỗi"""

    def name(self) -> Text:
        return "action_handle_error"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(response="utter_error")
        return []