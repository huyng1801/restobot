"""
Menu-related Actions for RestoBot
Xử lý các action liên quan đến menu và món ăn
"""
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .auth_helper import auth_helper

# URL của FastAPI backend
API_BASE_URL = "http://localhost:8000/api/v1"


class ActionShowMenu(Action):
    """Action để hiển thị thực đơn"""

    def name(self) -> Text:
        return "action_show_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            # Gọi API để lấy danh mục
            categories_response = requests.get(f"{API_BASE_URL}/menu/categories/", headers=headers, timeout=5)

            if categories_response.status_code == 200:
                categories = categories_response.json()
                message = "🍽️ **THỰC ĐƠN NHÀ HÀNG** 🍽️\n\n"

                for category in categories:
                    message += f"📂 **{category['name']}**\n"
                    if category.get('description'):
                        message += f"*{category['description']}*\n"

                    # Lấy món ăn theo danh mục
                    items_response = requests.get(
                        f"{API_BASE_URL}/menu/items/?category_id={category['id']}",
                        headers=headers,
                        timeout=5
                    )
                    if items_response.status_code == 200:
                        items = items_response.json()
                        for item in items[:3]:  # Chỉ hiển thị 3 món đầu mỗi danh mục
                            price_formatted = f"{item['price']:,.0f}đ" if item.get('price') else "Liên hệ"
                            message += f"   • {item['name']} - {price_formatted}\n"
                            if item['description']:
                                message += f"     _{item['description']}_\n"
                        if len(items) > 3:
                            message += f"     ... và {len(items) - 3} món khác\n"
                    message += "\n"

                message += "💡 **Cách gọi món:**\n"
                message += "- Nói: 'Tôi muốn gọi [tên món]'\n"
                message += "- Hoặc: 'Cho tôi 2 phần [tên món]'\n"
                message += "- Ví dụ: 'Tôi muốn gọi phở bò'\n\n"
                message += "❓ Bạn có thể hỏi giá hoặc chi tiết món nào bạn quan tâm!"
            else:
                message = "❌ Xin lỗi, hiện tại không thể tải thực đơn. Vui lòng thử lại sau."

        except requests.exceptions.Timeout:
            message = "⏱️ Kết nối chậm. Vui lòng thử lại sau."
        except requests.exceptions.RequestException as e:
            message = f"❌ Có lỗi xảy ra khi tải thực đơn. Vui lòng thử lại sau."
            print(f"Error in ActionShowMenu: {e}")
        except Exception as e:
            message = f"❌ Có lỗi bất ngờ xảy ra khi tải thực đơn. Vui lòng liên hệ hỗ trợ."
            print(f"Unexpected error in ActionShowMenu: {e}")

        dispatcher.utter_message(text=message)
        return []


