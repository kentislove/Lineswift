"""
執行測試腳本 - 用於執行單元與整合測試
"""
import unittest
import sys
import os

def run_tests():
    """
    執行所有測試
    """
    # 設置測試環境變數
    os.environ["LINE_CHANNEL_SECRET"] = "test_secret"
    os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = "test_token"
    os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"] = "test_service_account.json"
    os.environ["GOOGLE_CALENDAR_ID"] = "test_calendar_id"
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    
    # 執行測試
    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern="tests.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回測試結果
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
