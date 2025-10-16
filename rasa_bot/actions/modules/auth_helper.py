"""
Authentication Helper for RestoBot API
Xử lý authentication với FastAPI backend
"""
import requests
from datetime import datetime, timedelta
from typing import Dict


class AuthHelper:
    """Helper class để xử lý authentication với FastAPI backend"""

    # Thông tin đăng nhập admin để tự động authenticate
    ADMIN_CREDENTIALS = {
        "username": "admin",
        "password": "admin123"
    }

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.username = self.ADMIN_CREDENTIALS["username"]
        self.password = self.ADMIN_CREDENTIALS["password"]
        self.token = None
        self.token_expires = None

    def get_headers(self) -> Dict[str, str]:
        """Lấy headers với authentication token"""
        if not self.token or (self.token_expires and datetime.now() > self.token_expires):
            self._login()
        
        if self.token:
            return {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        return {"Content-Type": "application/json"} # Fallback if login fails

    def _login(self):
        """Authenticate và lấy access token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": self.username,
                    "password": self.password
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                # Token expires in 30 minutes, refresh slightly before
                self.token_expires = datetime.now() + timedelta(minutes=25)
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}")
                self.token = None
        except requests.exceptions.RequestException as e:
            print(f"Authentication error: {e}")
            self.token = None


# Global auth helper instance
auth_helper = AuthHelper()