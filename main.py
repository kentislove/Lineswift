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
    TemplateSendMessage, ConfirmTemplate, MessageAction
)
import google.oauth2.service_account
from googleapiclient.discovery import build

# ====== 環境變數設定 ======
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "")

if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("請設置 LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN 環境變數")
if not GOOGLE_CALENDAR_ID:
    print("警告: 未設置 GOOGLE_CALENDAR_ID 環境變數，Google Calendar 功能將無法正常運作")

# ====== LINE Bot 設定 ======
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ====== 換班請求正則表達式 ======
SHIFT_REQUEST_PATTERN = r"我希望在(\d{8})\s+(\d{2}):(\d{2})跟你換班\s*@(.+)"

# ====== 用戶管理 ======
INITIAL_USER_MAPPING = {
    "張書豪-Ragic SA Promote": "Uf15abf85bca4ee133d1027593de4d1ad",
    "KentChang-廠內維修中": "Ub2eb02fea865d917854d6ecaace84c70",
    "Eva-家萍": "eva700802",
    "張書豪-Ragic Customize!": "kent1027",
    "鄭銘貴": "U0c63e33715aebc37754bc2cf522ab6fa",
}
user_mapping = INITIAL_USER_MAPPING.copy()

# 用於存儲換班請求
shift_requests = {}

# ====== Google Calendar API 設定 ======
def get_calendar_service():
    try:
        service_account_info = None
        service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        if service_account_file and os.path.exists(service_account_file):
            with open(service_account_file, 'r') as f:
                service_account_info = json.load(f)
        if not service_account_info:
            service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
            service_account_info = json.loads(service_account_json)
        if not service_account_info:
            print("錯誤: 無法獲取服務帳號憑證")
            return None

        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"獲取 Google Calendar 服務時發生錯誤: {e}")
        return None

def get_calendar_events(date_str):
    service = get_calendar_service()
    if not service:
        return None
    date = datetime.strptime(date_str, "%Y%m%d")
    time_min = date.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
    time_max = date.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def create_or_update_event(date_str, time_str, user_name, description=None):
    service = get_calendar_service()
    if not service:
        return False
    date_time = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
    start_time = date_time.isoformat()
    end_time = date_time.replace(hour=date_time.hour + 1).isoformat()
    summary = f"班表: {user_name}"
    if not description:
        description = f"排班人員: {user_name}"
    event_body = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Taipei'},
        'end':   {'dateTime': end_time,   'timeZone': 'Asia/Taipei'},
    }

    # 檢查現有事件
    events = get_calendar_events(date_str) or []
    existing_event = None
    for e in events:
        start = e.get('start', {}).get('dateTime')
        if start and datetime.fromisoformat(start.replace('Z', '+00:00')) == date_time:
            existing_event = e
            break

    if existing_event:
        old_desc = existing_event.get('description', '')
        new_desc = f"{old_desc}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 更新為 {user_name}"
        event_body['description'] = new_desc
        service.events().update(
            calendarId=GOOGLE_CALENDAR_ID,
            eventId=existing_event['id'],
            body=event_body
        ).execute()
    else:
        service.events().insert(
            calendarId=GOOGLE_CALENDAR_ID,
            body=event_body
        ).execute()
    return True

def swap_shifts(date_str, time_str, user_a, user_b):
    service = get_calendar_service()
    if not service:
        return False
    target_time = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
    events = get_calendar_events(date_str) or []

    # 查找並更新或創建
    for event in events:
        start = event.get('start', {}).get('dateTime')
        if start:
            event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
            if event_time.hour == target_time.hour and event_time.minute == target_time.minute:
                original = event.get('summary', '').replace('班表: ', '')
                event['summary'] = f"班表: {user_b}"
                old_desc = event.get('description', '')
                new_desc = f"{old_desc}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {original} 換給 {user_b}"
                event['description'] = new_desc
                service.events().update(
                    calendarId=GOOGLE_CALENDAR_ID,
                    eventId=event['id'],
                    body=event
                ).execute()
                return True

    # 若未找到則創建
    return create_or_update_event(
        date_str, time_str, user_b,
        f"排班人員: {user_b}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {user_a} 換班"
    )

# ====== FastAPI 設定 ======
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "running", "message": "LINE Bot 換班系統已啟動"}

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")
    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return JSONResponse(content={"status": "ok"})

# ====== LINE 訊息處理 ======
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        user_id = event.source.user_id
        text = event.message.text

        # 更新用戶映射
        try:
            profile = line_bot_api.get_profile(user_id)
            user_mapping[profile.display_name] = user_id
            user_name = profile.display_name
        except LineBotApiError:
            user_name = "未知用戶"

        # 換班請求
        match = re.match(SHIFT_REQUEST_PATTERN, text)
        if match:
            date_str, hour, minute, target_user = match.groups()
            # (省略格式驗證與錯誤回覆，與原程式相同)
            # 儲存並通知
            request_id = f"{user_id}_{date_str}_{hour}_{minute}"
            shift_requests[request_id] = {
                "requester_id": user_id,
                "requester_name": user_name,
                "target_id": user_mapping.get(target_user),
                "target_name": target_user,
                "date": date_str,
                "time": f"{hour}:{minute}",
                "status": "pending"
            }
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"已發送換班請求給 {target_user}，等待回應...")
            )
            line_bot_api.push_message(
                shift_requests[request_id]["target_id"],
                TemplateSendMessage(
                    alt_text="換班請求確認",
                    template=ConfirmTemplate(
                        text=f"{user_name} 希望在 {datetime.strptime(date_str,'%Y%m%d').strftime('%Y/%m/%d')} {hour}:{minute} 與您換班",
                        actions=[
                            MessageAction(label="批准", text=f"批准換班:{request_id}"),
                            MessageAction(label="拒絕", text=f"拒絕換班:{request_id}")
                        ]
                    )
                )
            )
            return

        # 處理批准/拒絕
        if text.startswith("批准換班:") or text.startswith("拒絕換班:"):
            action, request_id = text.split(":", 1)
            request = shift_requests.get(request_id)
            if not request:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="找不到對應的換班請求，可能已過期或已處理")
                )
                return

            # 如果已非 pending，則忽略重複
            if request["status"] != "pending":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="此換班請求已處理過，請勿重複操作")
                )
                return

            if action == "批准換班":
                request["status"] = "approved"
                success = swap_shifts(
                    request["date"],
                    request["time"],
                    request["requester_name"],
                    request["target_name"]
                )
                if success:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="您已批准換班請求，Google Calendar 已更新")
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="您已批准換班請求，但 Google Calendar 更新失敗")
                    )
                line_bot_api.push_message(
                    request["requester_id"],
                    TextSendMessage(text=f"{request['target_name']} 已批准您在 {request['date']} {request['time']} 的換班請求")
                )
            else:  # 拒絕
                request["status"] = "rejected"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="您已拒絕換班請求")
                )
                line_bot_api.push_message(
                    request["requester_id"],
                    TextSendMessage(text=f"{request['target_name']} 已拒絕您在 {request['date']} {request['time']} 的換班請求")
                )

            # 處理完畢後移除，避免重複處理
            shift_requests.pop(request_id, None)
            return

        # 其他指令（查看映射、測試日曆、格式提示等），與原程式相同…

    except Exception as e:
        print(f"處理訊息時發生錯誤: {e}")
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"處理您的請求時發生錯誤，請稍後再試。")
            )
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
