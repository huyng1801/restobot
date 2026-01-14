"""
Table Booking Actions for RestoBot
Xử lý các action liên quan đến đặt bàn
"""
import re
import requests
from datetime import datetime, timedelta
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .auth_helper import auth_helper, get_authenticated_user_from_tracker, get_auth_headers_from_tracker

# URL của FastAPI backend (dùng Docker internal network)
API_BASE_URL = "http://api:8000/api/v1"

# Business hours validation
def validate_business_hours(reservation_datetime: datetime) -> tuple[bool, str]:
    """Validate if reservation is within business hours"""
    weekday = reservation_datetime.weekday()
    hour = reservation_datetime.hour
    
    # Business hours: 10:00-22:00, lunch break: 14:00-17:00 (Mon-Fri)
    if hour < 10:
        return False, "🕘 Nhà hàng mở cửa từ **10:00 sáng**. Vui lòng chọn giờ khác."
    
    if hour >= 22:
        return False, "🕘 Nhà hàng đóng cửa lúc **22:00 tối**. Vui lòng chọn giờ khác."
    
    # Check lunch break (Monday-Friday only)
    if weekday < 5 and 14 <= hour < 17:  # Monday=0, Friday=4
        return False, "🍽️ Nhà hàng **nghỉ trưa từ 14:00-17:00** (Thứ 2-6). Vui lòng chọn:\n• **10:00-14:00** (sáng)\n• **17:00-22:00** (tối)"
    
    return True, ""
API_BASE_URL = "http://api:8000/api/v1"


class ActionAskTableBookingInfo(Action):
    """Action để hỏi thông tin đặt bàn theo format chuẩn"""

    def name(self) -> Text:
        return "action_ask_table_booking_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = """🪑 **ĐẶT BÀN NHÀ HÀNG**

Để đặt bàn, vui lòng cung cấp thông tin theo định dạng sau:

📋 **Thông tin cần thiết:**
• **Số người**: 2, 4, 6, 8 người...
• **Ngày**: DD/MM/YYYY (ví dụ: 20/10/2025)
• **Giờ**: HH:MM (ví dụ: 19:00, 12:30)

💡 **Ví dụ:**
- 'Tôi muốn đặt bàn 4 người ngày 20/10/2025 lúc 19:00'
- 'Đặt bàn 2 người mai 7 giờ tối'
- 'Book bàn 6 người chủ nhật 12:30'

Hoặc bạn có thể cung cấp từng thông tin, tôi sẽ hỏi từng bước! 😊"""
        
        dispatcher.utter_message(text=message)
        return []


class ActionShowAvailableTables(Action):
    """Action để hiển thị bàn trống"""

    def name(self) -> Text:
        return "action_show_available_tables"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ""
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            number_of_people = tracker.get_slot("number_of_people")
            
            # Gọi API để lấy bàn trống
            params = {}
            if number_of_people:
                params["min_capacity"] = int(number_of_people)
            
            response = requests.get(f"{API_BASE_URL}/tables/available", params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                tables = response.json()
                
                if tables:
                    message = f"🪑 **CÁC BÀN TRỐNG**"
                    if number_of_people:
                        message += f" (cho {number_of_people} người)"
                    message += "\n\n"
                    
                    for table in tables:
                        message += f"• **Bàn {table['table_number']}** - {table['capacity']} chỗ"
                        if table['location']:
                            message += f" ({table['location']})"
                        message += "\n"
                    
                    message += f"\n✅ Có **{len(tables)} bàn** phù hợp với yêu cầu của bạn.\n"
                    message += "💡 Để đặt bàn, vui lòng cho biết thời gian cụ thể!"
                    
                else:
                    message = "❌ Xin lỗi, hiện tại không có bàn trống phù hợp.\n"
                    message += "🕐 Bạn có thể thử thời gian khác hoặc liên hệ trực tiếp: **0901234567**"
                    
            else:
                message = "❌ Không thể kiểm tra bàn trống. Vui lòng thử lại sau."
                
        except requests.exceptions.Timeout:
            message = "⏱️ Kết nối chậm. Vui lòng thử lại sau."
        except requests.exceptions.RequestException as e:
            message = f"❌ Có lỗi xảy ra khi kiểm tra bàn trống."
            print(f"Error in ActionShowAvailableTables: {e}")
        except Exception as e:
            message = f"❌ Có lỗi bất ngờ xảy ra khi kiểm tra bàn trống."
            print(f"Unexpected error in ActionShowAvailableTables: {e}")
        
        dispatcher.utter_message(text=message)
        return []


class ActionBookTable(Action):
    """Action để đặt bàn với xác thực thông tin"""

    def name(self) -> Text:
        return "action_book_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Import auth functions
        from .auth_helper import get_authenticated_user_from_tracker, get_auth_headers_from_tracker
        
        # Lấy thông tin user đã xác thực từ tracker
        authenticated_user = get_authenticated_user_from_tracker(tracker)
        
        # Nếu không có user đã xác thực, yêu cầu đăng nhập
        if not authenticated_user:
            dispatcher.utter_message(text="""🔐 **ĐĂNG NHẬP YÊU CẦU**
            
