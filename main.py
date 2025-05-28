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

# ====== Google Calendar API 函式封裝 ======
def get_calendar_service():
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

    creds = google.oauth2.service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    return build('calendar', 'v3', credentials=creds)

def get_calendar_events(date_str):
    service = get_calendar_service()
    if not service:
        return None
    date = datetime.strptime(date_str, "%Y%m%d")
    time_min = date.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
    time_max = date.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
    events = service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=time_min, timeMax=time_max,
        singleEvents=True, orderBy='startTime'
    ).execute().get('items', [])
    return events

def create_or_update_event(date_str, time_str, user_name, description=None):
    service = get_calendar_service()
    if not service:
        return False
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
    start = dt.isoformat()
    end = dt.replace(hour=dt.hour + 1).isoformat()
    body = {
        'summary': f"班表: {user_name}",
        'description': description or f"排班人員: {user_name}",
        'start': {'dateTime': start, 'timeZone': 'Asia/Taipei'},
        'end':   {'dateTime': end,   'timeZone': 'Asia/Taipei'},
    }

    # 檢查是否已存在同時段事件
    for e in get_calendar_events(date_str) or []:
        s = e.get('start', {}).get('dateTime')
        if s and datetime.fromisoformat(s.replace('Z', '+00:00')) == dt:
            # 更新描述
            old = e.get('description', '')
            body['description'] = f"{old}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 更新為 {user_name}"
            service.events().update(
                calendarId=GOOGLE_CALENDAR_ID,
                eventId=e['id'], body=body
            ).execute()
            return True

    # 不存在同時段就新建
    service.events().insert(
        calendarId=GOOGLE_CALENDAR_ID, body=body
    ).execute()
    return True

def swap_shifts(date_str, time_str, user_a, user_b):
    service = get_calendar_service()
    if not service:
        return False
    target = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
    for e in get_calendar_events(date_str) or []:
        s = e.get('start', {}).get('dateTime')
        if s and datetime.fromisoformat(s.replace('Z', '+00:00')) == target:
            orig = e.get('summary', '').replace('班表: ', '')
            e['summary'] = f"班表: {user_b}"
            old_desc = e.get('description', '')
            e['description'] = f"{old_desc}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {orig} 換給 {user_b}"
            service.events().update(
                calendarId=GOOGLE_CALENDAR_ID,
                eventId=e['id'], body=e
            ).execute()
            return True
    # 不存在則新建
    return create_or_update_event(
        date_str, time_str, user_b,
        f"排班人員: {user_b}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {user_a} 換班"
    )

# ====== FastAPI App ======
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "running", "message": "LINE Bot 換班系統已啟動"}

# 新增：查看目前用戶映射
@app.get("/users")
async def list_users():
    return {"user_mapping": user_mapping}

# 新增：查看指定日期的 Calendar 事件
@app.get("/calendar/events/{date_str}")
async def view_calendar(date_str: str):
    events = get_calendar_events(date_str)
    if events is None:
        raise HTTPException(status_code=500, detail="無法取得 Calendar 事件")
    return {"date": date_str, "events": events}

# 新增：測試用 — 取得今天的 Calendar 事件
@app.get("/calendar/test")
async def test_calendar():
    today = datetime.now().strftime("%Y%m%d")
    events = get_calendar_events(today)
    if events is None:
        raise HTTPException(status_code=500, detail="無法取得今天的 Calendar 事件")
    return {"date": today, "events": events}

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return JSONResponse(content={"status": "ok"})

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
            date_str, hh, mm, target_user = match.groups()
            req_id = f"{user_id}_{date_str}_{hh}_{mm}"
            shift_requests[req_id] = {
                "requester_id": user_id,
                "requester_name": user_name,
                "target_id": user_mapping.get(target_user),
                "target_name": target_user,
                "date": date_str,
                "time": f"{hh}:{mm}",
                "status": "pending"
            }
            # 通知 requester
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"已發送換班請求給 {target_user}，等待回應...")
            )
            # 通知 target
            line_bot_api.push_message(
                shift_requests[req_id]["target_id"],
                TemplateSendMessage(
                    alt_text="換班請求確認",
                    template=ConfirmTemplate(
                        text=f"{user_name} 希望在 {datetime.strptime(date_str,'%Y%m%d').strftime('%Y/%m/%d')} {hh}:{mm} 與您換班",
                        actions=[
                            MessageAction(label="批准", text=f"批准換班:{req_id}"),
                            MessageAction(label="拒絕", text=f"拒絕換班:{req_id}")
                        ]
                    )
                )
            )
            return

        # 處理批准/拒絕
        if text.startswith("批准換班:") or text.startswith("拒絕換班:"):
            action, req_id = text.split(":", 1)
            req = shift_requests.get(req_id)
            if not req:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="找不到對應的換班請求，可能已過期或已處理")
                )
                return
            if req["status"] != "pending":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="此換班請求已處理過，請勿重複操作")
                )
                return

            # 批准
            if action == "批准換班":
                req["status"] = "approved"
                ok = swap_shifts(
                    req["date"], req["time"],
                    req["requester_name"], req["target_name"]
                )
                reply = "已批准換班並更新 Calendar" if ok else "已批准，但更新 Calendar 失敗"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply)
                )
                line_bot_api.push_message(
                    req["requester_id"],
                    TextSendMessage(text=f"{req['target_name']} 已批准您在 {req['date']} {req['time']} 的換班請求")
                )
            else:
                # 拒絕
                req["status"] = "rejected"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="您已拒絕換班請求")
                )
                line_bot_api.push_message(
                    req["requester_id"],
                    TextSendMessage(text=f"{req['target_name']} 已拒絕您在 {req['date']} {req['time']} 的換班請求")
                )

            # 移除已完成請求
            shift_requests.pop(req_id, None)
            return

    except Exception as e:
        print(f"處理訊息時發生錯誤: {e}")
        try:
            line_bot_api.reply_message(
                event.reply_token,
