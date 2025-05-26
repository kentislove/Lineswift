import os
import re
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ConfirmTemplate, MessageAction
)

# ====== 環境變數設定 ======
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

# 確認環境變數已設置
if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("請設置 LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN 環境變數")

# ====== LINE Bot 設定 ======
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ====== 換班請求正則表達式 ======
# 匹配格式: "我希望在YYYYMMDD[早/下/晚]午HH:MM跟你換班 @用戶名"
SHIFT_REQUEST_PATTERN = r"我希望在(\d{8})([早下晚])上?(\d{2}):(\d{2})跟你換班\s*@(.+)"

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
        
        # 檢查是否為換班請求
        match = re.match(SHIFT_REQUEST_PATTERN, text)
        if match:
            date_str, time_period, hour, minute, target_user = match.groups()
            
            # 解析日期
            try:
                date = datetime.strptime(date_str, "%Y%m%d").strftime("%Y/%m/%d")
            except ValueError:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="日期格式錯誤，請使用YYYYMMDD格式，例如：20250530")
                )
                return
            
            # 時間段轉換
            time_period_full = {"早": "早上", "下": "下午", "晚": "晚上"}.get(time_period, time_period)
            
            # 構建確認訊息
            confirm_message = f"換班請求\n請求在{date} {time_period_full}{hour}:{minute}進行換班"
            
            # 發送確認模板
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text="換班請求確認",
                    template=ConfirmTemplate(
                        text=confirm_message,
                        actions=[
                            MessageAction(label="批准", text="批准換班"),
                            MessageAction(label="拒絕", text="拒絕換班")
                        ]
                    )
                )
            )
        elif text in ["批准換班", "拒絕換班"]:
            # 處理換班回應
            response = "您已批准換班請求，系統將更新日曆。" if text == "批准換班" else "您已拒絕換班請求。"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response)
            )
        else:
            # 提示正確的換班請求格式
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請使用正確的換班請求格式：\n我希望在YYYYMMDD[早/下/晚]上HH:MM跟你換班 @用戶名\n\n例如：\n我希望在20250530早上08:00跟你換班 @小明")
            )
    except Exception as e:
        print(f"處理訊息時發生錯誤: {str(e)}")
        # 發送錯誤訊息給用戶
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"處理您的請求時發生錯誤，請稍後再試。")
            )
        except Exception:
            pass  # 忽略回覆錯誤

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