Để đặt bàn, bạn cần đăng nhập vào hệ thống.

📱 **Các bước:**
1. Nhấn **"Đăng nhập"** ở góc trên
2. Nhập tài khoản và mật khẩu  
3. Quay lại chat để đặt bàn

💡 **Tại sao cần đăng nhập?**
• Lưu thông tin đặt bàn của bạn
• Gửi xác nhận qua email/SMS
• Quản lý lịch sử đặt bàn

🚀 Sau khi đăng nhập, hãy thử lại: "Đặt bàn 4 người ngày 20/10/2025 lúc 19:00" """)
            return []
        
        # Sử dụng thông tin của user đã xác thực
        user_id = authenticated_user.get('user_id') or authenticated_user.get('user_id')
        username = authenticated_user.get('username', 'User')
        user_full_name = authenticated_user.get('full_name', username)
        
        print(f"✅ Booking for authenticated user: {username} (ID: {user_id})")
        
        
        num_people = tracker.get_slot('number_of_people')
        reservation_date = tracker.get_slot('reservation_date')
        reservation_time = tracker.get_slot('reservation_time')
        
        # Get the latest message text for debugging
        latest_message = tracker.latest_message.get('text', '')
        
        print(f"DEBUG - Latest message: {latest_message}")
        print(f"DEBUG - Extracted slots: people={num_people} (type: {type(num_people)}), date={reservation_date}, time={reservation_time}")
        print(f"DEBUG - Entities from latest message: {tracker.latest_message.get('entities', [])}")
        
        # If no slots extracted, try to extract from message text directly
        if not num_people:
            # Try to find number in the latest message
            message_text = latest_message.lower()
            
            # Extract number patterns
            number_patterns = [
                r'(\d+)\s*người',
                r'(\d+)\s*khách',
                r'(\d+)\s*chỗ',
                r'(\d+)\s*bàn',
                r'\b(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\b',
                r'\b(gia đình|cặp đôi|nhóm)\b'
            ]
            
            for pattern in number_patterns:
                match = re.search(pattern, message_text)
                if match:
                    num_people = match.group(1)
                    print(f"DEBUG - Extracted number from text: {num_people}")
                    break
        
        # Check if all required information is available
        if not all([num_people, reservation_date, reservation_time]):
            missing_info = []
            if not num_people:
                missing_info.append("số người")
            if not reservation_date:
                missing_info.append("ngày")
            if not reservation_time:
                missing_info.append("giờ")
                
            dispatcher.utter_message(text=f"""🔍 **THÔNG TIN CHƯA ĐẦY ĐỦ**
Bạn thiếu thông tin: {', '.join(missing_info)}

📝 **Ví dụ hoàn chỉnh:** 
"Tôi muốn đặt bàn 4 người ngày 20/10/2025 lúc 19:00"

💡 **Định dạng:**
• Số người: 1-20 người
• Ngày: dd/mm/yyyy (từ hôm nay)
• Giờ: hh:mm (10:00-22:00)

