"""
Order Management Actions for RestoBot
Xử lý các action liên quan đến đặt món và quản lý đơn hàng
"""
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .auth_helper import auth_helper, get_authenticated_user_from_tracker, get_auth_headers_from_tracker

# URL của FastAPI backend (dùng Docker internal network)
API_BASE_URL = "http://api:8000/api/v1"

class ActionAddToOrder(Action):
    """Action để thêm món vào đơn hàng"""

    def name(self) -> Text:
        return "action_add_to_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        dish_name = None
        quantity = 1 # Default quantity

        # Import auth functions
        from .auth_helper import get_authenticated_user_from_tracker, get_auth_headers_from_tracker
        
        # Lấy thông tin user đã xác thực từ tracker
        authenticated_user = get_authenticated_user_from_tracker(tracker)
        
        # Nếu không có user đã xác thực, yêu cầu đăng nhập
        if not authenticated_user:
            dispatcher.utter_message(text="""🔐 **ĐĂNG NHẬP YÊU CẦU**
            
Để gọi món, bạn cần đăng nhập vào hệ thống.

📱 **Các bước:**
1. Nhấn **"Đăng nhập"** ở góc trên
2. Nhập tài khoản và mật khẩu
3. Quay lại chat để gọi món

💡 **Tại sao cần đăng nhập?**
• Lưu đơn hàng của bạn
• Xem lịch sử đặt món
• Nhận ưu đãi đặc biệt

🚀 Sau khi đăng nhập, hãy thử lại: "Tôi muốn gọi [tên món]" """)
            return []

        try:
            # Lấy thông tin món từ entities
            for entity in tracker.latest_message.get('entities', []):
                if entity['entity'] == 'dish_name':
                    dish_name = entity['value']
                elif entity['entity'] == 'quantity':
                    try:
                        quantity = int(entity['value'])
                    except ValueError:
                        quantity = 1 # Fallback if quantity is not a valid number
            
            if not dish_name:
                dispatcher.utter_message(text="Bạn muốn gọi món gì? Vui lòng cho tôi biết tên món ăn.")
                return []
            
            # Sử dụng auth headers từ user token, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)
            
            # Kiểm tra user có reservation active không - sử dụng endpoint my reservations
            reservations_response = requests.get(
                f"{API_BASE_URL}/orders/reservations/my", 
                headers=headers, 
                timeout=5
            )
            
            active_reservation = None
            if reservations_response.status_code == 200:
                reservations_data = reservations_response.json()
                # API trả về list trực tiếp
                reservations = reservations_data if isinstance(reservations_data, list) else []
                
                print(f"🔍 Debug: Found {len(reservations)} total reservations for user")
                
                # Tìm reservation CONFIRMED của user hiện tại (trong vòng 7 ngày tới)
                from datetime import datetime, date, timedelta
                today = date.today()
                max_future_date = today + timedelta(days=7)  # Cho phép đặt món trước 7 ngày
                
                print(f"🔍 Debug: Looking for reservations between {today} and {max_future_date}")
                
                for reservation in reservations:
                    print(f"🔍 Debug: Checking reservation {reservation.get('id')} with status {reservation.get('status')}")
                    if reservation.get('status') == 'confirmed' or reservation.get('status') == 'pending':
                        # Kiểm tra ngày đặt bàn có trong khoảng từ hôm nay đến 7 ngày tới
                        reservation_date = reservation.get('reservation_date')
                        print(f"🔍 Debug: Raw reservation_date value: {reservation_date} (type: {type(reservation_date).__name__})")
                        print(f"🔍 Debug: Full reservation object: {reservation}")
                        
                        if reservation_date:
                            try:
                                # Parse reservation date - handle multiple formats
                                res_date = None
                                date_str = str(reservation_date)
                                
                                # Try ISO format with T separator (2026-01-07T19:00:00)
                                if 'T' in date_str:
                                    res_date = datetime.fromisoformat(date_str.replace('Z', '').replace('+00:00', '')).date()
                                    print(f"✅ Parsed ISO datetime: {res_date}")
                                # Try date-only format (2026-01-07)
                                elif len(date_str) == 10 and date_str.count('-') == 2:
                                    res_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                                    print(f"✅ Parsed YYYY-MM-DD: {res_date}")
                                # Try datetime string formats
                                else:
                                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                                        try:
                                            res_date = datetime.strptime(date_str, fmt).date()
                                            print(f"✅ Parsed with format {fmt}: {res_date}")
                                            break
                                        except ValueError:
                                            continue
                                
                                if not res_date:
                                    print(f"❌ FAILED to parse reservation_date: {reservation_date}")
                                    continue
                                
                                print(f"🔍 Comparing: {today} <= {res_date} <= {max_future_date}")
                                
                                # Cho phép gọi món cho reservation từ hôm nay đến 7 ngày tới
                                if today <= res_date <= max_future_date:
                                    print(f"✅✅✅ FOUND ACTIVE RESERVATION #{reservation.get('id')} for {res_date}")
                                    active_reservation = reservation
                                    break
                                else:
                                    print(f"❌ Date {res_date} outside range [{today}, {max_future_date}]")
                            except Exception as e:
                                print(f"❌ Exception parsing date: {e}")
                                import traceback
                                traceback.print_exc()
                                continue
                        else:
                            print(f"⚠️ Reservation #{reservation.get('id')} has no reservation_date field!")
            else:
                print(f"❌ API call to /reservations/my failed with status {reservations_response.status_code}")
                print(f"❌ Response: {reservations_response.text}")
            
            if not active_reservation:
                print(f"❌ No active reservation found for user")
                dispatcher.utter_message(text="""🍽️ **CẦN ĐẶT BÀN ĐỂ GỌI MÓN**
                
Không tìm thấy đặt bàn active của bạn.

📋 **Vui lòng:**
1. Kiểm tra lại bàn đã đặt chưa bị hủy
2. Đặt bàn mới nếu cần: **"Đặt bàn [số người] người [ngày] [giờ]"**

💡 **Ví dụ:** "Đặt bàn 4 người ngày 20/10/2025 lúc 19:00"

🔄 Sau khi đặt bàn xong, bạn có thể gọi món: **"Tôi muốn ăn [tên món]"** """)
                return []

            print(f"✅ Using reservation ID: {active_reservation.get('id')} for table {active_reservation.get('table_id', 'N/A')}")

            # Tìm món trong menu để lấy ID và giá - Sử dụng exact matching
            response = requests.get(f"{API_BASE_URL}/menu/items", headers=headers, timeout=5)

            if response.status_code == 200:
                response_data = response.json()
                print(f"🔍 Debug: All menu items loaded for exact matching")
                
                # API trả về dict với key 'items' chứa list các món
                all_items = response_data.get('items', []) if isinstance(response_data, dict) else response_data
                
                # Import exact matching function from menu_actions
                import sys, os
                sys.path.append(os.path.dirname(__file__))
                from .menu_actions import find_exact_dish_match, get_similar_dishes
                
                # Find exact match
                matched_item = find_exact_dish_match(dish_name, all_items)
                
                if matched_item:
                    item = matched_item
                    print(f"✅ Exact match found: {item.get('name')} (ID: {item.get('id')})")
                    
                    # If exact match found, add directly without confirmation
                    # (User already specified the dish name clearly)
                    table_id = active_reservation.get('table_id')
                    print("authenticated_user:", authenticated_user)
                    customer_id = authenticated_user.get('user_id') if authenticated_user else None
                    
                    print(f"🔍 Debug: Creating order with customer_id={customer_id}, table_id={table_id}")
                    
                    # Kiểm tra xem đã có order cho bàn này chưa
                    current_order_id = tracker.get_slot("current_order_id")
                    order_response = None
                    
                    if current_order_id:
                        # Kiểm tra order hiện tại có tồn tại không
                        order_response = requests.get(f"{API_BASE_URL}/orders/orders/{current_order_id}", headers=headers, timeout=5)
                    
                    if not current_order_id or (order_response and order_response.status_code != 200):
                        # Tạo order mới cho bàn này với tất cả thông tin cần thiết
                        order_data = {
                            "table_id": table_id,
                            "customer_id": customer_id,  # Gửi customer_id
                            "status": "PENDING",
                            "order_items": [
                                {
                                    "menu_item_id": item["id"],
                                    "quantity": quantity,
                                    "special_instructions": ""
                                }
                            ],
                            "notes": f"Đơn hàng cho bàn {table_id} - Từ chatbot"
                        }
                        
                        print(f"🔍 Debug: Sending order data: {order_data}")
                        print(f"🔍 Debug: Request headers: {headers}")
                        
                        # Đảm bảo headers có Content-Type
                        headers_with_content_type = dict(headers)
                        if "Content-Type" not in headers_with_content_type:
                            headers_with_content_type["Content-Type"] = "application/json"
                        
                        print(f"🔍 Debug: Final headers: {headers_with_content_type}")
                        
                        create_order_response = requests.post(
                            f"{API_BASE_URL}/orders/orders/",
                            headers=headers_with_content_type,
                            json=order_data,  # Dùng json parameter - tự động serialize + set Content-Type
                            timeout=10
                        )
                        
                        print(f"🔍 Debug: Create order response status: {create_order_response.status_code}")
                        print(f"🔍 Debug: Response headers: {dict(create_order_response.headers)}")
                        
                        if create_order_response.status_code != 200:
                            print(f"🔍 Debug: Full response content: {create_order_response.text}")
                            try:
                                error_detail = create_order_response.json()
                                print(f"🔍 Debug: Error detail: {error_detail}")
                            except Exception as parse_error:
                                print(f"🔍 Debug: Could not parse error response as JSON: {parse_error}")
                        
                        if create_order_response.status_code == 200:
                            order_info = create_order_response.json()
                            current_order_id = order_info.get('id')
                            print(f"✅ Order created with ID: {current_order_id}")
                        else:
                            print(f"❌ Create order failed: {create_order_response.text}")
                            dispatcher.utter_message(text="❌ Không thể tạo đơn hàng. Vui lòng thử lại sau.")
                            return []
                    else:
                        # Thêm món vào order hiện tại
                        add_item_data = {
                            "menu_item_id": item["id"],
                            "quantity": quantity,
                            "special_instructions": ""
                        }
                        
                        print(f"🔍 Debug: Adding item to existing order {current_order_id}")
                        print(f"🔍 Debug: Add item data: {add_item_data}")
                        print(f"🔍 Debug: Request headers for add item: {headers}")
                        
                        add_item_response = requests.post(
                            f"{API_BASE_URL}/orders/orders/{current_order_id}/items/",
                            headers=headers,
                            json=add_item_data,
                            timeout=10
                        )
                        
                        print(f"🔍 Debug: Add item response status: {add_item_response.status_code}")
                        print(f"🔍 Debug: Add item response: {add_item_response.text}")
                        
                        if add_item_response.status_code not in [200, 201]:
                            print(f"❌ Add item failed: {add_item_response.text}")
                            try:
                                error_detail = add_item_response.json()
                                print(f"🔍 Debug: Add item error detail: {error_detail}")
                            except Exception as parse_error:
                                print(f"🔍 Debug: Could not parse add item error response: {parse_error}")
                            dispatcher.utter_message(text="❌ Không thể thêm món vào đơn hàng. Vui lòng thử lại.")
                            return []
                        
                        print(f"✅ Item added successfully to order {current_order_id}")
                    
                    # Hiển thị thông báo thêm món thành công
                    if current_order_id:
                        price_formatted = f"{item['price']:,.0f}đ"
                        total_formatted = f"{item['price'] * quantity:,.0f}đ"
                        table_number = active_reservation.get('table', {}).get('number', table_id)
                        
                        message = f"✅ **ĐÃ THÊM MÓN VÀO ĐƠN HÀNG**\n\n"
                        message += f"🍽️ **Món:** {item['name']}\n"
                        message += f"📊 **Số lượng:** {quantity} phần\n"
                        message += f"💰 **Giá:** {price_formatted} x {quantity} = {total_formatted}\n"
                        message += f"🪑 **Bàn:** {table_number}\n\n"
                        message += f"💡 **Tiếp theo:**\n"
                        message += f"• Gọi thêm món: 'Tôi muốn thêm [tên món]'\n"
                        message += f"• Xem đơn hàng: 'Xem đơn hàng'\n"
                        message += f"• Xác nhận: 'Xác nhận đơn hàng'"
                        
                        dispatcher.utter_message(text=message)
                        return [
                            SlotSet("current_order_id", current_order_id),
                            SlotSet("last_mentioned_dish", item['name']),
                            SlotSet("active_table_id", table_id)
                        ]
                    else:
                        dispatcher.utter_message(text="❌ Không thể thêm món vào đơn hàng. Vui lòng thử lại sau.")
                        return []
                else:
                    # No exact match found, get similar dishes for suggestion
                    similar_dishes = get_similar_dishes(dish_name, all_items, limit=5)
                    
                    if similar_dishes:
                        message = f"❓ **KHÔNG TÌM THẤY CHÍNH XÁC:** `{dish_name}`\n\n"
                        message += "🔍 **Có phải bạn muốn gọi một trong những món này?**\n\n"
                        
                        for i, dish in enumerate(similar_dishes, 1):
                            message += f"{i}. **{dish['name']}**"
                            if dish.get('price'):
                                message += f" - {dish['price']:,.0f}đ"
                            message += "\n"
                        
                        message += "\n💡 **Cách chọn:**\n"
                        message += "• Nói: 'Tôi muốn gọi [tên món chính xác]'\n"
                        message += "• Hoặc: 'Xem thực đơn' để duyệt tất cả món\n"
                        message += "• Hoặc: 'Món số [1-5]' để chọn nhanh"
                        
                        dispatcher.utter_message(text=message)
                        return [SlotSet("suggested_dishes", [dish['name'] for dish in similar_dishes])]
                    else:
                        message = f"❌ **KHÔNG TÌM THẤY:** `{dish_name}`\n\n"
                        message += "🔍 **Gợi ý:**\n"
                        message += "• Nói 'Xem thực đơn' để xem tất cả món\n"
                        message += "• Thử tên món khác\n"
                        message += "• Kiểm tra chính tả\n\n"
                        message += "💡 **Ví dụ:** 'Tôi muốn gọi phở bò' (tên chính xác)"
                        
                        dispatcher.utter_message(text=message)
                        return []
                    
            else:
                message = "Không thể tìm kiếm món ăn. Vui lòng thử lại sau."
                dispatcher.utter_message(text=message)
                return []
                
        except requests.exceptions.Timeout:
            message = "⏱️ Kết nối chậm. Vui lòng thử lại sau."
            dispatcher.utter_message(text=message)
        except requests.exceptions.RequestException as e:
            message = f"❌ Có lỗi xảy ra khi thêm món vào đơn hàng."
            print(f"Error in ActionAddToOrder: {e}")
            dispatcher.utter_message(text=message)
        except Exception as e:
            message = f"❌ Có lỗi bất ngờ xảy ra khi thêm món vào đơn hàng."
            print(f"Unexpected error in ActionAddToOrder: {e}")
            dispatcher.utter_message(text=message)
        
        return []


