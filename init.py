"""
初始化模組 - 用於初始化 LINE Bot 與 Google Calendar 整合
"""
import os
import sys
from src.user_manager import UserManager
from src.calendar_manager import CalendarManager

def init_environment():
    """
    初始化環境變數與資料夾
    """
    # 確保必要的資料夾存在
    os.makedirs("./docs", exist_ok=True)
    os.makedirs("./faiss_index", exist_ok=True)
    
    # 檢查必要的環境變數
    required_env_vars = [
        "LINE_CHANNEL_SECRET",
        "LINE_CHANNEL_ACCESS_TOKEN",
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        "GOOGLE_CALENDAR_ID",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"錯誤: 缺少以下環境變數: {', '.join(missing_vars)}")
        print("請確保這些環境變數已在 Render 平台上設定")
        return False
    
    return True

def init_database():
    """
    初始化資料庫
    """
    try:
        # 初始化用戶管理器
        user_manager = UserManager()
        print("用戶資料庫初始化成功")
        return True
    except Exception as e:
        print(f"初始化資料庫失敗: {e}")
        return False

def test_calendar_connection():
    """
    測試 Google Calendar 連接
    """
    try:
        # 初始化日曆管理器
        calendar_manager = CalendarManager()
        
        # 嘗試獲取日曆事件
        service = calendar_manager._get_calendar_service()
        if not service:
            print("無法連接到 Google Calendar 服務")
            return False
        
        print("Google Calendar 連接測試成功")
        return True
    except Exception as e:
        print(f"Google Calendar 連接測試失敗: {e}")
        return False

def main():
    """
    主函數
    """
    print("開始初始化 LINE Bot 與 Google Calendar 整合系統...")
    
    # 初始化環境
    if not init_environment():
        print("環境初始化失敗")
        sys.exit(1)
    
    # 初始化資料庫
    if not init_database():
        print("資料庫初始化失敗")
        sys.exit(1)
    
    # 測試 Google Calendar 連接
    if not test_calendar_connection():
        print("Google Calendar 連接測試失敗")
        sys.exit(1)
    
    print("初始化完成，系統準備就緒")

if __name__ == "__main__":
    main()
