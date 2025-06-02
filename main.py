import os
import re
import json
import hashlib
import time
from datetime import datetime, timedelta
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

# 匹配格式: "新增排班 YYYYMMDD HH:MM @用戶名"
ADD_SHIFT_PATTERN = r"新增排班\s+(\d{8})\s+(\d{2}):(\d{2})\s*@(.+)"

# 匹配格式: "批次排班 @用戶名"
BATCH_SHIFT_PATTERN = r"批次排班\s*@(.+)"

# ====== 用戶管理 ======
# 初始化用戶映射表 - 預設已知用戶的名稱與 LINE ID 對應關係
# 格式: {"用戶名稱": "LINE_USER_ID"}
# 注意: 請將以下示例替換為您實際的用戶名稱和 LINE ID
INITIAL_USER_MAPPING = {
    "張書豪-Ragic Customize!": "Uf15abf85bca4ee133d1027593de4d1ad",
    "KentChang-廠內維修中": "Ub2eb02fea865d917854d6ecaace84c70",
    # 可以添加更多用戶
}

# 用於存儲用戶名稱與 LINE ID 的對應關係
user_mapping = INITIAL_USER_MAPPING.copy()

# 用於存儲換班請求
shift_requests = {}

# ====== 去重機制 ======
# 存儲已處理的 webhook 請求
processed_webhook_requests = {}
# 存儲已發送的訊息，格式: {message_hash: timestamp}
sent_messages = {}
# 存儲已處理的日曆操作，格式: {operation_hash: timestamp}
processed_calendar_operations = {}
# 訊息和操作的過期時間（秒）
MESSAGE_EXPIRY = 3600  # 1小時
OPERATION_EXPIRY = 86400  # 24小時

def generate_hash(data):
    """生成數據的雜湊值"""
    if isinstance(data, dict):
        # 將字典轉換為排序後的字符串，確保相同內容的字典生成相同的雜湊值
        data = json.dumps(data, sort_keys=True)
    return hashlib.md5(str(data).encode()).hexdigest()

def is_duplicate_webhook(request_id, body_text):
    """檢查 webhook 請求是否重複"""
    # 生成請求的唯一標識
    request_hash = generate_hash(f"{request_id}_{body_text}")
    
    # 檢查是否已處理過此請求
    if request_hash in processed_webhook_requests:
        # 檢查請求是否在短時間內重複
        last_time = processed_webhook_requests[request_hash]
        if time.time() - last_time < 10:  # 10秒內的重複請求視為重複
            print(f"檢測到重複的 webhook 請求: {request_id}")
            return True
    
    # 記錄此請求
    processed_webhook_requests[request_hash] = time.time()
    
    # 清理過期的請求記錄
    clean_expired_records(processed_webhook_requests, 300)  # 5分鐘後過期
    
    return False

def is_duplicate_message(user_id, message_text):
    """檢查訊息是否重複發送"""
    # 生成訊息的唯一標識
    message_hash = generate_hash(f"{user_id}_{message_text}")
    
    # 檢查是否已發送過此訊息
    if message_hash in sent_messages:
        # 檢查訊息是否在短時間內重複
        last_time = sent_messages[message_hash]
        if time.time() - last_time < MESSAGE_EXPIRY:
            print(f"檢測到重複的訊息: {message_text[:30]}...")
            return True
    
    # 記錄此訊息
    sent_messages[message_hash] = time.time()
    
    # 清理過期的訊息記錄
    clean_expired_records(sent_messages, MESSAGE_EXPIRY)
    
    return False

def is_duplicate_calendar_operation(operation_type, date_str, time_str, user_a, user_b=""):
    """檢查日曆操作是否重複"""
    # 生成操作的唯一標識
    operation_data = {
        "type": operation_type,
        "date": date_str,
        "time": time_str,
        "user_a": user_a,
        "user_b": user_b
    }
    operation_hash = generate_hash(operation_data)
    
    # 檢查是否已執行過此操作
    if operation_hash in processed_calendar_operations:
        # 檢查操作是否在有效期內重複
        last_time = processed_calendar_operations[operation_hash]
        if time.time() - last_time < OPERATION_EXPIRY:
            print(f"檢測到重複的日曆操作: {operation_type} {date_str} {time_str}")
            return True
    
    # 記錄此操作
    processed_calendar_operations[operation_hash] = time.time()
    
    # 清理過期的操作記錄
    clean_expired_records(processed_calendar_operations, OPERATION_EXPIRY)
    
    return False

