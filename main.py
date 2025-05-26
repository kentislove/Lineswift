import os
import re
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, SeparatorComponent,
    URIAction
)
import google.oauth2.service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ====== 環境變數設定 ======
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "")

# 確認環境變數已設置
if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("請設置 LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN 環境變數")

if not GOOGLE_CALENDAR_ID:
    print("警告: 未設置 GOOGLE_CALENDAR_ID 環境變數，Google Calendar 功能將無法正常運作")

# ====== LINE Bot 設定 ======
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ====== 換班請求正則表達式 ======
# 匹配格式: "我希望在YYYYMMDD HH:MM (24小時制)跟你換班 @用戶名"
SHIFT_REQUEST_PATTERN = r"我希望在(\d{8})\s+(\d{2}):(\d{2})跟你換班\s*@(.+)"

# ====== 用戶管理 ======
# 初始化用戶映射表 - 預設已知用戶的名稱與 LINE ID 對應關係
# 格式: {"用戶名稱": "LINE_USER_ID"}
# 注意: 請將以下示例替換為您實際的用戶名稱和 LINE ID
INITIAL_USER_MAPPING = {
    "張書豪-Ragic Customize!": "kent1027",  # 請替換為實際 LINE ID
    "KentChang-廠內維修中": "newkent27",  # 請替換為實際 LINE ID
    # 可以添加更多用戶
}

# 用於存儲用戶名稱與 LINE ID 的對應關係
user_mapping = INITIAL_USER_MAPPING.copy()

# 用於存儲換班請求
shift_requests = {}

# ====== Google Calendar API 設定 ======
def get_calendar_service():
    """獲取 Google Calendar 服務"""
    try:
        # 從環境變數中獲取服務帳號憑證
        service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}"))
        if not service_account_info:
            print("警告: 未設置 GOOGLE_SERVICE_ACCOUNT_JSON 環境變數")
            return None
            
        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"獲取 Google Calendar 服務時發生錯誤: {str(e)}")
        return None

def get_calendar_events(date_str):
    """獲取指定日期的日曆事件"""
    service = get_calendar_service()
    if not service:
        return None
        
    try:
        # 將日期字符串轉換為 datetime 對象
        date = datetime.strptime(date_str, "%Y%m%d")
        
        # 設置時間範圍為整天
        time_min = date.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        time_max = date.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
        
        # 獲取事件
        events_result = service.events().list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    except Exception as e:
        print(f"獲取日曆事件時發生錯誤: {str(e)}")
        return None

def create_or_update_event(date_str, time_str, user_name, description=None):
    """創建或更新日曆事件"""
    service = get_calendar_service()
    if not service:
        return False
        
    try:
        # 將日期和時間字符串轉換為 datetime 對象
        date_time = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
        
        # 設置事件開始和結束時間 (假設每個班次為 1 小時)
        start_time = date_time.isoformat()
        end_time = date_time.replace(hour=date_time.hour + 1).isoformat()
        
        # 設置事件標題和描述
        summary = f"班表: {user_name}"
        if not description:
            description = f"排班人員: {user_name}"
        
        # 創建事件
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Taipei',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Taipei',
            },
        }
        
        # 檢查是否已有相同時間的事件
        events = get_calendar_events(date_str)
        existing_event = None
        
        if events:
            for e in events:
                start = e.get('start', {}).get('dateTime', '')
                if start and datetime.fromisoformat(start.replace('Z', '+00:00')) == date_time:
                    existing_event = e
                    break
        
        # 更新或創建事件
        if existing_event:
            # 更新現有事件的描述，添加換班歷史
            old_description = existing_event.get('description', '')
            new_description = f"{old_description}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 更新為 {user_name}"
            event['description'] = new_description
            
            service.events().update(
                calendarId=GOOGLE_CALENDAR_ID,
                eventId=existing_event['id'],
                body=event
            ).execute()
        else:
            service.events().insert(
                calendarId=GOOGLE_CALENDAR_ID,
                body=event
            ).execute()
        
        return True
    except Exception as e:
        print(f"創建或更新日曆事件時發生錯誤: {str(e)}")
        return False

def swap_shifts(date_str, time_str, user_a, user_b):
    """交換兩個用戶的班次"""
    service = get_calendar_service()
    if not service:
        return False
        
    try:
        # 獲取指定日期的所有事件
        events = get_calendar_events(date_str)
        if not events:
            # 如果沒有事件，則為兩個用戶創建新事件
            create_or_update_event(date_str, time_str, user_b, 
                                  f"排班人員: {user_b}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {user_a} 換班")
            return True
            
        # 將日期和時間字符串轉換為 datetime 對象
        target_time = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
        
        # 查找目標時間的事件
        target_event = None
        for event in events:
            start = event.get('start', {}).get('dateTime', '')
            if start:
                event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                if event_time.hour == target_time.hour and event_time.minute == target_time.minute:
                    target_event = event
                    break
        
        # 更新事件
        if target_event:
            # 獲取原始排班人員
            original_user = target_event.get('summary', '').replace('班表: ', '')
            
            # 更新事件
            target_event['summary'] = f"班表: {user_b}"
            
            # 添加換班歷史
            old_description = target_event.get('description', '')
            new_description = f"{old_description}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {original_user} 換班給 {user_b}"
            target_event['description'] = new_description
            
            service.events().update(
                calendarId=GOOGLE_CALENDAR_ID,
                eventId=target_event['id'],
                body=target_event
            ).execute()
        else:
            # 如果沒有找到事件，則創建新事件
            create_or_update_event(date_str, time_str, user_b, 
                                  f"排班人員: {user_b}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {user_a} 換班")
        
        return True
    except Exception as e:
        print(f"交換班次時發生錯誤: {str(e)}")
        return False

