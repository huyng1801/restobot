"""
Table Booking Actions for RestoBot
Xử lý các action liên quan đến đặt bàn
"""
import requests
from datetime import datetime, timedelta
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .auth_helper import auth_helper

# URL của FastAPI backend
API_BASE_URL = "http://localhost:8000/api/v1"


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
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

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
            import re
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
                import re
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
            time_formats = ["%H:%M", "%H.%M", "%H:%M:%S"]
            time_obj = None
            
            # Clean up time string
            time_str = reservation_time.strip().lower()
            
            # Convert Vietnamese time phrases
            time_replacements = {
                "giờ sáng": ":00",
                "giờ chiều": ":00", 
                "giờ tối": ":00",
                "rưỡi": ":30",
                "giờ": ":00",
                "h": ":00"
            }
            
            for vn_phrase, replacement in time_replacements.items():
                if vn_phrase in time_str:
                    time_str = time_str.replace(vn_phrase, replacement)
                    break
            
            # Try to parse the time
            for time_format in time_formats:
                try:
                    time_obj = datetime.strptime(time_str, time_format)
                    break
                except ValueError:
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

            # Convert back to standard format for API call
            standard_date = date_obj.strftime("%d/%m/%Y")
            standard_time = time_obj.strftime("%H:%M")

        except Exception as e:
            print(f"Validation error: {e}")
            dispatcher.utter_message(text="""❌ **LỖI XỬ LÝ THÔNG TIN**
Có lỗi khi xử lý thông tin đặt bàn.

📝 **Vui lòng thử lại với format:**
"Đặt bàn [số người] người ngày [dd/mm/yyyy] lúc [hh:mm]"

💡 **Ví dụ:** "Đặt bàn 4 người ngày 20/10/2025 lúc 19:00" """)
            return []
                        
        # Attempt to book the table via API
        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống đặt bàn. Vui lòng thử lại sau.")
                return []

            booking_data = {
                "customer_name": "Khách hàng chatbot",  # Placeholder, could be asked from user
                "customer_phone": "0000000000",       # Placeholder
                "number_of_guests": num_people_int,
                "reservation_date": standard_date,
                "reservation_time": standard_time,
                "special_requests": ""
            }
            
            print(f"DEBUG - Booking data: {booking_data}")
            
            response = requests.post(
                f"{API_BASE_URL}/tables/book",
                headers=headers,
                json=booking_data,
                timeout=10
            )
            
            if response.status_code == 201:
                booking_info = response.json()
                confirmation_message = f"""✅ **ĐẶT BÀN THÀNH CÔNG**

📋 **Thông tin đặt bàn:**
• **Mã đặt bàn:** #{booking_info.get('id', 'N/A')}
• **Số khách:** {num_people_int} người
• **Ngày:** {standard_date}
• **Giờ:** {standard_time}
• **Bàn số:** {booking_info.get('table_number', 'Sẽ được sắp xếp')}

📞 **Lưu ý:** Vui lòng đến đúng giờ. Nếu muốn hủy, liên hệ trước 2 giờ.
🍽️ Bạn có muốn xem thực đơn để gọi món trước không?"""
                
                dispatcher.utter_message(text=confirmation_message)
                
                # Store booking info in slots
                return [
                    SlotSet("number_of_people", num_people_int),
                    SlotSet("reservation_date", standard_date),
                    SlotSet("reservation_time", standard_time),
                    SlotSet("last_booking_id", booking_info.get('id'))
                ]
                
            elif response.status_code == 409: # Conflict, meaning table might be occupied
                dispatcher.utter_message(text=f"""😔 **KHÔNG CÒN BÀN TRỐNG**
Thời gian {standard_time} ngày {standard_date} đã hết chỗ.

🕐 **Khung giờ gợi ý:**
• 11:00-12:00 (ít khách)
• 14:00-17:00 (thoải mái)
• 20:00-21:30 (còn chỗ)

📝 **Thử lại:** "Đặt bàn {num_people_int} người ngày {standard_date} lúc [giờ khác]" """)
            else:
                dispatcher.utter_message(text=f"❌ Không thể đặt bàn lúc này. Vui lòng thử lại hoặc gọi điện đặt bàn. (Mã lỗi: {response.status_code})")

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý đặt bàn... Vui lòng đợi hoặc liên hệ nhân viên.")
        except requests.exceptions.RequestException as e:
            print(f"Booking error: {e}")
            dispatcher.utter_message(text=f"🔧 Lỗi hệ thống đặt bàn. Vui lòng liên hệ nhân viên: 0123-456-789.")
        except Exception as e:
            print(f"Unexpected booking error: {e}")
            dispatcher.utter_message(text=f"🔧 Lỗi bất ngờ khi đặt bàn. Vui lòng liên hệ nhân viên: 0123-456-789.")

        return []