🎯 **Bạn có thể nói:** "Đặt bàn [số người] người ngày [dd/mm/yyyy] lúc [hh:mm]" """)
            return []

        # Validate the booking information
        try:
            # Validate number of people
            num_people_int = None
            
            # Handle different types of num_people values
            if isinstance(num_people, (int, float)):
                num_people_int = int(num_people)
            elif isinstance(num_people, str):
                # Try to extract number from string
                # Extract number from string like "4 người", "bốn", etc.
                number_match = re.search(r'\d+', str(num_people))
                if number_match:
                    num_people_int = int(number_match.group())
                else:
                    # Handle Vietnamese number words
                    vietnamese_numbers = {
                        'một': 1, 'hai': 2, 'ba': 3, 'bốn': 4, 'năm': 5,
                        'sáu': 6, 'bảy': 7, 'tám': 8, 'chín': 9, 'mười': 10,
                        'gia đình': 4, 'cặp đôi': 2, 'nhóm': 6
                    }
                    
                    num_people_lower = str(num_people).lower().strip()
                    for vn_word, number in vietnamese_numbers.items():
                        if vn_word in num_people_lower:
                            num_people_int = number
                            break
            
            if num_people_int is None:
                dispatcher.utter_message(text=f"""❌ **SỐ LƯỢNG KHÁCH KHÔNG HỢP LỆ**
Không thể xử lý "{num_people}".

✅ **Định dạng đúng:**
• **Số:** 1, 2, 3, 4, 5, 6... (tối đa 20)
• **Chữ:** một, hai, ba, bốn người...
• **Từ khóa:** gia đình (4 người), cặp đôi (2 người)

📝 **Thử lại:** "Đặt bàn 4 người ngày {reservation_date or '20/10/2025'} lúc {reservation_time or '19:00'}" """)
                return []
                
            if num_people_int < 1 or num_people_int > 20:
                dispatcher.utter_message(text=f"""❌ **SỐ LƯỢNG KHÁCH KHÔNG HỢP LỆ**
Số người "{num_people_int}" không được hỗ trợ.

✅ **Giới hạn:** Nhà hàng phục vụ từ **1-20 người/bàn**

📝 **Thử lại:** "Đặt bàn [1-20] người ngày {reservation_date or '20/10/2025'} lúc {reservation_time or '19:00'}" """)
                return []

            # Normalize and validate date format
            date_formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
            date_obj = None
            
            # Try to parse the date with different formats
            for date_format in date_formats:
                try:
                    date_obj = datetime.strptime(reservation_date.strip(), date_format)
                    break
                except ValueError:
                    continue
            
            # If no format worked, try some common Vietnamese phrases
            if not date_obj:
                today = datetime.now()
                reservation_date_lower = reservation_date.lower().strip()
                
                if reservation_date_lower in ["hôm nay", "today", "hôm nay"]:
                    date_obj = today
                elif reservation_date_lower in ["ngày mai", "tomorrow", "mai"]:
                    date_obj = today + timedelta(days=1)
                elif reservation_date_lower in ["ngày kia", "day after tomorrow"]:
                    date_obj = today + timedelta(days=2)
                else:
                    dispatcher.utter_message(text=f"""❌ **ĐỊNH DẠNG NGÀY KHÔNG ĐÚNG**
Ngày "{reservation_date}" không hợp lệ.

✅ **Định dạng đúng:**
• **dd/mm/yyyy** (ví dụ: 20/10/2025)
• **Hoặc:** hôm nay, ngày mai, ngày kia

