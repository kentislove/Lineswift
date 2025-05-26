"""
測試模組 - 用於測試 LINE Bot 與 Google Calendar 整合
"""
import os
import unittest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from src.user_manager import UserManager
from src.calendar_manager import CalendarManager

# 測試客戶端
client = TestClient(app)

class TestLineBot(unittest.TestCase):
    """
    LINE Bot 整合測試
    """
    def setUp(self):
        """
        測試前準備
        """
        # 模擬用戶資料
        self.user_manager = UserManager(db_path=":memory:")
        self.user_manager.add_user("user_a", "用戶A", True)  # 管理員
        self.user_manager.add_user("user_b", "用戶B", False)  # 普通用戶
        
        # 模擬日曆管理器
        self.calendar_manager = MagicMock()
        
        # 模擬 LINE Bot API
        self.line_bot_api = MagicMock()
        self.handler = MagicMock()
    
    @patch("src.line_bot.line_bot_api")
    @patch("src.line_bot.handler")
    @patch("src.line_bot.user_manager")
    @patch("src.line_bot.calendar_manager")
    def test_line_callback(self, mock_calendar_manager, mock_user_manager, mock_handler, mock_line_bot_api):
        """
        測試 LINE Webhook 回調
        """
        # 設置模擬對象
        mock_user_manager.is_admin.return_value = True
        mock_user_manager.get_user_name.return_value = "用戶A"
        mock_user_manager.user_exists.return_value = True
        
        mock_calendar_manager.get_shift.return_value = {
            "id": "event123",
            "summary": "測試排班",
            "start": {"dateTime": "2025-05-30T08:00:00+08:00"},
            "end": {"dateTime": "2025-05-30T09:00:00+08:00"},
            "description": "測試描述"
        }
        
        # 模擬 LINE Webhook 請求
        webhook_body = {
            "events": [
                {
                    "type": "message",
                    "message": {
                        "type": "text",
                        "id": "message123",
                        "text": "我希望在20250530早上08:00跟你換班 @用戶B"
                    },
                    "source": {
                        "type": "user",
                        "userId": "user_a"
                    },
                    "replyToken": "reply123"
                }
            ]
        }
        
        # 發送請求
        response = client.post(
            "/line/callback",
            json=webhook_body,
            headers={"X-Line-Signature": "test_signature"}
        )
        
        # 驗證回應
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "OK"})
        
        # 驗證處理函數被調用
        mock_handler.handle.assert_called_once()
    
    @patch("src.line_bot.line_bot_api")
    @patch("src.line_bot.user_manager")
    @patch("src.line_bot.calendar_manager")
    def test_handle_shift_request(self, mock_calendar_manager, mock_user_manager, mock_line_bot_api):
        """
        測試換班請求處理
        """
        from src.line_bot import handle_shift_request
        import re
        
        # 設置模擬對象
        mock_user_manager.is_admin.return_value = True
        mock_user_manager.get_user_name.side_effect = lambda user_id: "用戶A" if user_id == "user_a" else "用戶B"
        mock_user_manager.user_exists.return_value = True
        mock_user_manager.get_user_id_by_name.return_value = "user_b"
        
        mock_calendar_manager.get_shift.return_value = {
            "id": "event123",
            "summary": "測試排班",
            "start": {"dateTime": "2025-05-30T08:00:00+08:00"},
            "end": {"dateTime": "2025-05-30T09:00:00+08:00"},
            "description": "測試描述"
        }
        
        # 模擬消息事件
        event = MagicMock()
        event.source.user_id = "user_a"
        event.message.text = "我希望在20250530早上08:00跟你換班 @用戶B"
        event.reply_token = "reply123"
        
        # 模擬正則匹配
        match = re.search(r"我希望在(\d{8})([早中下晚]午|上|下)(\d{1,2}:\d{2})跟你換班", event.message.text)
        
        # 調用函數
        with patch("src.line_bot.extract_mentioned_users", return_value=["user_b"]):
            handle_shift_request(event, match)
        
        # 驗證 LINE Bot API 被調用
        mock_line_bot_api.reply_message.assert_called_once()
        mock_line_bot_api.push_message.assert_called_once()
    
    @patch("src.line_bot.line_bot_api")
    @patch("src.line_bot.user_manager")
    @patch("src.line_bot.calendar_manager")
    def test_handle_postback(self, mock_calendar_manager, mock_user_manager, mock_line_bot_api):
        """
        測試按鈕回調處理
        """
        from src.line_bot import handle_postback, shift_requests
        
        # 設置模擬對象
        mock_user_manager.get_user_name.side_effect = lambda user_id: "用戶A" if user_id == "user_a" else "用戶B"
        mock_calendar_manager.swap_shifts.return_value = True
        
        # 模擬請求數據
        request_id = "user_a_user_b_20250530_早上_08:00"
        shift_requests[request_id] = {
            "requester_id": "user_a",
            "target_id": "user_b",
            "date": "20250530",
            "time_period": "早上",
            "time": "08:00",
            "requester_shift": {
                "id": "event_a",
                "summary": "用戶A排班",
                "description": "測試描述A"
            },
            "target_shift": {
                "id": "event_b",
                "summary": "用戶B排班",
                "description": "測試描述B"
            }
        }
        
        # 模擬回調事件 - 同意換班
        event_approve = MagicMock()
        event_approve.source.user_id = "user_b"
        event_approve.postback.data = f"action=approve&request_id={request_id}"
        event_approve.reply_token = "reply_approve"
        
        # 調用函數 - 同意換班
        handle_postback(event_approve)
        
        # 驗證日曆更新被調用
        mock_calendar_manager.swap_shifts.assert_called_once_with(
            "user_a", "user_b", "20250530", "早上", "08:00"
        )
        
        # 驗證 LINE Bot API 被調用
        mock_line_bot_api.reply_message.assert_called_once()
        mock_line_bot_api.push_message.assert_called_once()
        
        # 重置模擬對象
        mock_line_bot_api.reset_mock()
        mock_calendar_manager.reset_mock()
        
        # 重新添加請求
        shift_requests[request_id] = {
            "requester_id": "user_a",
            "target_id": "user_b",
            "date": "20250530",
            "time_period": "早上",
            "time": "08:00",
            "requester_shift": {
                "id": "event_a",
                "summary": "用戶A排班",
                "description": "測試描述A"
            },
            "target_shift": {
                "id": "event_b",
                "summary": "用戶B排班",
                "description": "測試描述B"
            }
        }
        
        # 模擬回調事件 - 拒絕換班
        event_reject = MagicMock()
        event_reject.source.user_id = "user_b"
        event_reject.postback.data = f"action=reject&request_id={request_id}"
        event_reject.reply_token = "reply_reject"
        
        # 調用函數 - 拒絕換班
        handle_postback(event_reject)
        
        # 驗證日曆更新未被調用
        mock_calendar_manager.swap_shifts.assert_not_called()
        
        # 驗證 LINE Bot API 被調用
        mock_line_bot_api.reply_message.assert_called_once()
        mock_line_bot_api.push_message.assert_called_once()

