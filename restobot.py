#!/usr/bin/env python3
"""
RestoBot - All-in-One Launcher v3.0
🍽️ Trợ lý ảo thông minh cho nhà hàng
Updated: Sử dụng API structure có sẵn thay vì embedded API
"""

import sys
import signal
import subprocess
import time
import requests
import webbrowser
import warnings
import os
from pathlib import Path
from threading import Thread
import uvicorn

# Fix SQLAlchemy warnings và Rasa compatibility
os.environ['SQLALCHEMY_WARN_20'] = '0'
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'
os.environ['PYDANTIC_V1'] = '1'

# Suppress additional warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*pydantic.*")
warnings.filterwarnings("ignore", message=".*MovedIn20Warning.*")

class RestoBot:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def create_fastapi_app(self):
        """Tạo FastAPI app sử dụng API structure có sẵn"""
        from app.main import app
        
        # Thêm academic project description vào app existing
        app.title = "🍽️ RestoBot - Trợ lý ảo thông minh cho nhà hàng"
        app.description = """
        # Building an Intelligent Virtual Assistant for Restaurants
        ## Xây dựng trợ lý ảo thông minh cho nhà hàng
        
        ### 📋 Thông tin đề tài:
        - **Tên tiếng Việt**: Xây dựng trợ lý ảo thông minh cho nhà hàng
        - **Tên tiếng Anh**: Building an Intelligent Virtual Assistant for Restaurants
        - **Từ khóa**: application, artificial intelligence, chatbot, machine learning, management system, NLP, retail, web app, software design
        
        ### 🎯 Mục đích và ý nghĩa:
        Đề tài nhằm giải quyết thách thức về tối ưu hóa trải nghiệm khách hàng và hiệu quả vận hành trong ngành nhà hàng bằng cách phát triển một trợ lý ảo thông minh trong bối cảnh công nghiệp 4.0.
        
        ### 🚀 Tính năng chính:
        - 🤖 **Trợ lý ảo AI**: Rasa NLU/Core với khả năng hiểu tiếng Việt tự nhiên
        - 🍽️ **Quản lý thực đơn**: CRUD danh mục và món ăn với dữ liệu tiếng Việt
        - 🪑 **Quản lý bàn ăn**: Đặt bàn, kiểm tra trạng thái, quản lý reservation
        - 📦 **Quản lý đơn hàng**: Tạo, cập nhật, theo dõi đơn hàng thông minh
        - 👥 **Quản lý người dùng**: Phân quyền khách hàng/nhân viên/quản lý
        - 📊 **Thống kê & báo cáo**: Dashboard analytics và revenue tracking
        - 🔐 **Bảo mật**: JWT authentication với phân quyền đa cấp
        
        ### 🛠️ Technology Stack:
        - **Backend**: Python 3.9+ với FastAPI (RESTful API hiệu suất cao)
        - **Frontend**: ReactJS 18+ với Material-UI/Ant Design
        - **Database**: PostgreSQL 14+ với SQLAlchemy ORM
        - **NLP & AI**: Rasa Framework (NLU + Core) cho Conversational AI
        - **ML Libraries**: NLTK/SpaCy, Transformer models (BERT multilingual)
        - **Deployment**: Docker & Docker Compose
        - **Version Control**: Git với GitHub/GitLab
        
        ### 🏗️ Kiến trúc Microservices:
        1. **Client**: ReactJS Web App với chat interface
        2. **API Gateway**: Điểm truy cập duy nhất
        3. **Backend Service**: FastAPI với business logic
        4. **NLP Service**: Rasa với Vietnamese conversation capability
        5. **Database**: PostgreSQL với optimized schema
        
        ### 📈 Kế hoạch 15 tuần:
        - **Tuần 1-2**: Nghiên cứu & thiết kế hệ thống
        - **Tuần 3-4**: Backend core development
        - **Tuần 5-7**: NLP Service với Rasa
        - **Tuần 8-9**: Frontend development
        - **Tuần 10-11**: Integration & testing
        - **Tuần 12-13**: Deployment & UAT
        - **Tuần 14-15**: Documentation & delivery
        """
        app.version = "2.0.0"
        app.contact = {
            "name": "Nhóm phát triển RestoBot",
            "email": "restobot.dev@university.edu.vn"
        }
        app.license_info = {
            "name": "Academic Project License",
            "url": "https://university.edu.vn/academic-license"
        }
        
        # Thêm các endpoint bổ sung cho chatbot demo
        from fastapi import HTTPException
        from fastapi.responses import RedirectResponse
        
        @app.get("/", include_in_schema=False)
        async def redirect_to_docs():
            return RedirectResponse(url="/docs")
        
        @app.post("/webhook", tags=["Chatbot"])
        async def rasa_webhook(data: dict):
            """Webhook cho Rasa chatbot"""
            return {"status": "received", "data": data}
            
        @app.post("/chat", tags=["Chatbot"])
        async def chat_endpoint(message: dict):
            """Endpoint chat đơn giản"""
            user_message = message.get("message", "")
            return {
                "response": f"Đã nhận tin nhắn: {user_message}",
                "type": "text"
            }
        
        return app
    
    def start_fastapi(self):
        """Khởi động FastAPI server với API structure có sẵn"""
        print("🚀 Khởi động FastAPI server...")
        
        try:
            app = self.create_fastapi_app()
            print("📍 FastAPI URL: http://localhost:8000")
            print("📍 API Docs: http://localhost:8000/docs")
            print("📍 Real API Endpoints:")
            print("   • /api/v1/auth/ - Authentication endpoints")
            print("   • /api/v1/users/ - User management")  
            print("   • /api/v1/menu/ - Menu & categories")
            print("   • /api/v1/tables/ - Table management")
            print("   • /api/v1/orders/ - Order management")
            
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
            
        except KeyboardInterrupt:
            print("⏹️ FastAPI đã dừng")
        except Exception as e:
            print(f"❌ FastAPI lỗi: {e}")
    
    def start_rasa_actions(self):
        """Khởi động Rasa Actions"""
        print("⚡ Khởi động Rasa Actions...")
        
        try:
            rasa_dir = Path("rasa_bot")
            if not rasa_dir.exists():
                print("⚠️ Thư mục rasa_bot không tồn tại")
                return
                
            process = subprocess.Popen([
                sys.executable, "-m", "rasa", "run", "actions",
                "--port", "5055"
            ], cwd=rasa_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.processes.append(process)
            time.sleep(2)
            print("✅ Rasa Actions started (Port 5055)")
            
        except Exception as e:
            print(f"⚠️ Rasa Actions không khởi động được: {e}")
    
    def start_rasa_server(self):
        """Khởi động Rasa server"""
        print("🤖 Khởi động Rasa server...")
        
        try:
            rasa_dir = Path("rasa_bot")
            if not rasa_dir.exists():
                print("⚠️ Thư mục rasa_bot không tồn tại")
                return
            
            # Kiểm tra model
            models_dir = rasa_dir / "models"
            if not models_dir.exists() or not list(models_dir.glob("*.tar.gz")):
                print("📦 Training Rasa model...")
                train_result = subprocess.run([
                    sys.executable, "-m", "rasa", "train"
                ], cwd=rasa_dir, capture_output=True, text=True)
                
                if train_result.returncode != 0:
                    print("❌ Model training thất bại")
                    print("💡 Chỉ FastAPI sẽ hoạt động")
                    return
                    
                print("✅ Model đã được train")
            
            # Start Rasa server với debug mode
            process = subprocess.Popen([
                sys.executable, "-m", "rasa", "run",
                "--enable-api", "--cors", "*", "--port", "5005", "--debug"
            ], cwd=rasa_dir)
            
            self.processes.append(process)
            time.sleep(8)  # Tăng thời gian chờ để Rasa load model
            
            # Kiểm tra process còn sống không
            if process.poll() is None:
                print("✅ Rasa server started (Port 5005)")
                print("📍 Rasa API: http://localhost:5005")
            else:
                print("❌ Rasa server đã crash ngay sau khi start")
                return
            
        except Exception as e:
            print(f"❌ Rasa server lỗi: {e}")
            print("💡 Chỉ FastAPI sẽ hoạt động")
    
    def open_chat_interface(self):
        """Mở giao diện chat"""
        time.sleep(5)  # Đợi services khởi động
        
        try:
            chat_file = Path("chat_interface.html")
            if chat_file.exists():
                webbrowser.open(f"file://{chat_file.absolute()}")
                print("🌐 Đã mở chat interface trong browser")
            else:
                print("⚠️ File chat_interface.html không tồn tại")
        except Exception as e:
            print(f"⚠️ Không thể mở browser: {e}")
    
    def test_services(self):
        """Test services sau khi khởi động"""
        time.sleep(12)  # Tăng thời gian chờ cho Rasa load model
        
        print("\n🧪 Kiểm tra services...")
        
        # Test FastAPI
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ FastAPI: Hoạt động bình thường")
                
                # Test API endpoints
                try:
                    # Test menu API
                    menu_response = requests.get("http://localhost:8000/api/v1/menu/categories", timeout=5)
                    if menu_response.status_code == 200:
                        print("✅ Menu API: Ready")
                    
                    # Test users API  
                    users_response = requests.get("http://localhost:8000/api/v1/users/", timeout=5)
                    if users_response.status_code in [200, 401]:  # 401 is expected without auth
                        print("✅ Users API: Ready")
                        
                    # Test tables API
                    tables_response = requests.get("http://localhost:8000/api/v1/tables/", timeout=5)
                    if tables_response.status_code in [200, 401]:
                        print("✅ Tables API: Ready")
                        
                except Exception as api_e:
                    print(f"⚠️ Some API endpoints may need authentication: {api_e}")
                    
            else:
                print("❌ FastAPI: Có lỗi")
        except Exception as e:
            print(f"❌ FastAPI: Không truy cập được - {e}")
        
        # Test Rasa với retry logic
        rasa_working = False
        for attempt in range(3):
            try:
                # Test Rasa status endpoint trước
                status_response = requests.get("http://localhost:5005/status", timeout=10)
                if status_response.status_code == 200:
                    print("✅ Rasa: Hoạt động bình thường")
                    
                    # Test parse endpoint
                    parse_response = requests.post(
                        "http://localhost:5005/model/parse",
                        json={"text": "xin chào"},
                        timeout=10
                    )
                    if parse_response.status_code == 200:
                        print("✅ Rasa NLU: Ready")
                        rasa_working = True
                        break
                else:
                    print(f"⚠️ Rasa attempt {attempt + 1}: Status {status_response.status_code}")
                    time.sleep(5)
                    
            except requests.exceptions.ConnectionError:
                print(f"⚠️ Rasa attempt {attempt + 1}: Connection failed")
                if attempt < 2:
                    time.sleep(5)
            except Exception as e:
                print(f"⚠️ Rasa attempt {attempt + 1}: {e}")
                if attempt < 2:
                    time.sleep(5)
        
        if not rasa_working:
            print("💡 Chỉ FastAPI hoạt động. Rasa có thể cần thời gian load model lâu hơn.")
    
    def signal_handler(self, sig, frame):
        """Xử lý tín hiệu dừng"""
        print("\n🛑 Đang dừng tất cả services...")
        self.running = False
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass
        
        print("👋 Tất cả services đã dừng!")
        sys.exit(0)
    
    def run(self):
        """Chạy toàn bộ hệ thống"""
        print("=" * 60)
        print("🍽️  RESTOBOT - All-in-One Launcher v3.0")
        print("🔧 Using Real API Structure | PostgreSQL Ready")
        print("=" * 60)
        
        # Setup signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("🚀 Đang khởi động services...")
        
        # Start Rasa Actions trong background
        actions_thread = Thread(target=self.start_rasa_actions, daemon=True)
        actions_thread.start()
        time.sleep(3)
        
        # Start Rasa Server trong background
        rasa_thread = Thread(target=self.start_rasa_server, daemon=True)
        rasa_thread.start()
        time.sleep(3)
        
        # Start test services trong background
        test_thread = Thread(target=self.test_services, daemon=True)
        test_thread.start()
        
        # Start chat interface trong background
        chat_thread = Thread(target=self.open_chat_interface, daemon=True)
        chat_thread.start()
        
        # Start FastAPI (main thread)
        self.start_fastapi()

if __name__ == "__main__":
    bot = RestoBot()
    bot.run()