📝 **Thử lại:** "Đặt bàn {num_people_int} người ngày 20/10/2025 lúc 19:00" """)
                    return []

            # Check if date is not in the past
            if date_obj.date() < datetime.now().date():
                dispatcher.utter_message(text="📅 Ngày đặt bàn phải từ hôm nay trở đi. Vui lòng chọn ngày khác.")
                return []

            # Normalize and validate time format
            time_formats = ["%H:%M", "%H.%M", "%H:%M:%S", "%H"]
            time_obj = None
            
            # Clean up time string
            time_str = reservation_time.strip().lower()
            print(f"DEBUG: Original time string: '{reservation_time}', cleaned: '{time_str}'")
            
            # Convert Vietnamese time phrases to standard format
            if "tối" in time_str or "chiều" in time_str:
                # Extract number before "giờ tối" or "giờ chiều"  
                match = re.search(r'(\d+)[\s]*(?:giờ|h)?\s*(?:tối|chiều)', time_str)
                if match:
                    hour = int(match.group(1))
                    if hour <= 12 and ("tối" in time_str or ("chiều" in time_str and hour < 6)):
                        hour += 12  # Convert to 24h format
                    time_str = f"{hour:02d}:00"
                    print(f"DEBUG: Converted evening time: {time_str}")
            elif "sáng" in time_str:
                match = re.search(r'(\d+)[\s]*(?:giờ|h)?\s*sáng', time_str)
                if match:
                    hour = int(match.group(1))
                    time_str = f"{hour:02d}:00"
                    print(f"DEBUG: Converted morning time: {time_str}")
            elif "rưỡi" in time_str:
                match = re.search(r'(\d+)[\s]*(?:giờ|h)?\s*rưỡi', time_str)
                if match:
                    hour = int(match.group(1))
                    time_str = f"{hour:02d}:30"
                    print(f"DEBUG: Converted half hour: {time_str}")
            elif re.match(r'^\d+$', time_str.strip()):
                # Just a number like "19", "7" 
                hour = int(time_str.strip())
                time_str = f"{hour:02d}:00"
                print(f"DEBUG: Converted simple hour: {time_str}")
            
            print(f"DEBUG: Final time string for parsing: '{time_str}'")
            
            # Try to parse the time
            for time_format in time_formats:
                try:
                    time_obj = datetime.strptime(time_str, time_format)
                    print(f"DEBUG: Successfully parsed time with format {time_format}: {time_obj}")
                    break
                except ValueError as e:
                    print(f"DEBUG: Failed to parse '{time_str}' with format '{time_format}': {e}")
                    continue
            
            if not time_obj:
                dispatcher.utter_message(text=f"""❌ **ĐỊNH DẠNG GIỜ KHÔNG ĐÚNG**
Giờ "{reservation_time}" không hợp lệ.

✅ **Định dạng đúng:**
• **hh:mm** (ví dụ: 19:00, 18:30, 12:15)
• **Hoặc:** 7 giờ tối, 6 rưỡi chiều

📝 **Thử lại:** "Đặt bàn {num_people_int} người ngày {reservation_date} lúc 19:00" """)
                return []

            # Check restaurant operating hours (10:00-22:00)
            if time_obj.hour < 10 or time_obj.hour >= 22:
                dispatcher.utter_message(text="⏰ Giờ đặt bàn phải trong khung 10:00-22:00. Vui lòng chọn giờ khác.")
                return []

            # Check if booking time is at least 1 hour from now
            booking_datetime = datetime.combine(date_obj.date(), time_obj.time())
            if booking_datetime <= datetime.now() + timedelta(hours=1):
                dispatcher.utter_message(text="⏱️ Vui lòng đặt bàn trước ít nhất 1 giờ.")
                return []

            # Validate business hours
            is_valid_time, time_error_msg = validate_business_hours(booking_datetime)
            if not is_valid_time:
                dispatcher.utter_message(text=time_error_msg)
                return []

            # Convert back to standard format for API call
            standard_date = date_obj.strftime("%d/%m/%Y")
            standard_time = time_obj.strftime("%H:%M")

        except Exception as e:
            print(f"Validation error: {e}")
            print(f"DEBUG - num_people: {num_people}, reservation_date: {reservation_date}, reservation_time: {reservation_time}")
            import traceback
            traceback.print_exc()
            dispatcher.utter_message(text=f"""❌ **LỖI XỬ LÝ THÔNG TIN**
Có lỗi khi xử lý thông tin đặt bàn: {str(e)}

📝 **Vui lòng thử lại với format:**
"Đặt bàn [số người] người ngày [dd/mm/yyyy] lúc [hh:mm]"