class ActionRemoveFromOrder(Action):
    """Action để xóa món khỏi đơn hàng"""

    def name(self) -> Text:
        return "action_remove_from_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_order = tracker.get_slot('current_order') or []
        dish_name = None
        
        # Lấy tên món từ entity
        for entity in tracker.latest_message.get('entities', []):
            if entity['entity'] == 'dish_name':
                dish_name = entity['value']
                break
        
        # Nếu không có entity, lấy từ slot last_mentioned_dish
        if not dish_name:
            dish_name = tracker.get_slot('last_mentioned_dish')
        
        if not dish_name:
            dispatcher.utter_message(text="Bạn muốn xóa món nào? Vui lòng cho tôi biết tên món ăn.")
            return []
            
        if not current_order:
            dispatcher.utter_message(text="Đơn hàng của bạn đang trống. Không có món nào để xóa.")
            return []
        
        # Tìm và xóa món
        updated_order = []
        removed_item = None
        
        for item in current_order:
            if dish_name.lower() in item.get('name', '').lower():
                removed_item = item
                # Không thêm vào updated_order (xóa món)
            else:
                updated_order.append(item)
        
        if removed_item:
            price_formatted = f"{removed_item.get('price', 0):,.0f}đ"
            message = f"✅ Đã xóa **{removed_item.get('name')}** khỏi đơn hàng"
            
            if updated_order:
                # Tính lại tổng tiền
                total_amount = sum(item.get('price', 0) * item.get('quantity', 0) for item in updated_order)
                message += f"\n💰 **Tổng còn lại:** {total_amount:,.0f}đ"
                message += "\n\n💡 Nói 'xem đơn hàng' để kiểm tra lại"
            else:
                message += "\n📝 **Đơn hàng hiện tại trống**"
                message += "\n💡 Nói 'xem thực đơn' để gọi món mới"
                
            dispatcher.utter_message(text=message)
            return [SlotSet("current_order", updated_order)]
        else:
            # Hiển thị danh sách món có trong đơn để khách chọn
            if current_order:
                order_list = "❌ **Không tìm thấy món** `" + dish_name + "` **trong đơn hàng**\n\n"
                order_list += "📋 **Các món hiện có:**\n"
                for i, item in enumerate(current_order, 1):
                    order_list += f"{i}. {item.get('name', 'Món không tên')} (x{item.get('quantity', 1)})\n"
                order_list += "\n💡 **Bạn có thể nói:** 'Xóa món [tên món chính xác]'"
                
                dispatcher.utter_message(text=order_list)
            else:
                dispatcher.utter_message(text=f"Không tìm thấy món '{dish_name}' trong đơn hàng.")
                
            return []