class ActionAskDishDetails(Action):
    """Action để hỏi chi tiết món ăn"""

    def name(self) -> Text:
        return "action_ask_dish_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        dish_name = None
        
        # Lấy tên món từ entity hoặc slot
        for entity in tracker.latest_message.get('entities', []):
            if entity['entity'] == 'dish_name':
                dish_name = entity['value']
                break
        
        if not dish_name:
            dish_name = tracker.get_slot("last_mentioned_dish")
            
        if not dish_name:
            dispatcher.utter_message(text="Bạn muốn hỏi về món nào? Vui lòng cho tôi biết tên món ăn.")
            return []
            
        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            # Tìm món trong menu
            response = requests.get(f"{API_BASE_URL}/menu/items/search?q={dish_name}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    item = items[0]  # Lấy kết quả đầu tiên
                    
                    price_formatted = f"{item['price']:,.0f}đ" if item.get('price') else "Liên hệ"
                    message = f"🍽️ **{item['name']}**\n\n"
                    message += f"💰 Giá: {price_formatted}\n"
                    
                    if item['description']:
                        message += f"📝 Mô tả: {item['description']}\n"
                        
                    if item.get('preparation_time'):
                        message += f"⏱️ Thời gian chuẩn bị: {item['preparation_time']} phút\n"
                    
                    if item.get('category') and item['category'].get('name'):
                        message += f"📂 Danh mục: {item['category']['name']}\n"
                    
                    message += f"\n💡 Bạn có muốn gọi món này không?"
                    
                    return [SlotSet("last_mentioned_dish", item['name'])]
                else:
                    message = f"Xin lỗi, không tìm thấy món '{dish_name}' trong thực đơn. Bạn có thể xem thực đơn để chọn món khác."
                    
            else:
                message = "Không thể tìm kiếm thông tin món ăn. Vui lòng thử lại sau."
                
        except requests.exceptions.Timeout:
            message = "⏱️ Kết nối chậm. Vui lòng thử lại sau."
        except requests.exceptions.RequestException as e:
            message = f"❌ Có lỗi xảy ra khi tìm kiếm thông tin món ăn."
            print(f"Error in ActionAskDishDetails: {e}")
        except Exception as e:
            message = f"❌ Có lỗi bất ngờ xảy ra khi tìm kiếm thông tin món ăn."
            print(f"Unexpected error in ActionAskDishDetails: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionShowPopularDishes(Action):
    """Action để hiển thị món phổ biến"""

    def name(self) -> Text:
        return "action_show_popular_dishes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            # Gọi API lấy món featured (được đánh dấu phổ biến)
            response = requests.get(f"{API_BASE_URL}/menu/items/featured", headers=headers, timeout=5)
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    message = "🌟 **MÓN ĂN PHỔ BIẾN**\n\n"
                    
                    for item in items:
                        price_formatted = f"{item['price']:,.0f}đ" if item.get('price') else "Liên hệ"
                        message += f"⭐ **{item['name']}** - {price_formatted}\n"
                        if item['description']:
                            message += f"   _{item['description']}_\n"
                        message += "\n"
                    
                    message += "💡 Bạn có muốn gọi món nào không?"
                    
                else:
                    message = "Hiện tại chúng tôi đang cập nhật danh sách món phổ biến."
                    
            else:
                message = "Không thể tải danh sách món phổ biến. Vui lòng thử lại sau."
                
        except requests.exceptions.Timeout:
            message = "⏱️ Kết nối chậm. Vui lòng thử lại sau."
        except requests.exceptions.RequestException as e:
            message = f"❌ Có lỗi xảy ra khi tải món phổ biến."
            print(f"Error in ActionShowPopularDishes: {e}")
        except Exception as e:
            message = f"❌ Có lỗi bất ngờ xảy ra khi tải món phổ biến."
            print(f"Unexpected error in ActionShowPopularDishes: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionShowSpecialDishes(Action):
    """Action để hiển thị món đặc biệt"""

    def name(self) -> Text:
        return "action_show_special_dishes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        # Tạm thời trả về featured dishes
        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            response = requests.get(f"{API_BASE_URL}/menu/items/featured", headers=headers, timeout=5)
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    message = "🍽️ **MÓN ĐẶC BIỆT HÔM NAY**\n\n"
                    
                    for item in items:
                        price_formatted = f"{item['price']:,.0f}đ" if item.get('price') else "Liên hệ"
                        message += f"✨ **{item['name']}** - {price_formatted}\n"
                        if item['description']:
                            message += f"   _{item['description']}_\n"
                        if item.get('preparation_time'):
                            message += f"   ⏱️ Thời gian: {item['preparation_time']} phút\n"
                        message += "\n"
                    
                    message += "💡 Đây là những món đặc biệt được đầu bếp khuyến nghị!"
                    
                else:
                    message = "Hôm nay chúng tôi không có món đặc biệt. Bạn có thể xem thực đơn thường."
                    
            else:
                message = "Không thể tải món đặc biệt. Vui lòng thử lại sau."
                
        except requests.exceptions.Timeout:
            message = "⏱️ Kết nối chậm. Vui lòng thử lại sau."
        except requests.exceptions.RequestException as e:
            message = f"❌ Có lỗi xảy ra khi tải món đặc biệt."
            print(f"Error in ActionShowSpecialDishes: {e}")
        except Exception as e:
            message = f"❌ Có lỗi bất ngờ xảy ra khi tải món đặc biệt."
            print(f"Unexpected error in ActionShowSpecialDishes: {e}")
        
        dispatcher.utter_message(text=message)
        return []