def clean_expired_records(records_dict, expiry_seconds):
    """清理過期的記錄"""
    current_time = time.time()
    expired_keys = [k for k, v in records_dict.items() if current_time - v > expiry_seconds]
    for key in expired_keys:
        del records_dict[key]

def safe_send_message(method, *args, **kwargs):
    """安全發送訊息，避免重複發送"""
    # 提取用戶 ID 和訊息內容
    user_id = None
    message_text = None
    
    if method == line_bot_api.reply_message:
        # reply_message(reply_token, messages)
        message_obj = args[1]
        if isinstance(message_obj, list):
            message_obj = message_obj[0]
        if hasattr(message_obj, 'text'):
            message_text = message_obj.text
        # 對於 reply_message，我們使用 reply_token 作為用戶標識
        user_id = args[0]
    elif method == line_bot_api.push_message:
        # push_message(to, messages)
        user_id = args[0]
        message_obj = args[1]
        if isinstance(message_obj, list):
            message_obj = message_obj[0]
        if hasattr(message_obj, 'text'):
            message_text = message_obj.text
    
    # 如果無法提取訊息內容，直接發送
    if not user_id or not message_text:
        return method(*args, **kwargs)
    
    # 檢查是否重複發送
    if is_duplicate_message(user_id, message_text):
        print(f"跳過重複訊息: {message_text[:30]}...")
        return None
    
    # 發送訊息
    try:
        return method(*args, **kwargs)
    except Exception as e:
        print(f"發送訊息時發生錯誤: {str(e)}")
        # 如果發送失敗，從記錄中移除此訊息
        message_hash = generate_hash(f"{user_id}_{message_text}")
        if message_hash in sent_messages:
            del sent_messages[message_hash]
        raise

# ====== Google Calendar API 設定 ======
def get_calendar_service():
    """獲取 Google Calendar 服務"""
    try:
        # 嘗試從環境變數中獲取服務帳號憑證
        service_account_info = None
        
        # 首先嘗試從 GOOGLE_SERVICE_ACCOUNT_FILE 讀取檔案
        service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        if service_account_file and os.path.exists(service_account_file):
            try:
                print(f"嘗試從檔案讀取服務帳號憑證: {service_account_file}")
                with open(service_account_file, 'r') as f:
                    service_account_info = json.load(f)
                print("成功從檔案讀取服務帳號憑證")
            except Exception as e:
                print(f"從檔案讀取服務帳號憑證時發生錯誤: {str(e)}")
        
        # 如果檔案讀取失敗，嘗試從 GOOGLE_SERVICE_ACCOUNT_JSON 讀取 JSON 字串
        if not service_account_info:
            service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
            try:
                print("嘗試從環境變數 GOOGLE_SERVICE_ACCOUNT_JSON 讀取服務帳號憑證")
                service_account_info = json.loads(service_account_json)
                if not service_account_info:
                    print("警告: GOOGLE_SERVICE_ACCOUNT_JSON 環境變數為空或格式不正確")
            except Exception as e:
                print(f"解析 GOOGLE_SERVICE_ACCOUNT_JSON 時發生錯誤: {str(e)}")
        
        if not service_account_info:
            print("錯誤: 無法獲取服務帳號憑證，請檢查 GOOGLE_SERVICE_ACCOUNT_FILE 或 GOOGLE_SERVICE_ACCOUNT_JSON 環境變數")
            return None
            
        # 使用服務帳號憑證創建 credentials
        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        # 創建 Google Calendar 服務
        service = build('calendar', 'v3', credentials=credentials)
        print(f"成功創建 Google Calendar 服務，使用日曆 ID: {GOOGLE_CALENDAR_ID}")
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
        
        print(f"查詢日曆事件: 日期={date_str}, 日曆ID={GOOGLE_CALENDAR_ID}")
        
        # 獲取事件
        events_result = service.events().list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"找到 {len(events)} 個事件")
        return events
    except Exception as e:
        print(f"獲取日曆事件時發生錯誤: {str(e)}")
        return None