💡 **Ví dụ:** "Đặt bàn 4 người ngày 20/10/2025 lúc 19:00" """)
            return []
                        
        # Attempt to book the table via API
        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Chuẩn bị datetime cho reservation_date theo API mới
            try:
                # Build reservation datetime directly from parsed date_obj and time_obj
                reservation_datetime = datetime.combine(date_obj.date(), time_obj.time())
                iso_datetime = reservation_datetime.isoformat()
                
                # Tìm bàn phù hợp - cần gọi API tables để lấy table_id
                tables_response = requests.get(f"{API_BASE_URL}/tables/available", headers=headers, timeout=5)
                if tables_response.status_code != 200:
                    dispatcher.utter_message(text="❌ Không thể kiểm tra bàn trống. Vui lòng thử lại sau.")
                    return []
                
                available_tables = tables_response.json()
                suitable_table = None
                for table in available_tables:
                    if table.get('capacity', 0) >= num_people_int:
                        suitable_table = table
                        break
                
                if not suitable_table:
                    dispatcher.utter_message(text=f"❌ Không có bàn trống cho {num_people_int} người vào thời gian này. Vui lòng chọn thời gian khác.")
                    return []
                
                booking_data = {
                    "table_id": suitable_table['id'],
                    "reservation_date": iso_datetime,
                    "party_size": num_people_int,
                    "special_requests": f"Đặt bàn qua chatbot - {user_full_name}"
                }
                
                # Thêm user_id nếu có
                if user_id:
                    booking_data["customer_id"] = user_id
            except Exception as e:
                print(f"Error preparing booking data: {e}")
                dispatcher.utter_message(text="❌ Có lỗi khi chuẩn bị thông tin đặt bàn. Vui lòng thử lại.")
                return []
            
            print(f"DEBUG - Booking data: {booking_data}")
            
            response = requests.post(
                f"{API_BASE_URL}/orders/reservations/",
                headers=headers,
                json=booking_data,
                timeout=10
            )
            
            print(f"DEBUG - Reservation POST status: {response.status_code}, response: {getattr(response, 'text', '')}")

            if response.status_code in [200, 201]:  # Accept both 200 OK and 201 Created
                try:
                    booking_info = response.json()
                    print(f"DEBUG - Booking response JSON: {booking_info}")
                except Exception as e:
                    print(f"DEBUG - Failed to parse booking response JSON: {e}")
                    print(f"DEBUG - Response text: {getattr(response, 'text', '')}")
                    dispatcher.utter_message(text="❌ Đặt bàn thất bại do lỗi phản hồi từ server. Vui lòng thử lại.")
                    return []
                customer_name = user_full_name
                customer_phone = authenticated_user.get('phone', '')
                
                # Handle different response formats from the API
                booking_id = booking_info.get('id') or booking_info.get('reservation_id') or 'N/A'
                table_info = booking_info.get('table_number') or booking_info.get('table', {}).get('table_number') or 'Sẽ được sắp xếp'
                
                confirmation_message = f"""✅ **ĐẶT BÀN THÀNH CÔNG**

👤 **Khách hàng:** {customer_name}
📞 **Số ĐT:** {customer_phone if customer_phone else 'Chưa cập nhật'}

📋 **Thông tin đặt bàn:**
• **Mã đặt bàn:** #{booking_id}
• **Số khách:** {num_people_int} người
• **Ngày:** {standard_date}
• **Giờ:** {standard_time}
• **Bàn số:** {table_info}

📞 **Lưu ý:** Vui lòng đến đúng giờ. Nếu muốn hủy, liên hệ trước 2 giờ.
🍽️ Bạn có muốn xem thực đơn để gọi món trước không?"""
                
                dispatcher.utter_message(text=confirmation_message)
                
                # Store booking info in slots
                return [
                    SlotSet("number_of_people", num_people_int),
                    SlotSet("reservation_date", standard_date),
                    SlotSet("reservation_time", standard_time),
                    SlotSet("last_booking_id", booking_id)
                ]
                
            elif response.status_code == 409: # Conflict, meaning table might be occupied
                dispatcher.utter_message(text=f"""😔 **KHÔNG CÒN BÀN TRỐNG**
