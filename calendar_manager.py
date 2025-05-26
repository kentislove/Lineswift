"""
日曆管理模組 - 處理 Google Calendar 整合
"""
import os
import datetime
from typing import Dict, List, Optional, Any, Tuple
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Calendar API 設定
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "./service-account.json")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

class CalendarManager:
    """
    日曆管理類 - 處理 Google Calendar 整合
    """
    def __init__(self, calendar_id: str = CALENDAR_ID):
        self.calendar_id = calendar_id
        self.service = self._get_calendar_service()
    
    def _get_calendar_service(self):
        """
        獲取 Google Calendar 服務
        """
        try:
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
            service = build('calendar', 'v3', credentials=credentials)
            return service
        except Exception as e:
            print(f"獲取 Google Calendar 服務失敗: {e}")
            return None
    
    def get_shift(self, user_id: str, date_str: str, time_period: str, time_str: str) -> Optional[Dict[str, Any]]:
        """
        獲取用戶在指定日期和時間的排班資訊
        
        Args:
            user_id: 用戶 ID
            date_str: 日期字符串 (YYYYMMDD)
            time_period: 時段 (早上/下午/晚上)
            time_str: 時間字符串 (HH:MM)
            
        Returns:
            排班資訊字典或 None
        """
        if not self.service:
            print("Google Calendar 服務未初始化")
            return None
        
        try:
            # 解析日期和時間
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:])
            
            # 解析時間
            hour, minute = map(int, time_str.split(':'))
            
            # 根據時段調整時間
            if time_period in ["早上", "上"]:
                # 早上時段不調整
                pass
            elif time_period in ["下午", "下"]:
                # 下午時段，如果小時 < 12，加 12
                if hour < 12:
                    hour += 12
            elif time_period in ["晚上", "晚"]:
                # 晚上時段，如果小時 < 12，加 12
                if hour < 12:
                    hour += 12
            
            # 創建日期時間對象
            start_time = datetime.datetime(year, month, day, hour, minute, 0)
            end_time = start_time + datetime.timedelta(hours=1)  # 假設排班時長為 1 小時
            
            # 轉換為 ISO 格式
            time_min = start_time.isoformat() + 'Z'
            time_max = end_time.isoformat() + 'Z'
            
            # 查詢日曆事件
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                q=user_id,  # 使用用戶 ID 作為查詢條件
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return None
            
            # 返回第一個匹配的事件
            return {
                'id': events[0]['id'],
                'summary': events[0]['summary'],
                'start': events[0]['start'],
                'end': events[0]['end'],
                'description': events[0].get('description', '')
            }
            
        except Exception as e:
            print(f"獲取排班資訊失敗: {e}")
            return None
    
    def swap_shifts(self, user_a_id: str, user_b_id: str, date_str: str, time_period: str, time_str: str) -> bool:
        """
        交換兩位用戶的排班
        
        Args:
            user_a_id: 用戶 A 的 ID
            user_b_id: 用戶 B 的 ID
            date_str: 日期字符串 (YYYYMMDD)
            time_period: 時段 (早上/下午/晚上)
            time_str: 時間字符串 (HH:MM)
            
        Returns:
            是否成功交換排班
        """
        if not self.service:
            print("Google Calendar 服務未初始化")
            return False
        
        try:
            # 獲取兩位用戶的排班
            user_a_shift = self.get_shift(user_a_id, date_str, time_period, time_str)
            user_b_shift = self.get_shift(user_b_id, date_str, time_period, time_str)
            
            if not user_a_shift or not user_b_shift:
                print("無法獲取完整的排班資訊")
                return False
            
            # 交換排班資訊
            # 更新用戶 A 的排班
            user_a_event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=user_a_shift['id']
            ).execute()
            
            # 更新用戶 B 的排班
            user_b_event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=user_b_shift['id']
            ).execute()
            
            # 交換摘要和描述
            temp_summary = user_a_event['summary']
            temp_description = user_a_event.get('description', '')
            
            user_a_event['summary'] = user_b_event['summary']
            user_a_event['description'] = user_b_event.get('description', '')
            
            user_b_event['summary'] = temp_summary
            user_b_event['description'] = temp_description
            
            # 添加換班記錄
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            swap_record = f"\n[換班記錄] {now}: 與 {user_b_id} 交換"
            user_a_event['description'] += swap_record
            
            swap_record = f"\n[換班記錄] {now}: 與 {user_a_id} 交換"
            user_b_event['description'] += swap_record
            
            # 更新事件
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=user_a_shift['id'],
                body=user_a_event
            ).execute()
            
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=user_b_shift['id'],
                body=user_b_event
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"交換排班失敗: {e}")
            return False
    
    def create_shift(self, user_id: str, date_str: str, time_period: str, time_str: str, summary: str, description: str = "") -> Optional[str]:
        """
        創建新的排班
        
        Args:
            user_id: 用戶 ID
            date_str: 日期字符串 (YYYYMMDD)
            time_period: 時段 (早上/下午/晚上)
            time_str: 時間字符串 (HH:MM)
            summary: 排班摘要
            description: 排班描述
            
        Returns:
            事件 ID 或 None
        """
        if not self.service:
            print("Google Calendar 服務未初始化")
            return None
        
        try:
            # 解析日期和時間
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:])
            
            # 解析時間
            hour, minute = map(int, time_str.split(':'))
            
            # 根據時段調整時間
            if time_period in ["早上", "上"]:
                # 早上時段不調整
                pass
            elif time_period in ["下午", "下"]:
                # 下午時段，如果小時 < 12，加 12
                if hour < 12:
                    hour += 12
            elif time_period in ["晚上", "晚"]:
                # 晚上時段，如果小時 < 12，加 12
                if hour < 12:
                    hour += 12
            
            # 創建日期時間對象
            start_time = datetime.datetime(year, month, day, hour, minute, 0)
            end_time = start_time + datetime.timedelta(hours=1)  # 假設排班時長為 1 小時
            
            # 創建事件
            event = {
                'summary': summary,
                'description': f"用戶 ID: {user_id}\n{description}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Taipei',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Taipei',
                },
            }
            
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return event['id']
            
        except Exception as e:
            print(f"創建排班失敗: {e}")
            return None
    
    def delete_shift(self, event_id: str) -> bool:
        """
        刪除排班
        
        Args:
            event_id: 事件 ID
            
        Returns:
            是否成功刪除
        """
        if not self.service:
            print("Google Calendar 服務未初始化")
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"刪除排班失敗: {e}")
            return False
