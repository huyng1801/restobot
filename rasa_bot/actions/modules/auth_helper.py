"""
Authentication Helper for RestoBot API
Xử lý authentication với FastAPI backend
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional


class AuthHelper:
    """Helper class để xử lý authentication với FastAPI backend"""

    # Thông tin đăng nhập admin để fallback
    ADMIN_CREDENTIALS = {
        "username": "admin",
        "password": "admin123"
    }

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.admin_token = None
        self.admin_token_expires = None

    def verify_user_token(self, token: str) -> Optional[Dict]:
        """Xác thực token của user và trả về thông tin user"""
        if not token:
            return None
            
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ User authenticated: {user_data.get('username', 'Unknown')}")
                return user_data
            else:
                print(f"❌ Token verification failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error verifying token: {e}")
            return None

    def get_headers_with_user_token(self, user_token: str = None) -> Dict[str, str]:
        """Lấy headers với user token hoặc fallback to admin token"""
        if user_token:
            # Thử sử dụng user token trước
            user_info = self.verify_user_token(user_token)
            if user_info:
                return {
                    "Authorization": f"Bearer {user_token}",
                    "Content-Type": "application/json"
                }
        
        # Fallback to admin token
        return self.get_admin_headers()

    def get_admin_headers(self) -> Dict[str, str]:
        """Lấy headers với admin token"""
        if not self.admin_token or (self.admin_token_expires and datetime.now() > self.admin_token_expires):
            self._admin_login()
        
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }

    def get_headers(self) -> Dict[str, str]:
        """Backwards compatibility - sử dụng admin token"""
        return self.get_admin_headers()

    def _admin_login(self):
        """Authenticate với admin credentials và lấy access token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": self.ADMIN_CREDENTIALS["username"],
                    "password": self.ADMIN_CREDENTIALS["password"]
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                # Token expires in 30 minutes, refresh slightly before
                self.admin_token_expires = datetime.now() + timedelta(minutes=25)
                print(f"✅ Admin authenticated successfully")
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                self.admin_token = None
        except requests.exceptions.RequestException as e:
            print(f"❌ Admin authentication error: {e}")
            self.admin_token = None

    def _login(self):
        """Backwards compatibility"""
        self._admin_login()


def get_authenticated_user_from_tracker(tracker) -> Optional[Dict]:
    """
    Extract và xác thực user từ tracker metadata
    Returns: User info dict nếu authenticated, None nếu không
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
            
        # Lấy auth token
        auth_token = metadata.get('auth_token')
        if not auth_token:
            print("❌ No auth token found in metadata")
            return None
            
        # Verify token với FastAPI
        auth_helper_instance = AuthHelper()
        user_info = auth_helper_instance.verify_user_token(auth_token)
        
        if user_info:
            print(f"✅ User authenticated from tracker: {user_info.get('username')}")
            return user_info
        else:
            print("❌ Token verification failed")
            return None
            
    except Exception as e:
        print(f"❌ Error getting authenticated user from tracker: {e}")
        return None


def get_auth_headers_from_tracker(tracker) -> Dict[str, str]:
    """
    Lấy auth headers từ tracker hoặc fallback to admin
    """
    try:
        latest_message = tracker.latest_message
        metadata = latest_message.get('metadata', {}) if latest_message else {}
        auth_token = metadata.get('auth_token')
        
        auth_helper_instance = AuthHelper()
        return auth_helper_instance.get_headers_with_user_token(auth_token)
        
    except Exception as e:
        print(f"❌ Error getting auth headers from tracker: {e}")
        # Fallback to admin headers
        return AuthHelper().get_admin_headers()


# Global auth helper instance
auth_helper = AuthHelper()