def get_week_calendar_events():
    """獲取一週內的日曆事件"""
    service = get_calendar_service()
    if not service:
        return None
        
    try:
        # 設置時間範圍為今天到一週後
        now = datetime.utcnow()
        time_min = now.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        time_max = (now + timedelta(days=7)).replace(hour=23, minute=59, second=59).isoformat() + 'Z'
        
        print(f"查詢一週內日曆事件: 從={time_min}, 到={time_max}")
        
        # 獲取事件
        events_result = service.events().list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"找到 {len(events)} 個事件")
        return events
    except Exception as e:
        print(f"獲取一週內日曆事件時發生錯誤: {str(e)}")
        return None

def create_or_update_event(date_str, time_str, user_name, description=None):
    """創建或更新日曆事件"""
    # 檢查是否重複操作
    if is_duplicate_calendar_operation("create_or_update", date_str, time_str, user_name):
        print(f"跳過重複的日曆創建/更新操作: {date_str} {time_str} {user_name}")
        return True
        
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
        
        print(f"準備創建或更新事件: 日期={date_str}, 時間={time_str}, 用戶={user_name}")
        
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
            print(f"找到現有事件，ID: {existing_event['id']}")
            # 更新現有事件的描述，添加換班歷史
            old_description = existing_event.get('description', '')
            # 檢查是否已經有相同的換班歷史記錄
            history_entry = f"換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 更新為 {user_name}"
            if history_entry not in old_description:
                new_description = f"{old_description}\n{history_entry}"
                event['description'] = new_description
                
                service.events().update(
                    calendarId=GOOGLE_CALENDAR_ID,
                    eventId=existing_event['id'],
                    body=event
                ).execute()
                print("事件更新成功")
            else:
                print("跳過重複的換班歷史記錄")
        else:
            print("未找到現有事件，創建新事件")
            service.events().insert(
                calendarId=GOOGLE_CALENDAR_ID,
                body=event
            ).execute()
            print("新事件創建成功")
        
        return True
    except Exception as e:
        print(f"創建或更新日曆事件時發生錯誤: {str(e)}")
        return False

def swap_shifts(date_str, time_str, user_a, user_b):
    """交換兩個用戶的班次"""
    # 檢查是否重複操作
    if is_duplicate_calendar_operation("swap", date_str, time_str, user_a, user_b):
        print(f"跳過重複的班次交換操作: {date_str} {time_str} {user_a} -> {user_b}")
        return True
        
    service = get_calendar_service()
    if not service:
        return False
        
    try:
        print(f"準備交換班次: 日期={date_str}, 時間={time_str}, 從用戶={user_a} 到用戶={user_b}")
        
        # 獲取指定日期的所有事件
        events = get_calendar_events(date_str)
        if not events:
            print("未找到事件，創建新事件")
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
            print(f"找到目標事件，ID: {target_event['id']}")
            # 獲取原始排班人員
            original_user = target_event.get('summary', '').replace('班表: ', '')
            
            # 更新事件
            target_event['summary'] = f"班表: {user_b}"
            
            # 添加換班歷史
            old_description = target_event.get('description', '')
            # 檢查是否已經有相同的換班歷史記錄
            history_entry = f"換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {original_user} 換班給 {user_b}"
            if history_entry not in old_description:
                new_description = f"{old_description}\n{history_entry}"
                target_event['description'] = new_description
                
                service.events().update(
                    calendarId=GOOGLE_CALENDAR_ID,
                    eventId=target_event['id'],
                    body=target_event
                ).execute()
                print("班次交換成功")
            else:
                print("跳過重複的換班歷史記錄")
        else:
            print("未找到目標事件，創建新事件")
            # 如果沒有找到事件，則創建新事件
            create_or_update_event(date_str, time_str, user_b, 
                                  f"排班人員: {user_b}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {user_a} 換班")
        
        return True
    except Exception as e:
        print(f"交換班次時發生錯誤: {str(e)}")
        return False