class TestCalendarManager(unittest.TestCase):
    """
    日曆管理器測試
    """
    @patch("src.calendar_manager.build")
    def test_get_shift(self, mock_build):
        """
        測試獲取排班
        """
        # 模擬 Google Calendar 服務
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_build.return_value = mock_service
        
        # 模擬事件列表響應
        mock_events_result = {
            "items": [
                {
                    "id": "event123",
                    "summary": "測試排班",
                    "start": {"dateTime": "2025-05-30T08:00:00+08:00"},
                    "end": {"dateTime": "2025-05-30T09:00:00+08:00"},
                    "description": "測試描述"
                }
            ]
        }
        mock_events.list.return_value.execute.return_value = mock_events_result
        
        # 創建日曆管理器
        calendar_manager = CalendarManager()
        
        # 調用函數
        shift = calendar_manager.get_shift("user_a", "20250530", "早上", "08:00")
        
        # 驗證結果
        self.assertIsNotNone(shift)
        self.assertEqual(shift["id"], "event123")
        self.assertEqual(shift["summary"], "測試排班")
    
    @patch("src.calendar_manager.build")
    def test_swap_shifts(self, mock_build):
        """
        測試交換排班
        """
        # 模擬 Google Calendar 服務
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_service.events.return_value = mock_events
        mock_build.return_value = mock_service
        
        # 模擬事件獲取響應
        mock_events.get.side_effect = lambda calendarId, eventId: MagicMock(
            execute=lambda: {
                "id": eventId,
                "summary": f"用戶{eventId[-1]}排班",
                "description": f"測試描述{eventId[-1]}"
            }
        )
        
        # 模擬事件列表響應
        mock_events.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "event_a",
                    "summary": "用戶A排班",
                    "start": {"dateTime": "2025-05-30T08:00:00+08:00"},
                    "end": {"dateTime": "2025-05-30T09:00:00+08:00"},
                    "description": "測試描述A"
                }
            ]
        }
        
        # 創建日曆管理器
        calendar_manager = CalendarManager()
        
        # 模擬 get_shift 方法
        calendar_manager.get_shift = MagicMock(side_effect=lambda user_id, date_str, time_period, time_str: {
            "id": f"event_{user_id[-1]}",
            "summary": f"用戶{user_id[-1].upper()}排班",
            "start": {"dateTime": "2025-05-30T08:00:00+08:00"},
            "end": {"dateTime": "2025-05-30T09:00:00+08:00"},
            "description": f"測試描述{user_id[-1].upper()}"
        })
        
        # 調用函數
        result = calendar_manager.swap_shifts("user_a", "user_b", "20250530", "早上", "08:00")
        
        # 驗證結果
        self.assertTrue(result)
        
        # 驗證事件更新被調用
        self.assertEqual(mock_events.update.call_count, 2)

