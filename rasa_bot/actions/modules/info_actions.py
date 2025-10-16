"""
Restaurant Information Actions for RestoBot
Xử lý các action liên quan đến thông tin nhà hàng
"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionShowOpeningHours(Action):
    """Action để hiển thị giờ mở cửa"""

    def name(self) -> Text:
        return "action_show_opening_hours"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = """🕐 **GIỜ MỞ CỬA NHÀ HÀNG**

📅 **Thứ 2 - Chủ nhật:**
• **Sáng:** 06:00 - 10:00
• **Trưa:** 11:00 - 14:00  
• **Tối:** 17:00 - 22:00

🎉 **Ngày lễ:** Mở cửa bình thường
🚫 **Nghỉ:** Không có ngày nghỉ trong tuần

📞 **Liên hệ:** 0901234567 (24/7)
💡 **Lưu ý:** Đặt bàn trước để có chỗ tốt nhất!"""

        dispatcher.utter_message(text=message)
        return []


class ActionShowAddress(Action):
    """Action để hiển thị địa chỉ nhà hàng"""

    def name(self) -> Text:
        return "action_show_address"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = """📍 **ĐỊA CHỈ NHÀ HÀNG**

🏢 **Nhà hàng RestoBot**
📌 123 Đường Nguyễn Huệ, Quận 1, TP.HCM

🚗 **Cách đến:**
• **Xe máy:** Có bãi gửi xe miễn phí
• **Ô tô:** Bãi đậu xe trước nhà hàng
• **Xe bus:** Tuyến 01, 05, 19 (Dừng Nguyễn Huệ)
• **Grab/Taxi:** Báo địa chỉ "123 Nguyễn Huệ Q1"

🏪 **Landmark:** 
• Gần chợ Bến Thành (300m)
• Đối diện tòa nhà Bitexco
• Cạnh ngân hàng Vietcombank

📞 **Liên hệ:** 0901234567"""

        dispatcher.utter_message(text=message)
        return []


class ActionShowContact(Action):
    """Action để hiển thị thông tin liên hệ"""

    def name(self) -> Text:
        return "action_show_contact"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = """📞 **THÔNG TIN LIÊN HỆ**

☎️ **Hotline:** 0901234567 (24/7)
📧 **Email:** info@restobot.vn
🌐 **Website:** www.restobot.vn

📱 **Mạng xã hội:**
• **Facebook:** @RestoBotVN
• **Instagram:** @restobot.official  
• **Zalo:** 0901234567

🕐 **Thời gian hỗ trợ:**
• **Đặt bàn:** 24/7 (online/phone)
• **Tư vấn menu:** 06:00 - 22:00
• **Khiếu nại:** 08:00 - 20:00

💬 **Chat trực tuyến:** Đang chat với tôi đây! 😊"""

        dispatcher.utter_message(text=message)
        return []


class ActionShowPromotions(Action):
    """Action để hiển thị khuyến mãi"""

    def name(self) -> Text:
        return "action_show_promotions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = """🎉 **KHUYẾN MÃI HIỆN TẠI**

💥 **Khuyến mãi tháng 10:**
• **Giảm 20%** cho hóa đơn từ 500K
• **Tặng khai vị** cho bàn từ 4 người  
• **Happy Hour** 14:00-17:00: Giảm 15% đồ uống

🎂 **Chương trình đặc biệt:**
• **Sinh nhật:** Tặng bánh kem (đặt bàn trước)
• **Nhóm 8+ người:** Giảm 10% tổng bill
• **Khách VIP:** Tích điểm đổi quà

📅 **Sự kiện cuối tuần:**
• **Thứ 7-CN:** Buffet trưa chỉ 299K/người
• **Nhạc sống:** 19:00-21:00 (Thứ 6-7)

🏷️ **Thẻ thành viên:**
• **Bạc:** 5% mọi hóa đơn  
• **Vàng:** 8% + ưu tiên đặt bàn
• **Kim cương:** 12% + phòng VIP miễn phí

💳 **Thanh toán:** VISA/Mastercard giảm thêm 5%
📞 **Đăng ký:** 0901234567"""

        dispatcher.utter_message(text=message)
        return []


class ActionRecommendDishes(Action):
    """Action để gợi ý món ăn"""

    def name(self) -> Text:
        return "action_recommend_dishes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = """👨‍🍳 **GỢI Ý MÓN ĂN TỪ ĐẦU BẾP**

🔥 **Món signature (đặc biệt):**
• **Phở Bò RestoBot** - 89K ⭐⭐⭐⭐⭐
• **Bún Chả Hà Nội** - 75K ⭐⭐⭐⭐⭐  
• **Cơm Tấm Sài Gòn** - 65K ⭐⭐⭐⭐

🍲 **Món cho nhóm:**
• **Lẩu Thái chua cay** (4-6 người) - 299K
• **Gà nướng nguyên con** - 189K
• **Chả cá Lã Vọng** - 129K

🥗 **Healthy choice:**
• **Salad bơ tôm** - 85K  
• **Canh chua chay** - 45K
• **Gỏi cuốn tôm thịt** - 55K

🍜 **Combo tiết kiệm:**
• **Phở + Chả giò + Nước** - 99K
• **Cơm + Canh + Trà đá** - 79K  
• **Bún bò + Nem nướng** - 89K

💡 **Theo thời tiết hôm nay:** Nên thử món nước nóng hoặc lẩu!
🎯 **Bạn thích ăn gì:** Cay, ngọt, chua hay đậm đà?"""

        dispatcher.utter_message(text=message)
        return []