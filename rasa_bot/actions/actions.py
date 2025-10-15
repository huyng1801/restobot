"""
Custom actions cho Rasa chatbot
Các actions này sẽ tương tác với FastAPI backend
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import json
from datetime import datetime, timedelta

# URL của FastAPI backend
API_BASE_URL = "http://localhost:8000/api/v1"

class ActionShowMenu(Action):
    """Action để hiển thị thực đơn"""
    
    def name(self) -> Text:
        return "action_show_menu"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Gọi API để lấy danh mục
            categories_response = requests.get(f"{API_BASE_URL}/menu/categories/")
            
            if categories_response.status_code == 200:
                categories = categories_response.json()
                
                message = "🍽️ **THỰC ĐƠN NHÀ HÀNG** 🍽️\n\n"
                
                for category in categories:
                    message += f"📂 **{category['name']}**\n"
                    
                    # Lấy món ăn theo danh mục
                    items_response = requests.get(f"{API_BASE_URL}/menu/items/?category_id={category['id']}")
                    
                    if items_response.status_code == 200:
                        items = items_response.json()
                        
                        for item in items[:3]:  # Chỉ hiển thị 3 món đầu mỗi danh mục
                            price_formatted = f"{item['price']:,.0f}đ"
                            message += f"   • {item['name']} - {price_formatted}\n"
                            if item['description']:
                                message += f"     _{item['description']}_\n"
                        
                        if len(items) > 3:
                            message += f"     ... và {len(items) - 3} món khác\n"
                    
                    message += "\n"
                
                message += "💡 Bạn có thể hỏi chi tiết về món nào bạn quan tâm!"
                
            else:
                message = "Xin lỗi, hiện tại không thể tải thực đơn. Vui lòng thử lại sau."
                
        except Exception as e:
            message = "Có lỗi xảy ra khi tải thực đơn. Vui lòng thử lại sau."
            print(f"Error in ActionShowMenu: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionShowAvailableTables(Action):
    """Action để hiển thị bàn trống"""
    
    def name(self) -> Text:
        return "action_show_available_tables"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Lấy số người từ slot
            number_of_people = tracker.get_slot("number_of_people")
            
            # Gọi API để lấy bàn trống
            params = {}
            if number_of_people:
                params["min_capacity"] = int(number_of_people)
            
            response = requests.get(f"{API_BASE_URL}/tables/available", params=params)
            
            if response.status_code == 200:
                tables = response.json()
                
                if tables:
                    message = f"🪑 **CÁC BÀN TRỐNG**\n\n"
                    
                    for table in tables:
                        message += f"• Bàn {table['table_number']} - {table['capacity']} chỗ"
                        if table['location']:
                            message += f" ({table['location']})"
                        message += "\n"
                    
                    message += f"\nCó {len(tables)} bàn phù hợp với yêu cầu của bạn."
                    
                else:
                    message = "Xin lỗi, hiện tại không có bàn trống phù hợp."
                    
            else:
                message = "Không thể kiểm tra bàn trống. Vui lòng thử lại sau."
                
        except Exception as e:
            message = "Có lỗi xảy ra khi kiểm tra bàn trống."
            print(f"Error in ActionShowAvailableTables: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionBookTable(Action):
    """Action để đặt bàn"""
    
    def name(self) -> Text:
        return "action_book_table"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Lấy thông tin từ slots
            number_of_people = tracker.get_slot("number_of_people")
            reservation_date = tracker.get_slot("reservation_date")
            reservation_time = tracker.get_slot("reservation_time")
            
            # Kiểm tra thông tin đầy đủ
            if not all([number_of_people, reservation_date, reservation_time]):
                dispatcher.utter_message(text="Vui lòng cung cấp đầy đủ thông tin: số người, ngày và giờ đặt bàn.")
                return []
            
            # Tìm bàn phù hợp
            response = requests.get(f"{API_BASE_URL}/tables/available?min_capacity={int(number_of_people)}")
            
            if response.status_code == 200:
                available_tables = response.json()
                
                if available_tables:
                    # Chọn bàn đầu tiên phù hợp
                    selected_table = available_tables[0]
                    
                    # Tạo reservation data
                    reservation_data = {
                        "table_id": selected_table["id"],
                        "party_size": int(number_of_people),
                        "reservation_date": f"{reservation_date} {reservation_time}",
                        "special_requests": ""
                    }
                    
                    # Gọi API tạo reservation
                    create_response = requests.post(
                        f"{API_BASE_URL}/orders/reservations/",
                        json=reservation_data
                    )
                    
                    if create_response.status_code == 200:
                        reservation = create_response.json()
                        
                        message = f"✅ **ĐẶT BÀN THÀNH CÔNG!**\n\n"
                        message += f"📋 Mã đặt bàn: #{reservation['id']}\n"
                        message += f"🪑 Bàn: {selected_table['table_number']}\n"
                        message += f"👥 Số người: {number_of_people}\n"
                        message += f"📅 Thời gian: {reservation_time} - {reservation_date}\n"
                        message += f"📍 Vị trí: {selected_table['location']}\n\n"
                        message += "Chúng tôi sẽ giữ bàn cho bạn. Vui lòng đến đúng giờ!"
                        
                        # Reset slots
                        return [
                            SlotSet("number_of_people", None),
                            SlotSet("reservation_date", None),
                            SlotSet("reservation_time", None)
                        ]
                        
                    else:
                        message = "Có lỗi xảy ra khi đặt bàn. Vui lòng thử lại."
                        
                else:
                    message = f"Xin lỗi, không có bàn trống cho {number_of_people} người vào thời gian bạn yêu cầu."
                    
            else:
                message = "Không thể kiểm tra bàn trống. Vui lòng thử lại sau."
                
        except Exception as e:
            message = "Có lỗi xảy ra trong quá trình đặt bàn. Vui lòng thử lại sau."
            print(f"Error in ActionBookTable: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionAddToOrder(Action):
    """Action để thêm món vào đơn hàng"""
    
    def name(self) -> Text:
        return "action_add_to_order"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Lấy thông tin món từ entities
            dish_name = None
            quantity = 1
            
            # Tìm dish_name trong entities
            for entity in tracker.latest_message.get('entities', []):
                if entity['entity'] == 'dish_name':
                    dish_name = entity['value']
                elif entity['entity'] == 'quantity':
                    quantity = int(entity['value'])
            
            if not dish_name:
                dispatcher.utter_message(text="Bạn muốn gọi món gì? Vui lòng cho tôi biết tên món ăn.")
                return []
            
            # Tìm món trong menu
            response = requests.get(f"{API_BASE_URL}/menu/items/search?q={dish_name}")
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    item = items[0]  # Lấy kết quả đầu tiên
                    
                    # Lấy đơn hàng hiện tại từ slot
                    current_order = tracker.get_slot("current_order") or []
                    
                    # Thêm món vào đơn
                    order_item = {
                        "menu_item_id": item["id"],
                        "name": item["name"],
                        "price": item["price"],
                        "quantity": quantity,
                        "total": item["price"] * quantity
                    }
                    
                    # Kiểm tra xem món đã có trong đơn chưa
                    found = False
                    for existing_item in current_order:
                        if existing_item["menu_item_id"] == item["id"]:
                            existing_item["quantity"] += quantity
                            existing_item["total"] = existing_item["price"] * existing_item["quantity"]
                            found = True
                            break
                    
                    if not found:
                        current_order.append(order_item)
                    
                    price_formatted = f"{item['price']:,.0f}đ"
                    total_formatted = f"{order_item['total']:,.0f}đ"
                    
                    message = f"✅ Đã thêm **{quantity} phần {item['name']}** vào đơn hàng\n"
                    message += f"💰 Giá: {price_formatted} x {quantity} = {total_formatted}"
                    
                    return [SlotSet("current_order", current_order)]
                    
                else:
                    message = f"Xin lỗi, không tìm thấy món '{dish_name}' trong thực đơn. Bạn có thể xem thực đơn để chọn món khác."
                    
            else:
                message = "Không thể tìm kiếm món ăn. Vui lòng thử lại sau."
                
        except Exception as e:
            message = "Có lỗi xảy ra khi thêm món vào đơn hàng."
            print(f"Error in ActionAddToOrder: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionShowCurrentOrder(Action):
    """Action để hiển thị đơn hàng hiện tại"""
    
    def name(self) -> Text:
        return "action_show_current_order"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_order = tracker.get_slot("current_order") or []
        
        if not current_order:
            message = "🛒 Đơn hàng của bạn đang trống. Hãy chọn món từ thực đơn!"
        else:
            message = "🛒 **ĐƠN HÀNG HIỆN TẠI**\n\n"
            total_amount = 0
            
            for i, item in enumerate(current_order, 1):
                item_total = item["price"] * item["quantity"]
                total_amount += item_total
                
                price_formatted = f"{item['price']:,.0f}đ"
                total_formatted = f"{item_total:,.0f}đ"
                
                message += f"{i}. **{item['name']}**\n"
                message += f"   Số lượng: {item['quantity']} x {price_formatted} = {total_formatted}\n\n"
            
            total_formatted = f"{total_amount:,.0f}đ"
            message += f"💰 **Tổng cộng: {total_formatted}**\n\n"
            message += "Bạn có muốn xác nhận đơn hàng này không?"
        
        dispatcher.utter_message(text=message)
        return []


class ActionConfirmOrder(Action):
    """Action để xác nhận đơn hàng"""
    
    def name(self) -> Text:
        return "action_confirm_order"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            current_order = tracker.get_slot("current_order") or []
            
            if not current_order:
                dispatcher.utter_message(text="Không có món nào trong đơn hàng để xác nhận.")
                return []
            
            # Tạo order data
            order_items = []
            for item in current_order:
                order_items.append({
                    "menu_item_id": item["menu_item_id"],
                    "quantity": item["quantity"],
                    "special_instructions": ""
                })
            
            order_data = {
                "order_items": order_items,
                "notes": ""
            }
            
            # Gọi API tạo order
            response = requests.post(f"{API_BASE_URL}/orders/orders/", json=order_data)
            
            if response.status_code == 200:
                order = response.json()
                
                message = f"✅ **ĐƠN HÀNG ĐÃ ĐƯỢC XÁC NHẬN!**\n\n"
                message += f"📋 Mã đơn hàng: #{order['order_number']}\n"
                message += f"💰 Tổng tiền: {order['total_amount']:,.0f}đ\n"
                message += f"🕐 Thời gian chuẩn bị ước tính: 15-25 phút\n\n"
                message += "Cảm ơn bạn đã đặt hàng! Đơn hàng sẽ được chuẩn bị ngay."
                
                # Xóa đơn hàng hiện tại
                return [SlotSet("current_order", [])]
                
            else:
                message = "Có lỗi xảy ra khi xác nhận đơn hàng. Vui lòng thử lại."
                
        except Exception as e:
            message = "Có lỗi xảy ra trong quá trình xác nhận đơn hàng."
            print(f"Error in ActionConfirmOrder: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionShowPopularDishes(Action):
    """Action để hiển thị món phổ biến"""
    
    def name(self) -> Text:
        return "action_show_popular_dishes"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Gọi API lấy món featured (được đánh dấu phổ biến)
            response = requests.get(f"{API_BASE_URL}/menu/items/featured")
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    message = "🌟 **MÓN ĂN PHỔ BIẾN**\n\n"
                    
                    for item in items:
                        price_formatted = f"{item['price']:,.0f}đ"
                        message += f"⭐ **{item['name']}** - {price_formatted}\n"
                        if item['description']:
                            message += f"   _{item['description']}_\n"
                        message += "\n"
                    
                    message += "💡 Bạn có muốn gọi món nào không?"
                    
                else:
                    message = "Hiện tại chúng tôi đang cập nhật danh sách món phổ biến."
                    
            else:
                message = "Không thể tải danh sách món phổ biến. Vui lòng thử lại sau."
                
        except Exception as e:
            message = "Có lỗi xảy ra khi tải món phổ biến."
            print(f"Error in ActionShowPopularDishes: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionShowSpecialDishes(Action):
    """Action để hiển thị món đặc biệt"""
    
    def name(self) -> Text:
        return "action_show_special_dishes"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Tạm thời trả về featured dishes
        try:
            response = requests.get(f"{API_BASE_URL}/menu/items/featured")
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    message = "🍽️ **MÓN ĐẶC BIỆT HÔM NAY**\n\n"
                    
                    for item in items:
                        price_formatted = f"{item['price']:,.0f}đ"
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
                
        except Exception as e:
            message = "Có lỗi xảy ra khi tải món đặc biệt."
            print(f"Error in ActionShowSpecialDishes: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionAskDishDetails(Action):
    """Action để hỏi chi tiết món ăn"""
    
    def name(self) -> Text:
        return "action_ask_dish_details"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Lấy tên món từ entity hoặc slot
            dish_name = None
            for entity in tracker.latest_message.get('entities', []):
                if entity['entity'] == 'dish_name':
                    dish_name = entity['value']
                    break
            
            if not dish_name:
                dish_name = tracker.get_slot("last_mentioned_dish")
            
            if not dish_name:
                dispatcher.utter_message(text="Bạn muốn hỏi về món nào? Vui lòng cho tôi biết tên món ăn.")
                return []
            
            # Tìm món trong menu
            response = requests.get(f"{API_BASE_URL}/menu/items/search?q={dish_name}")
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    item = items[0]
                    
                    price_formatted = f"{item['price']:,.0f}đ"
                    
                    message = f"🍽️ **{item['name']}**\n\n"
                    message += f"💰 Giá: {price_formatted}\n"
                    
                    if item['description']:
                        message += f"📝 Mô tả: {item['description']}\n"
                    
                    if item.get('preparation_time'):
                        message += f"⏱️ Thời gian chuẩn bị: {item['preparation_time']} phút\n"
                    
                    if item.get('category'):
                        message += f"📂 Danh mục: {item['category']['name']}\n"
                    
                    message += f"\n💡 Bạn có muốn gọi món này không?"
                    
                    return [SlotSet("last_mentioned_dish", item['name'])]
                    
                else:
                    message = f"Xin lỗi, không tìm thấy món '{dish_name}' trong thực đơn."
                    
            else:
                message = "Không thể tìm kiếm thông tin món ăn. Vui lòng thử lại sau."
                
        except Exception as e:
            message = "Có lỗi xảy ra khi tìm kiếm thông tin món ăn."
            print(f"Error in ActionAskDishDetails: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionCancelReservation(Action):
    """Action để hủy đặt bàn"""
    
    def name(self) -> Text:
        return "action_cancel_reservation"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "Để hủy đặt bàn, bạn vui lòng cung cấp:\n"
        message += "• Mã đặt bàn\n"
        message += "• Tên người đặt\n"
        message += "• Số điện thoại\n\n"
        message += "Hoặc bạn có thể gọi trực tiếp: (028) 3123 4567"
        
        dispatcher.utter_message(text=message)
        return []