class ActionViewCurrentOrder(Action):
    """Action để hiển thị đơn hàng hiện tại"""

    def name(self) -> Text:
        return "action_view_current_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract user info from metadata
        authenticated_user = get_authenticated_user_from_tracker(tracker)
        
        if not authenticated_user:
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để xem đơn hàng của bạn.")
            return []
        
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)
            
            # Lấy order hiện tại từ slot hoặc tìm order active
            current_order_id = tracker.get_slot("current_order_id")
            print(f"🔍 Debug: current_order_id from slot = {current_order_id}")
            
            if not current_order_id:
                dispatcher.utter_message(text="""📝 **CHƯA CÓ ĐƠN HÀNG**
Bạn chưa gọi món nào.

🍽️ **Bắt đầu gọi món:**
• Đặt bàn trước: "Tôi muốn đặt bàn"
• Sau đó gọi món: "Tôi muốn gọi [tên món]"

📋 **Ví dụ:** "Tôi muốn gọi Phở Bò" """)
                return []
            
            # Lấy thông tin order từ API
            response = requests.get(f"{API_BASE_URL}/orders/orders/{current_order_id}", headers=headers, timeout=5)
            
            print(f"🔍 Debug: Order API response status: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Order API failed with: {response.text}")
            
            if response.status_code == 200:
                order_info = response.json()
                print(f"🔍 Debug: Full order_info response: {order_info}")
                
                if not order_info.get('order_items'):
                    dispatcher.utter_message(text="""📝 **ĐƠN HÀNG TRỐNG**
Đơn hàng hiện tại chưa có món nào.

🍽️ **Gọi món:** "Tôi muốn gọi [tên món]" """)
                    return []

                table_id = order_info.get('table_id', 'N/A')
                order_number = order_info.get('order_number', 'N/A')
                total_amount = order_info.get('total_amount', 0)
                tax_amount = order_info.get('tax_amount', 0)
                status = order_info.get('status', 'pending')
                
                # Chuẩn bị items cho frontend
                items = []
                for item in order_info['order_items']:
                    menu_item = item.get('menu_item', {})
                    items.append({
                        'name': menu_item.get('name', 'Món không tên'),
                        'quantity': item.get('quantity', 0),
                        'unit_price': item.get('unit_price', 0),
                        'total_price': item.get('total_price', 0),
                        'price': item.get('unit_price', 0),  # Backup field
                        'description': menu_item.get('description', ''),
                        'image_url': menu_item.get('image_url', ''),
                        'category': menu_item.get('category', {}).get('name', '') if menu_item.get('category') else ''
                    })

                # Tạo custom response cho frontend
                custom_data = {
                    "order": {
                        "order_number": order_number,
                        "total_amount": total_amount,
                        "tax_amount": tax_amount,
                        "items": items,
                        "status": status
                    }
                }

                order_text = f"📋 **ĐƠN HÀNG #{order_number}** (Bàn {table_id})\n\n"
                order_text += f"🍽️ **{len(items)} món đã gọi**\n"
                order_text += f"💰 **Tổng cộng: {total_amount:,.0f}đ** (bao gồm thuế)\n\n"
                order_text += "💡 **Lựa chọn tiếp theo:**\n"
                order_text += "• Sửa đơn: 'Sửa đơn hàng'\n"
                order_text += "• Xác nhận: 'Xác nhận đơn hàng'\n"
                order_text += "• Thanh toán: 'Thanh toán đơn hàng'"

                dispatcher.utter_message(text=order_text, json_message=custom_data)
            else:
                print(f"❌ Order API failed with status: {response.status_code}")
                print(f"❌ Error response: {response.text}")
                dispatcher.utter_message(text="❌ Không thể tải thông tin đơn hàng. Vui lòng thử lại sau.")
            else:
                print(f"❌ Order API failed with status: {response.status_code}")
                print(f"❌ Error response: {response.text}")
                dispatcher.utter_message(text="❌ Không thể tải thông tin đơn hàng. Vui lòng thử lại sau.")
        
        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Vui lòng thử lại sau.")
        except Exception as e:
            print(f"Error in ActionViewCurrentOrder: {e}")
            dispatcher.utter_message(text="❌ Có lỗi xảy ra khi xem đơn hàng.")
        
        return []


