"""
Authentication Helper for RestoBot API
Xử lý authentication với token từ frontend React
"""
import requests
from typing import Dict, Optional


class AuthHelper:
    """Helper class để xử lý authentication với token từ frontend"""

    def get_headers_with_token(self, token: str) -> Dict[str, str]:
        """Tạo headers với token từ frontend"""
        if not token:
            print("❌ No token provided")
            return {}
            
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_rasa_headers(self) -> Dict[str, str]:
        """Tạo headers cho Rasa requests (bypass authentication)"""
        return {
            "X-Rasa-Request": "true",
            "Content-Type": "application/json"
        }

def get_authenticated_user_from_tracker(tracker) -> Optional[Dict]:
    """
    Extract user info từ tracker metadata (không cần verify token)
    Returns: User info dict nếu có, None nếu không
    """
    try:
        # Lấy metadata từ latest message
        latest_message = tracker.latest_message
        if not latest_message:
            print("❌ No latest message found in tracker")
            return None
            
        metadata = latest_message.get('metadata', {})
        if not metadata:
            print("❌ No metadata found in message")
            return None
            
        # Lấy user_info trực tiếp từ metadata (đã được gửi từ frontend)
        user_info = metadata.get('user_info')
        if not user_info:
            print("❌ No user_info found in metadata")
            return None
            
        print(f"✅ User info from tracker: {user_info.get('username', 'Unknown')}")
        return user_info
            
    except Exception as e:
        print(f"❌ Error getting user from tracker: {e}")
        return None


def get_auth_headers_from_tracker(tracker) -> Dict[str, str]:
    """
    Lấy auth headers từ auth_token trong tracker metadata
    Fallback to Rasa headers nếu không có token
    """
    try:
        latest_message = tracker.latest_message
        if not latest_message:
            print("❌ No latest message found in tracker, using Rasa headers")
            return AuthHelper().get_rasa_headers()
            
        metadata = latest_message.get('metadata', {})
        if not metadata:
            print("❌ No metadata found in message, using Rasa headers")
            return AuthHelper().get_rasa_headers()
            
        # Lấy auth_token từ metadata
        auth_token = metadata.get('auth_token')
        if not auth_token:
            print("❌ No auth_token found in metadata, using Rasa headers")
            return AuthHelper().get_rasa_headers()
        
        # Tạo headers với token
        auth_helper_instance = AuthHelper()
        return auth_helper_instance.get_headers_with_token(auth_token)
        
    except Exception as e:
        print(f"❌ Error getting auth headers from tracker: {e}, using Rasa headers")
        return AuthHelper().get_rasa_headers()


# Global auth helper instance
auth_helper = AuthHelper()