Thời gian {standard_time} ngày {standard_date} đã hết chỗ.

🕐 **Khung giờ gợi ý:**
• 11:00-12:00 (ít khách)
• 14:00-17:00 (thoải mái)
• 20:00-21:30 (còn chỗ)

📝 **Thử lại:** "Đặt bàn {num_people_int} người ngày {standard_date} lúc [giờ khác]" """)
            elif response.status_code == 400:
                try:
                    error_detail = response.json().get('detail', 'Dữ liệu không hợp lệ')
                except:
                    error_detail = 'Dữ liệu không hợp lệ'
                dispatcher.utter_message(text=f"❌ **THÔNG TIN KHÔNG HỢP LỆ**\n{error_detail}\n\nVui lòng kiểm tra lại thông tin đặt bàn.")
            else:
                try:
                    error_detail = response.json().get('detail', 'Lỗi không xác định')
                except:
                    error_detail = f"HTTP {response.status_code}"
                dispatcher.utter_message(text=f"❌ Không thể đặt bàn lúc này: {error_detail}\n\nVui lòng thử lại hoặc gọi điện đặt bàn: 0123-456-789")

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý đặt bàn... Vui lòng đợi hoặc liên hệ nhân viên.")
        except requests.exceptions.RequestException as e:
            print(f"Booking RequestException: {e}")
            print(f"DEBUG - booking_data at failure: {booking_data if 'booking_data' in locals() else 'N/A'}")
            print(f"DEBUG - authenticated_user at failure: {authenticated_user}")
            dispatcher.utter_message(text=f"🔧 Lỗi hệ thống đặt bàn. Vui lòng liên hệ nhân viên: 0123-456-789.")
        except Exception as e:
            print(f"Unexpected booking error: {e}")
            print(f"DEBUG - booking_data at failure: {booking_data if 'booking_data' in locals() else 'N/A'}")
            print(f"DEBUG - authenticated_user at failure: {authenticated_user}")
            import traceback
            traceback.print_exc()
            dispatcher.utter_message(text=f"🔧 Lỗi bất ngờ khi đặt bàn. Vui lòng liên hệ nhân viên: 0123-456-789.")

        return []


class ActionCancelReservation(Action):
    """Action để hủy đặt bàn với xác nhận thông tin"""

    def name(self) -> Text:
        return "action_cancel_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Import auth functions
        from .auth_helper import get_authenticated_user_from_tracker, get_auth_headers_from_tracker
        
        # Lấy thông tin user đã xác thực từ tracker
        authenticated_user = get_authenticated_user_from_tracker(tracker)
        
        if not authenticated_user:
            dispatcher.utter_message(text="🔐 Vui lòng đăng nhập để hủy đặt bàn.")
            return []
        
        try:
            # Sử dụng auth headers từ user token, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Tìm reservation active của user - sử dụng endpoint my reservations
            reservations_response = requests.get(
                f"{API_BASE_URL}/orders/reservations/my", 
                headers=headers, 
                timeout=5
            )
            
            active_reservations = []
            if reservations_response.status_code == 200:
                reservations_data = reservations_response.json()
                # API trả về list trực tiếp, không cần get 'items'
                reservations = reservations_data if isinstance(reservations_data, list) else []
                
                print(f"🔍 Debug: Found {len(reservations)} total reservations")
                
                from datetime import datetime, date
                today = date.today()
                print(f"🔍 Debug: Today is {today}")
                
                for reservation in reservations:
                    print(f"🔍 Debug: Checking reservation {reservation.get('id')} with status {reservation.get('status')}")
                    # Lọc chỉ những reservation confirmed từ hôm nay trở đi
                    if reservation.get('status') == 'confirmed' or reservation.get('status') == 'pending':
                        reservation_date = reservation.get('reservation_date')
                        print(f"🔍 Debug: Reservation date: {reservation_date}")
                        if reservation_date:
                            try:
                                # Parse datetime string
                                if 'T' in str(reservation_date):
                                    res_datetime = datetime.fromisoformat(str(reservation_date).replace('Z', ''))
                                else:
                                    res_datetime = datetime.strptime(str(reservation_date), '%Y-%m-%d')
                                
                                res_date = res_datetime.date()
                                
                                # Lấy reservation từ hôm nay trở đi
                                if res_date >= today:
                                    print(f"🔍 Debug: Reservation {reservation.get('id')} date {res_date} >= {today}: Adding to active list")
                                    active_reservations.append(reservation)
                                else:
                                    print(f"🔍 Debug: Reservation {reservation.get('id')} date {res_date} < {today}: Skipping (past date)")
                                    
                            except Exception as date_error:
                                print(f"❌ Error parsing reservation date {reservation_date}: {date_error}")
                                # Nếu không parse được date, vẫn thêm vào list để an toàn
                                print(f"🔍 Debug: Adding reservation {reservation.get('id')} despite date parse error")
                                active_reservations.append(reservation)
                    else:
                        print(f"🔍 Debug: Skipping reservation {reservation.get('id')} with status {reservation.get('status')}")
            else:
                print(f"❌ API call failed with status {reservations_response.status_code}")
                print(f"❌ Response: {reservations_response.text}")
            
            print(f"🔍 Debug: Final active_reservations count: {len(active_reservations)}")
            
            if not active_reservations:
                dispatcher.utter_message(text="""ℹ️ **KHÔNG TÌM THẤY ĐẶT BÀN ACTIVE**
