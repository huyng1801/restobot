"""
Business Hours Management for RestoBot
"""
from datetime import datetime, time, timedelta
from typing import Dict, List, Tuple
import pytz

class BusinessHours:
    """Manages restaurant business hours and validation"""
    
    # Define business hours (24-hour format)
    BUSINESS_HOURS = {
        0: [(time(10, 0), time(22, 0))],  # Monday: 10:00-22:00
        1: [(time(10, 0), time(22, 0))],  # Tuesday: 10:00-22:00  
        2: [(time(10, 0), time(22, 0))],  # Wednesday: 10:00-22:00
        3: [(time(10, 0), time(22, 0))],  # Thursday: 10:00-22:00
        4: [(time(10, 0), time(22, 0))],  # Friday: 10:00-22:00
        5: [(time(10, 0), time(22, 0))],  # Saturday: 10:00-22:00
        6: [(time(10, 0), time(22, 0))],  # Sunday: 10:00-22:00
    }
    
    # Special hours (lunch break)
    LUNCH_BREAK = {
        0: (time(14, 0), time(17, 0)),  # Monday: 14:00-17:00 closed
        1: (time(14, 0), time(17, 0)),  # Tuesday: 14:00-17:00 closed
        2: (time(14, 0), time(17, 0)),  # Wednesday: 14:00-17:00 closed
        3: (time(14, 0), time(17, 0)),  # Thursday: 14:00-17:00 closed
        4: (time(14, 0), time(17, 0)),  # Friday: 14:00-17:00 closed
        5: None,  # Saturday: No lunch break
        6: None,  # Sunday: No lunch break
    }
    
    @classmethod
    def is_open_now(cls) -> bool:
        """Check if restaurant is currently open"""
        now = datetime.now()
        return cls.is_open_at_time(now.weekday(), now.time())
    
    @classmethod
    def is_open_at_time(cls, weekday: int, check_time: time) -> bool:
        """Check if restaurant is open at specific day and time"""
        if weekday not in cls.BUSINESS_HOURS:
            return False
            
        # Check if within business hours
        business_hours = cls.BUSINESS_HOURS[weekday]
        is_open = False
        
        for start_time, end_time in business_hours:
            if start_time <= check_time <= end_time:
                is_open = True
                break
        
        if not is_open:
            return False
            
        # Check lunch break
        lunch_break = cls.LUNCH_BREAK.get(weekday)
        if lunch_break:
            break_start, break_end = lunch_break
            if break_start <= check_time <= break_end:
                return False
                
        return True
    
    @classmethod
    def get_next_opening_time(cls, from_datetime: datetime = None) -> datetime:
        """Get next opening time"""
        if from_datetime is None:
            from_datetime = datetime.now()
            
        # Try same day first
        weekday = from_datetime.weekday()
        
        # Check if restaurant opens later today
        business_hours = cls.BUSINESS_HOURS.get(weekday, [])
        for start_time, end_time in business_hours:
            # Check if we're before opening time
            if from_datetime.time() < start_time:
                return from_datetime.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
            
            # Check if we're in lunch break
            lunch_break = cls.LUNCH_BREAK.get(weekday)
            if lunch_break:
                break_start, break_end = lunch_break
                if break_start <= from_datetime.time() <= break_end:
                    return from_datetime.replace(hour=break_end.hour, minute=break_end.minute, second=0, microsecond=0)
        
        # Find next day opening
        for i in range(1, 8):  # Check next 7 days
            next_day = (weekday + i) % 7
            next_hours = cls.BUSINESS_HOURS.get(next_day, [])
            if next_hours:
                start_time = next_hours[0][0]
                next_date = from_datetime.date() + timedelta(days=i)
                return datetime.combine(next_date, start_time)
        
        return None
    
    @classmethod
    def validate_reservation_time(cls, reservation_datetime: datetime) -> Tuple[bool, str]:
        """Validate if reservation time is acceptable"""
        weekday = reservation_datetime.weekday()
        check_time = reservation_datetime.time()
        
        # Check if day has business hours
        if weekday not in cls.BUSINESS_HOURS:
            return False, "Nhà hàng không mở cửa vào ngày này"
        
        # Check if within business hours
        business_hours = cls.BUSINESS_HOURS[weekday]
        is_within_hours = False
        
        for start_time, end_time in business_hours:
            if start_time <= check_time <= end_time:
                is_within_hours = True
                break
                
        if not is_within_hours:
            hours_str = ", ".join([f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}" for start, end in business_hours])
            return False, f"Giờ đặt bàn phải trong khung giờ mở cửa: {hours_str}"
        
        # Check lunch break
        lunch_break = cls.LUNCH_BREAK.get(weekday)
        if lunch_break:
            break_start, break_end = lunch_break
            if break_start <= check_time <= break_end:
                return False, f"Nhà hàng nghỉ trưa từ {break_start.strftime('%H:%M')} đến {break_end.strftime('%H:%M')}"
        
        # Check if reservation is at least 1 hour from now
        now = datetime.now()
        if reservation_datetime <= now:
            return False, "Thời gian đặt bàn phải trong tương lai"
            
        if (reservation_datetime - now).total_seconds() < 3600:  # 1 hour
            return False, "Vui lòng đặt bàn trước ít nhất 1 giờ"
        
        return True, "OK"
    
    @classmethod
    def get_business_hours_text(cls) -> str:
        """Get formatted business hours text"""
        hours_text = "🕒 **GIỜ MỞ CỬA:**\n"
        
        days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        
        for i, day_name in enumerate(days):
            hours = cls.BUSINESS_HOURS.get(i, [])
            lunch_break = cls.LUNCH_BREAK.get(i)
            
            if not hours:
                hours_text += f"• **{day_name}:** Đóng cửa\n"
            else:
                hours_str = ", ".join([f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}" for start, end in hours])
                hours_text += f"• **{day_name}:** {hours_str}"
                
                if lunch_break:
                    break_start, break_end = lunch_break
                    hours_text += f" (Nghỉ trưa: {break_start.strftime('%H:%M')}-{break_end.strftime('%H:%M')})"
                
                hours_text += "\n"
        
        return hours_text