# ====== FastAPI 設定 ======
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "running", "message": "LINE Bot 換班系統已啟動"}

@app.post("/webhook")
async def webhook(request: Request):
    # 獲取 X-Line-Signature 標頭值
    signature = request.headers.get("X-Line-Signature", "")
    
    # 獲取請求體作為文本
    body = await request.body()
    body_text = body.decode("utf-8")
    
    try:
        # 驗證簽名
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # 即使處理過程中出錯，也返回 200 OK 給 LINE 平台
    return JSONResponse(content={"status": "ok"})

# ====== LINE 訊息處理 ======
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        user_id = event.source.user_id
        text = event.message.text
        
        # 嘗試獲取用戶資料
        try:
            user_profile = line_bot_api.get_profile(user_id)
            user_name = user_profile.display_name
            # 更新用戶映射
            user_mapping[user_name] = user_id
            print(f"用戶映射更新: {user_name} -> {user_id}")
        except LineBotApiError:
            user_name = "未知用戶"
        
        # 檢查是否為換班請求
        match = re.match(SHIFT_REQUEST_PATTERN, text)
        if match:
            date_str, hour, minute, target_user = match.groups()
            
            # 驗證日期格式
            try:
                date = datetime.strptime(date_str, "%Y%m%d")
                formatted_date = date.strftime("%Y/%m/%d")
            except ValueError:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="日期格式錯誤，請使用YYYYMMDD格式，例如：20250530")
                )
                return
            
            # 驗證時間格式
            try:
                hour_int = int(hour)
                minute_int = int(minute)
                if hour_int < 0 or hour_int > 23 or minute_int < 0 or minute_int > 59:
                    raise ValueError("時間格式錯誤")
                formatted_time = f"{hour}:{minute}"
            except ValueError:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="時間格式錯誤，請使用24小時制，例如：08:00 或 18:30")
                )
                return
            
            # 檢查目標用戶是否存在
            target_user_id = user_mapping.get(target_user)
            if not target_user_id:
                # 列出所有已知用戶，幫助用戶選擇正確的用戶名稱
                known_users = list(user_mapping.keys())
                user_list = "\n".join([f"- {name}" for name in known_users])
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"找不到用戶 '{target_user}'，請確認用戶名稱正確。\n\n已知用戶列表:\n{user_list}")
                )
                return
            
            # 儲存換班請求
            request_id = f"{user_id}_{date_str}_{hour}_{minute}"
            shift_requests[request_id] = {
                "requester_id": user_id,
                "requester_name": user_name,
                "target_id": target_user_id,
                "target_name": target_user,
                "date": date_str,
                "time": f"{hour}:{minute}",
                "status": "pending"
            }
            
            # 回覆請求者
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"已發送換班請求給 {target_user}，等待回應...")
            )
            
            # 發送確認訊息給目標用戶
            confirm_message = f"換班請求\n{user_name} 希望在 {formatted_date} {formatted_time} 與您換班"
            
            line_bot_api.push_message(
                target_user_id,
                TemplateSendMessage(
                    alt_text="換班請求確認",
                    template=ConfirmTemplate(
                        text=confirm_message,
                        actions=[
                            MessageAction(label="批准", text=f"批准換班:{request_id}"),
                            MessageAction(label="拒絕", text=f"拒絕換班:{request_id}")
                        ]
                    )
                )
            )
            
        elif text.startswith("批准換班:") or text.startswith("拒絕換班:"):
            # 處理換班回應
            parts = text.split(":", 1)
            if len(parts) != 2:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="無效的回應格式")
                )
                return
                
            action, request_id = parts
            request = shift_requests.get(request_id)
            
            if not request:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="找不到對應的換班請求，可能已過期或已處理")
                )
                return
                
            if request["target_id"] != user_id:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="您無權回應此換班請求")
                )
                return
                
            if action == "批准換班":
                # 更新請求狀態
                request["status"] = "approved"
                
                # 更新 Google Calendar
                success = swap_shifts(
                    request["date"], 
                    request["time"], 
                    request["requester_name"], 
                    request["target_name"]
                )
                
                # 回覆目標用戶
                if success:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="您已批准換班請求，Google Calendar 已更新")
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="您已批准換班請求，但 Google Calendar 更新失敗，請聯繫管理員")
                    )
                
                # 通知請求者
                line_bot_api.push_message(
                    request["requester_id"],
                    TextSendMessage(text=f"{request['target_name']} 已批准您在 {request['date']} {request['time']} 的換班請求")
                )
            else:  # 拒絕換班
                # 更新請求狀態
                request["status"] = "rejected"
                
                # 回覆目標用戶
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="您已拒絕換班請求")
                )
                
                # 通知請求者
                line_bot_api.push_message(
                    request["requester_id"],
                    TextSendMessage(text=f"{request['target_name']} 已拒絕您在 {request['date']} {request['time']} 的換班請求")
                )
        elif text == "查看用戶映射":
            # 管理員功能：查看當前用戶映射
            mapping_text = "\n".join([f"{name}: {id}" for name, id in user_mapping.items()])
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"當前用戶映射:\n{mapping_text}")
            )
        else:
            # 提示正確的換班請求格式
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請使用正確的換班請求格式：\n我希望在YYYYMMDD HH:MM (24小時制)跟你換班 @用戶名\n\n例如：\n我希望在20071231 08:00跟你換班 @劉德華")
            )
    except Exception as e:
        print(f"處理訊息時發生錯誤: {str(e)}")
        # 發送錯誤訊息給用戶
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"處理您的請求時發生錯誤，請稍後再試。錯誤詳情: {str(e)}")
            )
        except Exception:
            pass  # 忽略回覆錯誤

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