class TestUserManager(unittest.TestCase):
    """
    用戶管理器測試
    """
    def setUp(self):
        """
        測試前準備
        """
        # 使用內存數據庫進行測試
        self.user_manager = UserManager(db_path=":memory:")
    
    def test_add_user(self):
        """
        測試添加用戶
        """
        # 添加用戶
        result = self.user_manager.add_user("user_a", "用戶A", True)
        
        # 驗證結果
        self.assertTrue(result)
        self.assertTrue(self.user_manager.user_exists("user_a"))
        self.assertTrue(self.user_manager.is_admin("user_a"))
    
    def test_set_admin(self):
        """
        測試設置管理員權限
        """
        # 添加用戶
        self.user_manager.add_user("user_b", "用戶B", False)
        
        # 驗證初始狀態
        self.assertFalse(self.user_manager.is_admin("user_b"))
        
        # 設置為管理員
        result = self.user_manager.set_admin("user_b", True)
        
        # 驗證結果
        self.assertTrue(result)
        self.assertTrue(self.user_manager.is_admin("user_b"))
        
        # 取消管理員權限
        result = self.user_manager.set_admin("user_b", False)
        
        # 驗證結果
        self.assertTrue(result)
        self.assertFalse(self.user_manager.is_admin("user_b"))
    
    def test_get_user_name(self):
        """
        測試獲取用戶名稱
        """
        # 添加用戶
        self.user_manager.add_user("user_c", "用戶C", False)
        
        # 獲取用戶名稱
        name = self.user_manager.get_user_name("user_c")
        
        # 驗證結果
        self.assertEqual(name, "用戶C")
    
    def test_get_user_id_by_name(self):
        """
        測試通過名稱獲取用戶 ID
        """
        # 添加用戶
        self.user_manager.add_user("user_d", "用戶D", False)
        
        # 通過名稱獲取用戶 ID
        user_id = self.user_manager.get_user_id_by_name("用戶D")
        
        # 驗證結果
        self.assertEqual(user_id, "user_d")

if __name__ == "__main__":
    unittest.main()