class ActionConfirmOrder(Action):
    """Action để xác nhận đơn hàng"""

    def name(self) -> Text:
        return "action_confirm_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract user info from metadata
        user_info = None
        latest_message = tracker.latest_message
        if latest_message and 'metadata' in latest_message and latest_message['metadata']:
            user_info = latest_message['metadata'].get('user_info', {})
        
        if not user_info or not user_info.get('user_id'):
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để xác nhận đơn hàng.")
            return []
        
        current_order_id = tracker.get_slot('current_order_id')
        
        if not current_order_id:
            dispatcher.utter_message(text="📝 Bạn chưa có đơn hàng nào để xác nhận. Vui lòng gọi món trước.")
            return []

        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Lấy thông tin đơn hàng hiện tại
            order_response = requests.get(f"{API_BASE_URL}/orders/orders/{current_order_id}", headers=headers, timeout=5)
            
            if order_response.status_code != 200:
                dispatcher.utter_message(text="❌ Không tìm thấy đơn hàng để xác nhận.")
                return []
            
            order_info = order_response.json()
            
            if not order_info.get('order_items'):
                dispatcher.utter_message(text="📝 Đơn hàng không có món nào. Vui lòng gọi món trước khi xác nhận.")
                return []
            
            # Cập nhật trạng thái đơn hàng thành CONFIRMED
            update_response = requests.patch(
                f"{API_BASE_URL}/orders/orders/{current_order_id}/confirm",
                headers=headers,
                timeout=10
            )
            
            print(f"🔍 Debug: Confirm order response status: {update_response.status_code}")
            print(f"🔍 Debug: Confirm order response: {update_response.text}")
            
            if update_response.status_code == 200:
                # Tính tổng tiền
                total_amount = sum(item.get('subtotal', 0) for item in order_info['order_items'])
                table_id = order_info.get('table_id', 'N/A')
                
                confirmation_message = f"""✅ **ĐƠN HÀNG ĐÃ ĐƯỢC XÁC NHẬN**

📋 **Mã đơn hàng:** #{current_order_id}
🪑 **Bàn:** {table_id}
💰 **Tổng tiền:** {total_amount:,.0f}đ
⏱️ **Thời gian chuẩn bị:** 15-30 phút

📞 **Lưu ý:** 
• Đơn hàng đã được gửi vào bếp
• Món ăn sẽ được phục vụ tại bàn {table_id}
• Liên hệ nhân viên nếu cần hỗ trợ

🍽️ Cảm ơn bạn đã sử dụng dịch vụ! Chúc bạn dùng bữa ngon miệng! """
                
                dispatcher.utter_message(text=confirmation_message)
                
                # Clear current order slots
                return [
                    SlotSet("current_order_id", None),
                    SlotSet("last_order_id", current_order_id),
                    SlotSet("active_table_id", None)
                ]
                
            else:
                dispatcher.utter_message(text="❌ Không thể xác nhận đơn hàng lúc này. Vui lòng thử lại sau.")

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý đơn hàng... Vui lòng đợi.")
        except requests.exceptions.RequestException as e:
            print(f"Order confirmation error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi hệ thống khi xác nhận đơn hàng. Vui lòng liên hệ nhân viên.")
        except Exception as e:
            print(f"Unexpected order confirmation error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi bất ngờ khi xác nhận đơn hàng. Vui lòng liên hệ nhân viên.")

        return []


