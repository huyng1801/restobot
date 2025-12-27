"""
Menu-related Actions for RestoBot
Xử lý các action liên quan đến menu và món ăn
"""
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from .auth_helper import auth_helper, get_auth_headers_from_tracker

# URL của FastAPI backend
API_BASE_URL = "http://103.56.160.107:8000/api/v1"


class ActionShowMenu(Action):
    """Action để hiển thị thực đơn"""

    def name(self) -> Text:
        return "action_show_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        dishes_list = []
        
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Gọi API để lấy danh mục
            categories_response = requests.get(f"{API_BASE_URL}/menu/categories/", headers=headers, timeout=5)

            if categories_response.status_code == 200:
                categories_data = categories_response.json()
                # Xử lý response format từ API (có thể là paginated)
                if isinstance(categories_data, dict) and 'items' in categories_data:
                    categories = categories_data['items']
                else:
                    categories = categories_data
                    
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
                        items_data = items_response.json()
                        # Xử lý response format từ API (có thể là paginated)
                        if isinstance(items_data, dict) and 'items' in items_data:
                            items = items_data['items']
                        else:
                            items = items_data
                        
                        # Thêm tất cả món vào danh sách
                        for item in items:
                            dishes_list.append({
                                'name': item['name'],
                                'price': item.get('price'),
                                'description': item.get('description'),
                                'image_url': item.get('image_url'),
                                'preparation_time': item.get('preparation_time'),
                                'category': category['name']
                            })
                        
                        item_count = len(items)
                        message += f"   {item_count} món ăn\n"
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

        # Gửi message với custom data chứa danh sách món
        dispatcher.utter_message(text=message, custom={'dishes': dishes_list})
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
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

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
                    
                    # Gửi hình ảnh nếu có
                    if item.get('image_url'):
                        dispatcher.utter_message(image=item['image_url'])
                    
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
        dishes_list = []
        
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Gọi API lấy món featured (được đánh dấu phổ biến)
            response = requests.get(f"{API_BASE_URL}/menu/items/featured", headers=headers, timeout=5)
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    message = "🌟 **MÓN ĂN PHỔ BIẾN**\n\n"
                    
                    for item in items:
                        dishes_list.append({
                            'name': item['name'],
                            'price': item.get('price'),
                            'description': item.get('description'),
                            'image_url': item.get('image_url'),
                            'preparation_time': item.get('preparation_time'),
                            'category': item.get('category', {}).get('name') if item.get('category') else None
                        })
                    
                    message += f"Hiển thị {len(items)} món phổ biến nhất\n\n"
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
        
        dispatcher.utter_message(text=message, custom={'dishes': dishes_list})
        return []


class ActionShowSpecialDishes(Action):
    """Action để hiển thị món đặc biệt"""

    def name(self) -> Text:
        return "action_show_special_dishes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        dishes_list = []
        
        # Tạm thời trả về featured dishes
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            response = requests.get(f"{API_BASE_URL}/menu/items/featured", headers=headers, timeout=5)
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    message = "🍽️ **MÓN ĐẶC BIỆT HÔM NAY**\n\n"
                    
                    for item in items:
                        dishes_list.append({
                            'name': item['name'],
                            'price': item.get('price'),
                            'description': item.get('description'),
                            'image_url': item.get('image_url'),
                            'preparation_time': item.get('preparation_time'),
                            'category': item.get('category', {}).get('name') if item.get('category') else None
                        })
                    
                    message += f"Hiển thị {len(items)} món đặc biệt\n\n"
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
        
        dispatcher.utter_message(text=message, custom={'dishes': dishes_list})
        return []