Bạn không có đặt bàn nào đang chờ xử lý (từ hôm nay trở đi).

📋 **Có thể:**
• Bàn đã được hủy trước đó
• Bạn chưa đặt bàn nào
• Bàn đã quá hạn (trước hôm nay)

📞 **Liên hệ:** Gọi 0901234567 nếu cần hỗ trợ""")
                return []
            
            # Nếu có nhiều reservation, hiển thị danh sách để chọn
            if len(active_reservations) > 1:
                message = "📋 **BẠN CÓ NHIỀU ĐẶT BÀN**\n\n"
                for i, res in enumerate(active_reservations, 1):
                    try:
                        if 'T' in str(res.get('reservation_date')):
                            res_datetime = datetime.fromisoformat(str(res.get('reservation_date')).replace('Z', ''))
                        else:
                            res_datetime = datetime.strptime(str(res.get('reservation_date')), '%Y-%m-%d')
                        
                        date_str = res_datetime.strftime('%d/%m/%Y')
                        time_str = res_datetime.strftime('%H:%M')
                        table_info = res.get('table', {})
                        table_number = table_info.get('number', res.get('table_id', 'N/A'))
                        party_size = res.get('party_size', 'N/A')
                        
                        message += f"{i}. **Bàn {table_number}** - {party_size} người\n"
                        message += f"   📅 {date_str} lúc {time_str}\n\n"
                    except:
                        message += f"{i}. Đặt bàn #{res.get('id', 'N/A')}\n\n"
                
                message += "� **Để hủy:** Nói 'Hủy bàn số [1/2/3...]' hoặc liên hệ nhân viên"
                dispatcher.utter_message(text=message)
                return []
            
            # Có 1 reservation duy nhất - hiển thị xác nhận
            reservation = active_reservations[0]
            
            try:
                if 'T' in str(reservation.get('reservation_date')):
                    res_datetime = datetime.fromisoformat(str(reservation.get('reservation_date')).replace('Z', ''))
                else:
                    res_datetime = datetime.strptime(str(reservation.get('reservation_date')), '%Y-%m-%d')
                
                date_str = res_datetime.strftime('%d/%m/%Y')
                time_str = res_datetime.strftime('%H:%M')
            except:
                date_str = str(reservation.get('reservation_date', 'N/A'))
                time_str = 'N/A'
            
            table_info = reservation.get('table', {})
            table_number = table_info.get('number', reservation.get('table_id', 'N/A'))
            party_size = reservation.get('party_size', 'N/A')
            
            confirmation_message = f"""❓ **XÁC NHẬN HỦY ĐẶT BÀN**