class ActionCancelOrder(Action):
    """Action để hủy đơn hàng với xác nhận thông tin"""

    def name(self) -> Text:
        return "action_cancel_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract user info from metadata
        user_info = None
        latest_message = tracker.latest_message
        if latest_message and 'metadata' in latest_message and latest_message['metadata']:
            user_info = latest_message['metadata'].get('user_info', {})
        
        if not user_info or not user_info.get('user_id'):
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để hủy đơn hàng.")
            return []
        
        current_order_id = tracker.get_slot('current_order_id')
        
        if not current_order_id:
            dispatcher.utter_message(text="""ℹ️ **KHÔNG CÓ ĐƠN HÀNG ĐỂ HỦY**

Bạn không có đơn hàng nào đang chờ xử lý.

📋 **Để đặt món mới:**
• Đặt bàn trước: "Tôi muốn đặt bàn"  
• Sau đó gọi món: "Tôi muốn gọi [tên món]" """)
            return []
        
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Lấy thông tin đơn hàng hiện tại
            response = requests.get(f"{API_BASE_URL}/orders/orders/{current_order_id}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                order_info = response.json()
                
                if not order_info.get('order_items'):
                    dispatcher.utter_message(text="📝 Đơn hàng hiện tại trống. Không có gì để hủy.")
                    return [SlotSet("current_order_id", None)]
                
                # Hiển thị thông tin đơn hàng và xác nhận
                table_id = order_info.get('table_id', 'N/A')
                order_status = order_info.get('status', 'PENDING')
                total_amount = 0.0
                
                confirmation_message = f"""❓ **XÁC NHẬN HỦY ĐƠN HÀNG**

📋 **Thông tin đơn hàng:**
🆔 **Mã đơn:** #{current_order_id}
🪑 **Bàn:** {table_id}
📊 **Trạng thái:** {order_status}"""
                
                items_text = "\n\n📝 **Các món đã gọi:**"
                for i, item in enumerate(order_info['order_items'], 1):
                    # API now returns menu_item nested
                    menu_item = item.get('menu_item', {})
                    
                    quantity = item.get('quantity', 0)
                    total_price = item.get('total_price', 0)
                    item_name = menu_item.get('name', 'Món không tên')
                    
                    total_amount += total_price
                    items_text += f"\n{i}. {item_name} x{quantity} = {total_price:,.0f}đ"
                
                confirmation_message += f"\n💰 **Tổng tiền:** {total_amount:,.0f}đ"
                confirmation_message += items_text
                
                confirmation_message += f"""

⚠️ **Bạn có chắc chắn muốn hủy toàn bộ đơn hàng này không?**

💡 **Chọn:**
• Nói **"Có"** để xác nhận hủy đơn hàng
• Nói **"Không"** để giữ lại đơn hàng
• Nói **"Xóa món [tên]"** để chỉ xóa một món"""
                
                dispatcher.utter_message(text=confirmation_message)
                
                return [SlotSet("pending_cancellation_order_id", current_order_id),
                        SlotSet("conversation_context", "cancel_order_confirmation")]
            else:
                dispatcher.utter_message(text="❌ Không thể tải thông tin đơn hàng. Vui lòng thử lại sau.")
                return []
                
        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Vui lòng thử lại sau.")
        except Exception as e:
            print(f"Error in ActionCancelOrder: {e}")
            dispatcher.utter_message(text="❌ Có lỗi xảy ra khi kiểm tra đơn hàng.")
        
        return []


class ActionConfirmCancelOrder(Action):
    """Action để xác nhận hủy đơn hàng"""

    def name(self) -> Text:
        return "action_confirm_cancel_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        order_id = tracker.get_slot('pending_cancellation_order_id')
        
        if not order_id:
            dispatcher.utter_message(text="❌ Không tìm thấy thông tin đơn hàng cần hủy.")
            return []
        
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Cập nhật trạng thái đơn hàng thành CANCELLED
            update_data = {"status": "CANCELLED"}
            response = requests.put(
                f"{API_BASE_URL}/orders/orders/{order_id}",
                headers=headers,
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                success_message = f"""✅ **ĐÃ HỦY ĐƠN HÀNG THÀNH CÔNG**

📋 **Thông tin:**
🆔 **Mã đơn:** #{order_id}
🗑️ **Trạng thái:** Đã hủy

💡 **Lưu ý:**
• Đơn hàng đã được hủy hoàn toàn
• Không có phí phát sinh
• Bàn vẫn được giữ cho bạn

🔄 **Để gọi món mới:**
• Nói "Tôi muốn gọi [tên món]"
• Hoặc "Xem thực đơn" để chọn món"""
                
                dispatcher.utter_message(text=success_message)
                
                # Clear slots
                return [
                    SlotSet("pending_cancellation_order_id", None),
                    SlotSet("conversation_context", None),
                    SlotSet("current_order_id", None),
                    SlotSet("last_order_id", order_id)
                ]
                
            else:
                dispatcher.utter_message(text="❌ Không thể hủy đơn hàng lúc này. Vui lòng liên hệ nhân viên.")

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý hủy đơn hàng... Vui lòng đợi.")
        except requests.exceptions.RequestException as e:
            print(f"Cancel order error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi hệ thống khi hủy đơn hàng. Vui lòng liên hệ nhân viên.")
        except Exception as e:
            print(f"Unexpected cancel order error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi bất ngờ khi hủy đơn hàng. Vui lòng liên hệ nhân viên.")
        
        return []


class ActionDenyCancellation(Action):
    """Action để từ chối hủy (giữ lại đặt bàn/đơn hàng)"""

    def name(self) -> Text:
        return "action_deny_cancellation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        conversation_context = tracker.get_slot("conversation_context")
        
        if conversation_context == "cancel_reservation_confirmation":
            dispatcher.utter_message(text="""✅ **ĐÃ GIỮ LẠI ĐẶT BÀN**

Đặt bàn của bạn vẫn được giữ nguyên.

💡 **Bạn có thể:**
• Nói "Xem thông tin đặt bàn" 
• Nói "Sửa đặt bàn" để thay đổi thông tin
• Hoặc tiếp tục gọi món: "Tôi muốn gọi [tên món]" """)
        
        elif conversation_context == "cancel_order_confirmation":
            dispatcher.utter_message(text="""✅ **ĐÃ GIỮ LẠI ĐƠN HÀNG**

Đơn hàng của bạn vẫn được giữ nguyên.

💡 **Bạn có thể:**
• Nói "Xem đơn hàng" để kiểm tra lại  
• Nói "Thêm món [tên]" để gọi thêm
• Nói "Xác nhận đơn hàng" để hoàn tất""")
        else:
            dispatcher.utter_message(text="✅ Đã hủy thao tác. Bạn có cần hỗ trợ gì khác không?")
        
        # Clear cancellation context
        return [
            SlotSet("conversation_context", None),
            SlotSet("pending_cancellation_reservation_id", None),
            SlotSet("pending_cancellation_order_id", None)
        ]


class ActionModifyOrder(Action):
    """Action để sửa đơn hàng"""

    def name(self) -> Text:
        return "action_modify_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Lấy thông tin user đã xác thực
        authenticated_user = get_authenticated_user_from_tracker(tracker)
        
        if not authenticated_user:
            dispatcher.utter_message(text="🔐 Bạn cần đăng nhập để sửa đơn hàng.")
            return []
        
        # Kiểm tra xem có entities để xử lý modification không
        entities = tracker.latest_message.get('entities', [])
        dish_name = None
        quantity = None
        
        for entity in entities:
            if entity['entity'] == 'dish_name':
                dish_name = entity['value'].lower()
            elif entity['entity'] == 'quantity':
                try:
                    quantity = int(entity['value'])
                except ValueError:
                    quantity = None
        
        # Nếu có dish_name và quantity, xử lý sửa số lượng
        if dish_name and quantity is not None:
            return self._handle_quantity_modification(dispatcher, tracker, dish_name, quantity, authenticated_user)
        
        # Nếu chỉ có dish_name (không có quantity), xử lý xóa món
        elif dish_name:
            return self._handle_remove_dish(dispatcher, tracker, dish_name, authenticated_user)
            
        # Nếu không có entities cụ thể, hiển thị menu hướng dẫn
        current_order_id = tracker.get_slot("current_order_id")
        
        if not current_order_id:
            dispatcher.utter_message(text="❌ Không tìm thấy đơn hàng nào để sửa. Hãy gọi món trước.")
            return []
            
        dispatcher.utter_message(text="""🛠️ **SỬA ĐƠN HÀNG**

Bạn muốn sửa gì trong đơn hàng?

📝 **Các lựa chọn:**
• "Bỏ [tên món]" - Xóa món khỏi đơn
• "Thêm [tên món]" - Thêm món mới
• "Sửa số lượng [món] thành [số]" - Đổi số lượng
• "Xem đơn hàng" - Kiểm tra lại đơn hiện tại

💡 Hãy cho tôi biết cụ thể bạn muốn sửa gì nhé!""")
        
        return [SlotSet("conversation_context", "modify_order")]
    
    def _handle_quantity_modification(self, dispatcher, tracker, dish_name, quantity, authenticated_user):
        """Xử lý sửa số lượng món ăn"""
        try:
            current_order_id = tracker.get_slot("current_order_id")
            if not current_order_id:
                dispatcher.utter_message(text="❌ Không tìm thấy đơn hàng để sửa.")
                return []
            
            headers = get_auth_headers_from_tracker(tracker)
            
            # Gọi API để cập nhật số lượng
            response = requests.put(
                f"{API_BASE_URL}/orders/{current_order_id}/items/update_quantity",
                json={
                    "dish_name": dish_name,
                    "new_quantity": quantity
                },
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                dispatcher.utter_message(text=f"✅ Đã cập nhật số lượng **{dish_name.title()}** thành **{quantity}**!\n\n💡 Bạn có thể nói 'Xem đơn hàng' để kiểm tra lại.")
            elif response.status_code == 404:
                dispatcher.utter_message(text=f"❌ Không tìm thấy món **{dish_name.title()}** trong đơn hàng.")
            else:
                result = response.json()
                dispatcher.utter_message(text=f"❌ Lỗi: {result.get('detail', 'Không thể cập nhật số lượng')}")
                
        except Exception as e:
            dispatcher.utter_message(text=f"❌ Có lỗi xảy ra khi sửa số lượng: {str(e)}")
        
        return []
    
    def _handle_remove_dish(self, dispatcher, tracker, dish_name, authenticated_user):
        """Xử lý xóa món khỏi đơn hàng"""
        try:
            current_order_id = tracker.get_slot("current_order_id")
            if not current_order_id:
                dispatcher.utter_message(text="❌ Không tìm thấy đơn hàng để sửa.")
                return []
            
            headers = get_auth_headers_from_tracker(tracker)
            
            # Gọi API để xóa món
            response = requests.delete(
                f"{API_BASE_URL}/orders/{current_order_id}/items/remove",
                json={"dish_name": dish_name},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                dispatcher.utter_message(text=f"✅ Đã xóa **{dish_name.title()}** khỏi đơn hàng!\n\n💡 Bạn có thể nói 'Xem đơn hàng' để kiểm tra lại.")
            elif response.status_code == 404:
                dispatcher.utter_message(text=f"❌ Không tìm thấy món **{dish_name.title()}** trong đơn hàng.")
            else:
                result = response.json()
                dispatcher.utter_message(text=f"❌ Lỗi: {result.get('detail', 'Không thể xóa món')}")
                
        except Exception as e:
            dispatcher.utter_message(text=f"❌ Có lỗi xảy ra khi xóa món: {str(e)}")
        
        return []


class ActionShowCurrentOrder(Action):
    """Alias for ActionViewCurrentOrder"""

    def name(self) -> Text:
        return "action_show_current_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Delegate to ActionViewCurrentOrder
        view_action = ActionViewCurrentOrder()
        return view_action.run(dispatcher, tracker, domain)