class ActionCancelReservation(Action):
    """Action để hủy đặt bàn"""

    def name(self) -> Text:
        return "action_cancel_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        reservation_id = tracker.get_slot('last_booking_id')
        reservation_date = tracker.get_slot('reservation_date')
        reservation_time = tracker.get_slot('reservation_time')
        number_of_people = tracker.get_slot('number_of_people')

        if not reservation_id:
            dispatcher.utter_message(text="""ℹ️ **KHÔNG TÌM THẤY ĐẶT BÀN**
Bạn chưa có đặt bàn nào trong hệ thống hoặc chúng tôi không lưu mã đặt bàn gần nhất.

📋 **Để hủy đặt bàn:**
• Vui lòng cung cấp mã đặt bàn (nếu có)
• Hoặc số điện thoại đặt bàn
• Hoặc liên hệ trực tiếp: 📞 **0901234567**""")
            return []

        try:
            headers = auth_helper.get_headers()
            if not headers.get("Authorization"):
                dispatcher.utter_message(text="⚠️ Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return []

            response = requests.delete(f"{API_BASE_URL}/tables/book/{reservation_id}", headers=headers, timeout=5)
            
            if response.status_code == 200: # Assuming 200 for successful deletion
                cancellation_text = f"""✅ **ĐẶT BÀN ĐÃ ĐƯỢC HỦY THÀNH CÔNG**

🗓️ **Thông tin đã hủy:**
• Mã đặt bàn: #{reservation_id}
• Ngày: {reservation_date or 'N/A'}              
• Giờ: {reservation_time or 'N/A'}
• Số người: {number_of_people or 'N/A'}

💰 **Phí hủy:** Miễn phí (hủy trước 2 giờ)
📞 **Xác nhận:** Nhân viên có thể gọi lại để xác nhận chi tiết.

🔄 **Đặt bàn mới:** Nói "đặt bàn" để đặt lại"""
                dispatcher.utter_message(text=cancellation_text)
                
                # Clear reservation slots
                return [
                    SlotSet("reservation_date", None),
                    SlotSet("reservation_time", None),
                    SlotSet("number_of_people", None),
                    SlotSet("last_booking_id", None)
                ]
            elif response.status_code == 404:
                dispatcher.utter_message(text=f"❌ Không tìm thấy đặt bàn với mã **#{reservation_id}**. Vui lòng kiểm tra lại hoặc liên hệ nhân viên.")
            else:
                dispatcher.utter_message(text=f"❌ Không thể hủy đặt bàn lúc này. Vui lòng thử lại hoặc gọi điện. (Mã lỗi: {response.status_code})")

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="⏱️ Kết nối chậm. Đang xử lý hủy đặt bàn... Vui lòng đợi hoặc liên hệ nhân viên.")
        except requests.exceptions.RequestException as e:
            print(f"Cancellation error: {e}")
            dispatcher.utter_message(text=f"🔧 Lỗi hệ thống khi hủy đặt bàn. Vui lòng liên hệ nhân viên: 0123-456-789.")
        except Exception as e:
            print(f"Unexpected cancellation error: {e}")
            dispatcher.utter_message(text=f"🔧 Lỗi bất ngờ khi hủy đặt bàn. Vui lòng liên hệ nhân viên: 0123-456-789.")
        
        return []