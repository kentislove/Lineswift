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
    MessageEvent,
    TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    ConfirmTemplate,
    MessageAction
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

# ====== LINE Bot 初始 ======
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 換班請求正則
SHIFT_REQUEST_PATTERN = r"我希望在(\d{8})\s+(\d{2}):(\d{2})跟你換班\s*@(.+)"

# 用戶映射
INITIAL_USER_MAPPING = {
    "張書豪-Ragic SA Promote": "Uf15abf85bca4ee133d1027593de4d1ad",
    "KentChang-廠內維修中": "Ub2eb02fea865d917854d6ecaace84c70",
    "Eva-家萍": "eva700802",
    "張書豪-Ragic Customize!": "kent1027",
    "鄭銘貴": "U0c63e33715aebc37754bc2cf522ab6fa",
}
user_mapping = INITIAL_USER_MAPPING.copy()
shift_requests = {}

# ====== Google Calendar API ======
def get_calendar_service():
    info = None
    sa_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if sa_file and os.path.exists(sa_file):
        with open(sa_file, 'r', encoding='utf-8') as f:
            info = json.load(f)
    if not info:
        info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}"))
    if not info:
        print("錯誤: 無法獲取服務帳號憑證")
        return None

    creds = google.oauth2.service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return build("calendar", "v3", credentials=creds)

def get_calendar_events(date_str: str):
    service = get_calendar_service()
    if not service:
        return None
    dt = datetime.strptime(date_str, "%Y%m%d")
    tmin = dt.replace(hour=0, minute=0, second=0).isoformat() + "Z"
    tmax = dt.replace(hour=23, minute=59, second=59).isoformat() + "Z"
    return service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=tmin,
        timeMax=tmax,
        singleEvents=True,
        orderBy="startTime"
    ).execute().get("items", [])

def create_or_update_event(date_str, time_str, user_name, description=None):
    service = get_calendar_service()
    if not service:
        return False
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
    start = dt.isoformat()
    end = dt.replace(hour=dt.hour+1).isoformat()
    body = {
        "summary": f"班表: {user_name}",
        "description": description or f"排班人員: {user_name}",
        "start": {"dateTime": start, "timeZone": "Asia/Taipei"},
        "end":   {"dateTime": end,   "timeZone": "Asia/Taipei"},
    }

    # 檢查既有事件
    for e in get_calendar_events(date_str) or []:
        s = e.get("start", {}).get("dateTime")
        if s and datetime.fromisoformat(s.replace("Z","+00:00")) == dt:
            old = e.get("description", "")
            body["description"] = f"{old}\n換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 更新為 {user_name}"
            service.events().update(
                calendarId=GOOGLE_CALENDAR_ID,
                eventId=e["id"],
                body=body
            ).execute()
            return True

    service.events().insert(
        calendarId=GOOGLE_CALENDAR_ID,
        body=body
    ).execute()
    return True

def swap_shifts(date_str, time_str, user_a, user_b):
    service = get_calendar_service()
    if not service:
        return False
    target = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
    for e in get_calendar_events(date_str) or []:
        s = e.get("start", {}).get("dateTime")
        if s and datetime.fromisoformat(s.replace("Z","+00:00")) == target:
            orig = e.get("summary","").replace("班表: ","")
            e["summary"] = f"班表: {user_b}"
            old_desc = e.get("description","")
            e["description"] = (
                f"{old_desc}\n"
                f"換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} "
                f"- 從 {orig} 換給 {user_b}"
            )
            service.events().update(
                calendarId=GOOGLE_CALENDAR_ID,
                eventId=e["id"],
                body=e
            ).execute()
            return True

    # 若找不到同時段，直接新建
    return create_or_update_event(
        date_str, time_str, user_b,
        f"排班人員: {user_b}\n"
        f"換班歷史: {datetime.now().strftime('%Y-%m-%d %H:%M')} - 從 {user_a} 換班"
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
    return {"status":"running","message":"LINE Bot 換班系統已啟動"}

# 查看用戶映射
@app.get("/users")
async def list_users():
    return {"user_mapping": user_mapping}

# 查看指定日期的 Calendar 事件
@app.get("/calendar/events/{date_str}")
async def view_calendar(date_str: str):
    events = get_calendar_events(date_str)
    if events is None:
        raise HTTPException(status_code=500, detail="無法取得 Calendar 事件")
    return {"date": date_str, "events": events}

# 測試今天的 Calendar 事件
@app.get("/calendar/test")
async def test_calendar():
    today = datetime.now().strftime("%Y%m%d")
    events = get_calendar_events(today)
    if events is None:
        raise HTTPException(status_code=500, detail="無法取得今天的 Calendar 事件")
    return {"date": today, "events": events}

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature","")
    body = await request.body()
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return JSONResponse(content={"status":"ok"})

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        user_id = event.source.user_id
        text = event.message.text

        # 更新映射
        try:
            profile = line_bot_api.get_profile(user_id)
            user_mapping[profile.display_name] = user_id
            user_name = profile.display_name
        except LineBotApiError:
            user_name = "未知用戶"

        # 換班請求
        m = re.match(SHIFT_REQUEST_PATTERN, text)
        if m:
            date_str, hh, mm, target = m.groups()
            req_id = f"{user_id}_{date_str}_{hh}_{mm}"
            shift_requests[req_id] = {
                "requester_id": user_id,
                "requester_name": user_name,
                "target_id": user_mapping.get(target),
                "target_name": target,
                "date": date_str,
                "time": f"{hh}:{mm}",
                "status": "pending"
            }
            # 回覆申請者
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"已發送換班請求給 {target}，等待回應...")
            )
            # 通知對方
            line_bot_api.push_message(
                shift_requests[req_id]["target_id"],
                TemplateSendMessage(
                    alt_text="換班請求確認",
                    template=ConfirmTemplate(
                        text=(
                            f"{user_name} 希望在 "
                            f"{datetime.strptime(date_str,'%Y%m%d').strftime('%Y/%m/%d')} "
                            f"{hh}:{mm} 與您換班"
                        ),
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

            if action == "批准換班":
                req["status"] = "approved"
                ok = swap_shifts(
                    req["date"],
                    req["time"],
                    req["requester_name"],
                    req["target_name"]
                )
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=(
                            "已批准換班並更新 Calendar"
                            if ok else
                            "已批准，但更新 Calendar 失敗"
                        )
                    )
                )
                line_bot_api.push_message(
                    req["requester_id"],
                    TextSendMessage(
                        text=f"{req['target_name']} 已批准您在 {req['date']} {req['time']} 的換班請求"
                    )
                )
            else:
                req["status"] = "rejected"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="您已拒絕換班請求")
                )
                line_bot_api.push_message(
                    req["requester_id"],
                    TextSendMessage(
                        text=f"{req['target_name']} 已拒絕您在 {req['date']} {req['time']} 的換班請求"
                    )
                )

            shift_requests.pop(req_id, None)
            return

    except Exception as e:
        print(f"處理訊息時發生錯誤: {e}")
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="處理您的請求時發生錯誤，請稍後再試。")
            )
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT","10000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