📋 **Thông tin đặt bàn:**
🪑 **Bàn:** {table_number}
👥 **Số người:** {party_size} người  
📅 **Ngày:** {date_str}
🕐 **Giờ:** {time_str}

⚠️ **Bạn có chắc chắn muốn hủy đặt bàn này không?**

💡 **Chọn:**
• Nói **"Có"** để xác nhận hủy
• Nói **"Không"** để giữ lại đặt bàn"""
            
            dispatcher.utter_message(text=confirmation_message)
            
            # Lưu reservation_id để xử lý xác nhận
            return [SlotSet("pending_cancellation_reservation_id", reservation.get('id')),
                    SlotSet("conversation_context", "cancel_reservation_confirmation")]
            
        except Exception as e:
            print(f"Error in ActionCancelReservation: {e}")
            dispatcher.utter_message(text="❌ Có lỗi khi tìm kiếm thông tin đặt bàn. Vui lòng thử lại sau.")
            return []


class ActionConfirmCancelReservation(Action):
    """Action để xác nhận hủy đặt bàn"""

    def name(self) -> Text:
        return "action_confirm_cancel_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        reservation_id = tracker.get_slot('pending_cancellation_reservation_id')
        
        if not reservation_id:
            dispatcher.utter_message(text="❌ Không tìm thấy thông tin đặt bàn cần hủy.")
            return []

        try:
            # Lấy auth headers từ token trong tracker, fallback to Rasa headers
            headers = get_auth_headers_from_tracker(tracker)

            # Hủy reservation bằng DELETE endpoint
            response = requests.delete(f"{API_BASE_URL}/orders/reservations/{reservation_id}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                reservation_info = response.json()
                
                try:
                    if 'T' in str(reservation_info.get('reservation_date')):
                        res_datetime = datetime.fromisoformat(str(reservation_info.get('reservation_date')).replace('Z', ''))
                    else:
                        res_datetime = datetime.strptime(str(reservation_info.get('reservation_date')), '%Y-%m-%d')
                    
                    date_str = res_datetime.strftime('%d/%m/%Y')
                    time_str = res_datetime.strftime('%H:%M')
                except:
                    date_str = str(reservation_info.get('reservation_date', 'N/A'))
                    time_str = 'N/A'
                
                table_info = reservation_info.get('table', {})
                table_number = table_info.get('number', reservation_info.get('table_id', 'N/A'))
                
                success_message = f"""✅ **ĐÃ HỦY ĐẶT BÀN THÀNH CÔNG**

📋 **Thông tin đã hủy:**
🪑 **Bàn:** {table_number}
📅 **Ngày:** {date_str}  
🕐 **Giờ:** {time_str}

💡 **Lưu ý:**
• Đặt bàn đã được hủy hoàn toàn
• Bàn sẽ được giải phóng cho khách khác
• Bạn có thể đặt bàn mới bất cứ lúc nào

🔄 **Đặt bàn mới:** Nói "Đặt bàn [số người] người ngày [dd/mm/yyyy] lúc [hh:mm]" """
                
                dispatcher.utter_message(text=success_message)
                
                # Clear slots
                return [
                    SlotSet("pending_cancellation_reservation_id", None),
                    SlotSet("conversation_context", None),
                    SlotSet("last_booking_id", None)
                ]
                
            elif response.status_code == 404:
                dispatcher.utter_message(text="❌ Không tìm thấy đặt bàn để hủy. Có thể bàn đã được hủy trước đó.")
            else:
                dispatcher.utter_message(text="❌ Không thể hủy đặt bàn lúc này. Vui lòng liên hệ nhân viên.")

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý hủy đặt bàn... Vui lòng đợi hoặc liên hệ nhân viên.")
        except requests.exceptions.RequestException as e:
            print(f"Cancellation error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi hệ thống khi hủy đặt bàn. Vui lòng liên hệ nhân viên: 0901234567.")
        except Exception as e:
            print(f"Unexpected cancellation error: {e}")
            dispatcher.utter_message(text="🔧 Lỗi bất ngờ khi hủy đặt bàn. Vui lòng liên hệ nhân viên: 0901234567.")
        
        return []