class ActionAskDishPrice(Action):
    """Action để hỏi giá món ăn"""

    def name(self) -> Text:
        return "action_ask_dish_price"

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
            dispatcher.utter_message(text="Bạn muốn hỏi giá món nào? Vui lòng cho tôi biết tên món ăn.")
            return []
            
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Tìm món trong menu
            response = requests.get(f"{API_BASE_URL}/menu/items/search?q={dish_name}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                items = response.json()
                
                if items:
                    if len(items) == 1:
                        # Chỉ có 1 món khớp
                        item = items[0]
                        price_formatted = f"{item['price']:,.0f}đ" if item.get('price') else "Liên hệ"
                        
                        message = f"💰 **Giá {item['name']}: {price_formatted}**"
                        
                        if item.get('preparation_time'):
                            message += f"\n⏱️ Thời gian chuẩn bị: {item['preparation_time']} phút"
                        
                        message += f"\n\n💡 Bạn có muốn gọi món này không?"
                        
                        return [SlotSet("last_mentioned_dish", item['name'])]
                        
                    else:
                        # Nhiều món khớp - hiển thị danh sách
                        message = f"💰 **Giá các món có tên '{dish_name}':**\n\n"
                        
                        for item in items[:5]:  # Chỉ hiển thị 5 món đầu
                            price_formatted = f"{item['price']:,.0f}đ" if item.get('price') else "Liên hệ"
                            message += f"• **{item['name']}** - {price_formatted}\n"
                            if item.get('category', {}).get('name'):
                                message += f"  _{item['category']['name']}_\n"
                        
                        if len(items) > 5:
                            message += f"\n... và {len(items) - 5} món khác"
                        
                        message += "\n\n💡 **Để biết chi tiết:** Nói 'chi tiết [tên món cụ thể]'"
                else:
                    message = f"❌ Không tìm thấy món '{dish_name}' trong thực đơn.\n\n"
                    message += "💡 **Gợi ý:**\n"
                    message += "• Nói 'xem thực đơn' để xem tất cả món\n"
                    message += "• Nói 'món phổ biến' để xem món được yêu thích\n"
                    message += "• Nói 'gợi ý món ăn' để được tư vấn"
                    
            else:
                message = "❌ Không thể tra cứu giá món. Vui lòng thử lại sau."
                
        except requests.exceptions.Timeout:
            message = "⏱️ Kết nối chậm. Vui lòng thử lại sau."
        except requests.exceptions.RequestException as e:
            message = f"❌ Có lỗi xảy ra khi tra cứu giá món."
            print(f"Error in ActionAskDishPrice: {e}")
        except Exception as e:
            message = f"❌ Có lỗi bất ngờ xảy ra khi tra cứu giá món."
            print(f"Unexpected error in ActionAskDishPrice: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionShowBestsellerDishes(Action):
    """Action để hiển thị món bán chạy nhất dựa vào order_items"""

    def name(self) -> Text:
        return "action_show_bestseller_dishes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        dishes_list = []
        
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Gọi API lấy thống kê món bán chạy từ orders
            response = requests.get(f"{API_BASE_URL}/orders/analytics/bestsellers", headers=headers, timeout=5)
            
            if response.status_code == 200:
                bestsellers = response.json()
                
                if bestsellers:
                    message = "🔥 **MÓN BÁN CHẠY NHẤT**\n\n"
                    
                    for idx, item in enumerate(bestsellers[:5], 1):  # Top 5
                        # Lấy thông tin chi tiết món ăn
                        item_response = requests.get(f"{API_BASE_URL}/menu/items/{item['menu_item_id']}", headers=headers, timeout=5)
                        if item_response.status_code == 200:
                            item_detail = item_response.json()
                            total_sold = item.get('total_quantity', 0)
                            
                            dishes_list.append({
                                'name': item_detail['name'],
                                'price': item_detail.get('price'),
                                'description': f"{item_detail.get('description', '')} - Đã bán: {total_sold} suất",
                                'image_url': item_detail.get('image_url'),
                                'preparation_time': item_detail.get('preparation_time'),
                                'category': item_detail.get('category', {}).get('name') if item_detail.get('category') else None
                            })
                    
                    message += f"Top {len(dishes_list)} món bán chạy nhất\n\n"
                    message += "💡 Đây là những món được khách hàng yêu thích nhất!"
                    
                else:
                    # Fallback về featured dishes nếu chưa có dữ liệu bán hàng
                    featured_response = requests.get(f"{API_BASE_URL}/menu/items/featured", headers=headers, timeout=5)
                    if featured_response.status_code == 200:
                        featured_items = featured_response.json()
                        
                        if featured_items:
                            message = "🌟 **MÓN ĐƯỢC ĐỀ XUẤT** (Chưa có dữ liệu bán hàng)\n\n"
                            
                            for item in featured_items[:3]:
                                dishes_list.append({
                                    'name': item['name'],
                                    'price': item.get('price'),
                                    'description': item.get('description'),
                                    'image_url': item.get('image_url'),
                                    'preparation_time': item.get('preparation_time'),
                                    'category': item.get('category', {}).get('name') if item.get('category') else None
                                })
                                
                            message += "💡 Đây là những món được đầu bếp khuyến nghị!"
                        else:
                            message = "Hiện tại chúng tôi đang thu thập dữ liệu về món bán chạy. Bạn có thể xem thực đơn hoặc hỏi gợi ý món ăn."
                    else:
                        message = "Hiện tại chúng tôi đang thu thập dữ liệu về món bán chạy. Bạn có thể xem thực đơn hoặc hỏi gợi ý món ăn."
                        
            else:
                # Fallback về featured dishes
                featured_response = requests.get(f"{API_BASE_URL}/menu/items/featured", headers=headers, timeout=5)
                if featured_response.status_code == 200:
                    featured_items = featured_response.json()
                    
                    if featured_items:
                        message = "🌟 **MÓN ĐƯỢC ĐỀ XUẤT**\n\n"
                        
                        for item in featured_items[:3]:
                            dishes_list.append({
                                'name': item['name'],
                                'price': item.get('price'),
                                'description': item.get('description'),
                                'image_url': item.get('image_url'),
                                'preparation_time': item.get('preparation_time'),
                                'category': item.get('category', {}).get('name') if item.get('category') else None
                            })
                            
                        message += "💡 Đây là những món được đầu bếp khuyến nghị!"
                    else:
                        message = "Hiện tại không thể tải dữ liệu món bán chạy. Bạn có thể xem thực đơn hoặc hỏi gợi ý món ăn."
                else:
                    message = "Hiện tại không thể tải dữ liệu món bán chạy. Bạn có thể xem thực đơn hoặc hỏi gợi ý món ăn."
                
        except requests.exceptions.Timeout:
            message = "⏱️ Kết nối chậm. Vui lòng thử lại sau."
        except requests.exceptions.RequestException as e:
            message = f"❌ Có lỗi xảy ra khi tải món bán chạy."
            print(f"Error in ActionShowBestsellerDishes: {e}")
        except Exception as e:
            message = f"❌ Có lỗi bất ngờ xảy ra khi tải món bán chạy."
            print(f"Unexpected error in ActionShowBestsellerDishes: {e}")
        
        dispatcher.utter_message(text=message, custom={'dishes': dishes_list})
        return []