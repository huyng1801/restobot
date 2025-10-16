"""
Main Actions file for RestoBot
Import tất cả actions từ các modules
"""

import sys
import os
from typing import Any, Text, Dict, List

# Add current directory to Python path
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import Rasa SDK components
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Import all actions from modules
try:
    from modules.menu_actions import (
        ActionShowMenu,
        ActionAskDishDetails,
        ActionShowPopularDishes,
        ActionShowSpecialDishes
    )

    from modules.booking_actions import (
        ActionAskTableBookingInfo,
        ActionShowAvailableTables,
        ActionBookTable,
        ActionCancelReservation
    )

    from modules.confirmation_actions import (
        ActionConfirmBooking,
        ActionModifyBooking,
        ActionConfirmOrder
    )

    from modules.order_actions import (
        ActionAddToOrder,
        ActionViewCurrentOrder,
        ActionConfirmOrder,
        ActionCancelOrder
    )

    from modules.info_actions import (
        ActionShowOpeningHours,
        ActionShowAddress,
        ActionShowContact,
        ActionShowPromotions,
        ActionRecommendDishes
    )

    print("All action modules imported successfully!")

except ImportError as e:
    print(f"Import error: {e}")
    
    # Define basic fallback action if imports fail
    class ActionBookTable(Action):
        def name(self) -> Text:
            return "action_book_table"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            dispatcher.utter_message(text="Xin lỗi, hệ thống đặt bàn đang gặp sự cố. Vui lòng thử lại sau.")
            return []

# Export all actions để Rasa có thể tìm thấy
__all__ = [
    'ActionShowMenu',
    'ActionAskDishDetails', 
    'ActionShowPopularDishes',
    'ActionShowSpecialDishes',
    'ActionAskTableBookingInfo',
    'ActionShowAvailableTables',
    'ActionBookTable',
    'ActionCancelReservation',
    'ActionConfirmBooking',
    'ActionModifyBooking',
    'ActionConfirmOrder',
    'ActionAddToOrder',
    'ActionViewCurrentOrder',
    'ActionCancelOrder',
    'ActionShowOpeningHours',
    'ActionShowAddress',
    'ActionShowContact',
    'ActionShowPromotions',
    'ActionRecommendDishes'
]