def create_batch_shifts(user_name):
    """為未來一週（排除週六日）創建批次排班"""
    service = get_calendar_service()
    if not service:
        return False, "無法連接 Google Calendar 服務"
    
    try:
        # 獲取今天的日期
        today = datetime.now()
        
        # 創建未來一週的排班
        success_count = 0
        skipped_count = 0
        failed_count = 0
        result_messages = []
        
        for i in range(1, 8):  # 從明天開始，共7天
            current_date = today + timedelta(days=i)
            
            # 跳過週六和週日
            if current_date.weekday() >= 5:  # 5=週六, 6=週日
                continue
            
            # 格式化日期和時間
            date_str = current_date.strftime("%Y%m%d")
            time_str = "09:00"  # 默認早上9點
            
            # 檢查是否已有排班
            events = get_calendar_events(date_str)
            has_event_at_time = False
            
            if events:
                for event in events:
                    start = event.get('start', {}).get('dateTime', '')
                    if start:
                        event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        if event_time.hour == 9 and event_time.minute == 0:
                            has_event_at_time = True
                            skipped_count += 1
                            result_messages.append(f"{current_date.strftime('%Y/%m/%d')} 已有排班，跳過")
                            break
            
            # 如果沒有排班，則創建新排班
            if not has_event_at_time:
                success = create_or_update_event(date_str, time_str, user_name, 
                                               f"排班人員: {user_name}\n批次排班: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                if success:
                    success_count += 1
                    result_messages.append(f"{current_date.strftime('%Y/%m/%d')} 排班成功")
                else:
                    failed_count += 1
                    result_messages.append(f"{current_date.strftime('%Y/%m/%d')} 排班失敗")
        
        # 生成結果訊息
        summary = f"批次排班結果：\n成功: {success_count}\n已有排班: {skipped_count}\n失敗: {failed_count}"
        details = "\n".join(result_messages)
        
        return True, f"{summary}\n\n詳細結果:\n{details}"
    except Exception as e:
        print(f"批次創建排班時發生錯誤: {str(e)}")
        return False, f"批次排班時發生錯誤: {str(e)}"

def is_admin(user_id):
    """檢查用戶是否為管理員"""
    # 這裡可以實現更複雜的管理員檢查邏輯
    # 目前簡單地檢查用戶是否在用戶映射表中
    for name, id in user_mapping.items():
        if id == user_id:
            return True
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
    request_id = request.headers.get("x-line-request-id", "")
    
    # 獲取請求體作為文本
    body = await request.body()
    body_text = body.decode("utf-8")
    
    # 檢查是否為重複請求
    if is_duplicate_webhook(request_id, body_text):
        print(f"跳過重複的 webhook 請求: {request_id}")
        return JSONResponse(content={"status": "skipped", "message": "Duplicate request"})
    
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
        reply_token = event.reply_token
        
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
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
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
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text="時間格式錯誤，請使用24小時制，例如：08:00 或 18:30")
                )
                return
            
            # 檢查目標用戶是否存在
            target_user_id = user_mapping.get(target_user)
            if not target_user_id:
                # 列出所有已知用戶，幫助用戶選擇正確的用戶名稱
                known_users = list(user_mapping.keys())
                user_list = "\n".join([f"- {name}" for name in known_users])
                
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text=f"找不到用戶 '{target_user}'，請確認用戶名稱正確。\n\n已知用戶列表:\n{user_list}")
                )
                return
            
            # 生成請求 ID
            request_id = f"{user_id}_{date_str}_{hour}_{minute}_{target_user}"
            
            # 檢查是否為重複請求
            if request_id in shift_requests and shift_requests[request_id]["status"] == "pending":
                # 如果是短時間內的重複請求，直接回覆
                last_request_time = shift_requests[request_id].get("timestamp", 0)
                if time.time() - last_request_time < 300:  # 5分鐘內的重複請求
                    safe_send_message(
                        line_bot_api.reply_message,
                        reply_token,
                        TextSendMessage(text=f"您已經發送過相同的換班請求給 {target_user}，請等待回應")
                    )
                    return
            
            # 儲存換班請求
            shift_requests[request_id] = {
                "requester_id": user_id,
                "requester_name": user_name,
                "target_id": target_user_id,
                "target_name": target_user,
                "date": date_str,
                "time": f"{hour}:{minute}",
                "status": "pending",
                "timestamp": time.time()
            }
            
            # 回覆請求者
            safe_send_message(
                line_bot_api.reply_message,
                reply_token,
                TextSendMessage(text=f"已發送換班請求給 {target_user}，等待回應...")
            )
            
            # 發送確認訊息給目標用戶
            confirm_message = f"換班請求\n{user_name} 希望在 {formatted_date} {formatted_time} 與您換班"
            
            safe_send_message(
                line_bot_api.push_message,
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
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text="無效的回應格式")
                )
                return
                
            action, request_id = parts
            request = shift_requests.get(request_id)
            
            if not request:
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text="找不到對應的換班請求，可能已過期或已處理")
                )
                return
                
            if request["target_id"] != user_id:
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text="您無權回應此換班請求")
                )
                return
                
            # 檢查請求狀態，避免重複處理
            if request["status"] != "pending":
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text=f"此換班請求已經被{request['status']}，無法重複處理")
                )
                return
                
            if action == "批准換班":
                # 更新請求狀態
                request["status"] = "approved"
                request["response_time"] = time.time()
                
                # 更新 Google Calendar
                success = swap_shifts(
                    request["date"], 
                    request["time"], 
                    request["requester_name"], 
                    request["target_name"]
                )
                
                # 回覆目標用戶
                if success:
                    safe_send_message(
                        line_bot_api.reply_message,
                        reply_token,
                        TextSendMessage(text="您已批准換班請求，Google Calendar 已更新")
                    )
                else:
                    safe_send_message(
                        line_bot_api.reply_message,
                        reply_token,
                        TextSendMessage(text="您已批准換班請求，但 Google Calendar 更新失敗，請聯繫管理員")
                    )
                
                # 通知請求者
                safe_send_message(
                    line_bot_api.push_message,
                    request["requester_id"],
                    TextSendMessage(text=f"{request['target_name']} 已批准您在 {request['date']} {request['time']} 的換班請求")
                )
            else:  # 拒絕換班
                # 更新請求狀態
                request["status"] = "rejected"
                request["response_time"] = time.time()
                
                # 回覆目標用戶
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text="您已拒絕換班請求")
                )
                
                # 通知請求者
                safe_send_message(
                    line_bot_api.push_message,
                    request["requester_id"],
                    TextSendMessage(text=f"{request['target_name']} 已拒絕您在 {request['date']} {request['time']} 的換班請求")
                )
        
        # 新功能：新增排班
        elif match := re.match(ADD_SHIFT_PATTERN, text):
            # 檢查是否為管理員
            if not is_admin(user_id):
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text="抱歉，只有管理員可以使用此功能")
                )
                return
                
            date_str, hour, minute, target_user = match.groups()
            
            # 驗證日期格式
            try:
                date = datetime.strptime(date_str, "%Y%m%d")
                formatted_date = date.strftime("%Y/%m/%d")
            except ValueError:
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
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
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text="時間格式錯誤，請使用24小時制，例如：08:00 或 18:30")
                )
                return
            
            # 檢查目標用戶是否存在
            if target_user not in user_mapping:
                # 列出所有已知用戶，幫助用戶選擇正確的用戶名稱
                known_users = list(user_mapping.keys())
                user_list = "\n".join([f"- {name}" for name in known_users])
                
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text=f"找不到用戶 '{target_user}'，請確認用戶名稱正確。\n\n已知用戶列表:\n{user_list}")
                )
                return
            
            # 創建排班
            success = create_or_update_event(
                date_str, 
                f"{hour}:{minute}", 
                target_user, 
                f"排班人員: {target_user}\n排班管理員: {user_name}\n創建時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            # 回覆結果
            if success:
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text=f"已成功為 {target_user} 在 {formatted_date} {formatted_time} 新增排班")
                )
            else:
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text=f"為 {target_user} 新增排班失敗，請稍後再試")
                )
        
        # 新功能：批次排班
        elif match := re.match(BATCH_SHIFT_PATTERN, text):
            # 檢查是否為管理員
            if not is_admin(user_id):
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text="抱歉，只有管理員可以使用此功能")
                )
                return
                
            target_user = match.group(1)
            
            # 檢查目標用戶是否存在
            if target_user not in user_mapping:
                # 列出所有已知用戶，幫助用戶選擇正確的用戶名稱
                known_users = list(user_mapping.keys())
                user_list = "\n".join([f"- {name}" for name in known_users])
                
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text=f"找不到用戶 '{target_user}'，請確認用戶名稱正確。\n\n已知用戶列表:\n{user_list}")
                )
                return
            
            # 創建批次排班
            success, result_message = create_batch_shifts(target_user)
            
            # 回覆結果
            safe_send_message(
                line_bot_api.reply_message,
                reply_token,
                TextSendMessage(text=result_message)
            )
            
        elif text == "查看用戶映射":
            # 管理員功能：查看當前用戶映射
            mapping_text = "\n".join([f"{name}: {id}" for name, id in user_mapping.items()])
            safe_send_message(
                line_bot_api.reply_message,
                reply_token,
                TextSendMessage(text=f"當前用戶映射:\n{mapping_text}")
            )
            
        elif text == "測試日曆":
            # 測試 Google Calendar 連接，並列出一週內的排班
            service = get_calendar_service()
            if service:
                try:
                    # 獲取一週內的事件
                    events = get_week_calendar_events()
                    
                    if not events:
                        safe_send_message(
                            line_bot_api.reply_message,
                            reply_token,
                            TextSendMessage(text="Google Calendar 連接成功，但未找到未來一週內的排班")
                        )
                    else:
                        # 按日期分組事件
                        events_by_date = {}
                        for event in events:
                            start = event.get('start', {}).get('dateTime', '')
                            if start:
                                event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                                date_str = event_time.strftime("%Y/%m/%d")
                                time_str = event_time.strftime("%H:%M")
                                
                                if date_str not in events_by_date:
                                    events_by_date[date_str] = []
                                
                                summary = event.get('summary', '未知班表')
                                events_by_date[date_str].append(f"{time_str} - {summary}")
                        
                        # 生成排班列表
                        result = ["未來一週排班表:"]
                        for date_str in sorted(events_by_date.keys()):
                            result.append(f"\n【{date_str}】")
                            for event_str in sorted(events_by_date[date_str]):
                                result.append(event_str)
                        
                        safe_send_message(
                            line_bot_api.reply_message,
                            reply_token,
                            TextSendMessage(text="\n".join(result))
                        )
                except Exception as e:
                    safe_send_message(
                        line_bot_api.reply_message,
                        reply_token,
                        TextSendMessage(text=f"Google Calendar 連接成功，但查詢事件時發生錯誤: {str(e)}")
                    )
            else:
                safe_send_message(
                    line_bot_api.reply_message,
                    reply_token,
                    TextSendMessage(text="Google Calendar 連接失敗，請檢查服務帳號憑證和日曆 ID 設定")
                )
                
        elif text == "清理緩存":
            # 管理員功能：清理緩存
            old_webhook_count = len(processed_webhook_requests)
            old_message_count = len(sent_messages)
            old_operation_count = len(processed_calendar_operations)
            
            # 清理所有緩存
            processed_webhook_requests.clear()
            sent_messages.clear()
            processed_calendar_operations.clear()
            
            safe_send_message(
                line_bot_api.reply_message,
                reply_token,
                TextSendMessage(text=f"緩存清理完成！\n清理前:\n- Webhook 請求: {old_webhook_count}\n- 訊息: {old_message_count}\n- 日曆操作: {old_operation_count}")
            )
            
        elif text == "幫助":
            # 顯示幫助訊息
            help_text = """可用指令：

【所有用戶】
- 我希望在YYYYMMDD HH:MM跟你換班 @用戶名
  例如：我希望在20250530 08:00跟你換班 @張書豪-Ragic Customize!

- 測試日曆
  查看未來一週的排班表

- 查看用戶映射
  查看系統中已知的用戶名稱和ID對應關係

【僅限管理員】
- 新增排班 YYYYMMDD HH:MM @用戶名
  例如：新增排班 20250530 08:00 @張書豪-Ragic Customize!

- 批次排班 @用戶名
  為未來一週（排除週六日）自動新增排班

- 清理緩存
  清理系統緩存，解決可能的重複訊息問題"""
            
            safe_send_message(
                line_bot_api.reply_message,
                reply_token,
                TextSendMessage(text=help_text)
            )
            
        else:
            # 提示正確的指令格式
            safe_send_message(
                line_bot_api.reply_message,
                reply_token,
                TextSendMessage(text="無法識別的指令。請輸入「幫助」查看可用指令列表。")
            )
    except Exception as e:
        print(f"處理訊息時發生錯誤: {str(e)}")
        # 發送錯誤訊息給用戶
        try:
            safe_send_message(
                line_bot_api.reply_message,
                event.reply_token,
                TextSendMessage(text=f"處理您的請求時發生錯誤，請稍後再試。錯誤詳情: {str(e)}")
            )
        except Exception:
            pass  # 忽略回覆錯誤

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
