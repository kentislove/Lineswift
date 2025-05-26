"""
LINE Bot 模組 - 處理 LINE Messaging API 整合
"""
import os
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    PostbackEvent, PostbackAction
)

from .calendar_manager import CalendarManager
from .user_manager import UserManager, is_admin

# 從環境變數獲取 LINE 頻道密鑰
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

# 初始化 LINE Bot API 和 Webhook 處理器
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 創建 FastAPI 路由器
router = APIRouter()

# 初始化日曆管理器和用戶管理器
calendar_manager = CalendarManager()
user_manager = UserManager()

# 換班請求暫存
shift_requests = {}

# 正則表達式模式 - 匹配換班請求
SHIFT_REQUEST_PATTERN = r"我希望在(\d{8})([早中下晚]午|上|下)(\d{1,2}:\d{2})跟你換班"

@router.post("/line/callback")
async def line_callback(request: Request, x_line_signature: Optional[str] = Header(None)):
    """
    LINE Webhook 回調處理
    """
    if not x_line_signature:
        raise HTTPException(status_code=400, detail="X-Line-Signature header is missing")
    
    # 獲取請求體
    body = await request.body()
    body_str = body.decode('utf-8')
    
    try:
        # 驗證簽名並處理 webhook 事件
        handler.handle(body_str, x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return JSONResponse(content={"status": "OK"})

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """
    處理文本消息事件
    """
    user_id = event.source.user_id
    text = event.message.text
    reply_token = event.reply_token
    
    # 檢查是否為管理員
    if not is_admin(user_id):
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="抱歉，只有管理員可以使用此功能。")
        )
        return
    
    # 嘗試匹配換班請求
    match = re.search(SHIFT_REQUEST_PATTERN, text)
    if match:
        handle_shift_request(event, match)
        return
    
    # 處理其他命令
    if text == "幫助" or text == "help":
        show_help(reply_token)
        return
    
    # 默認回覆
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text="您好，管理員！請使用正確的指令格式。輸入「幫助」查看可用指令。")
    )

def handle_shift_request(event, match):
    """
    處理換班請求
    """
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    # 解析日期和時間
    date_str = match.group(1)  # YYYYMMDD
    time_period = match.group(2)  # 早午/下午/晚上
    time_str = match.group(3)  # HH:MM
    
    # 檢查是否有 @ 提及其他用戶
    text = event.message.text
    mentioned_users = extract_mentioned_users(text)
    
    if not mentioned_users:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="請在訊息中 @ 提及您想要換班的用戶。")
        )
        return
    
    target_user_id = mentioned_users[0]
    
    # 檢查目標用戶是否存在
    if not user_manager.user_exists(target_user_id):
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="找不到您提及的用戶。請確保該用戶已加入此 LINE 群組。")
        )
        return
    
    # 格式化日期和時間
    formatted_date = f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"
    
    # 檢查兩位用戶在該時段是否都有排班
    user_a_shift = calendar_manager.get_shift(user_id, date_str, time_period, time_str)
    user_b_shift = calendar_manager.get_shift(target_user_id, date_str, time_period, time_str)
    
    if not user_a_shift:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"您在 {formatted_date} {time_period}{time_str} 沒有排班記錄。")
        )
        return
    
    if not user_b_shift:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"目標用戶在 {formatted_date} {time_period}{time_str} 沒有排班記錄。")
        )
        return
    
    # 儲存換班請求
    request_id = f"{user_id}_{target_user_id}_{date_str}_{time_period}_{time_str}"
    shift_requests[request_id] = {
        "requester_id": user_id,
        "target_id": target_user_id,
        "date": date_str,
        "time_period": time_period,
        "time": time_str,
        "requester_shift": user_a_shift,
        "target_shift": user_b_shift
    }
    
    # 向請求者發送確認訊息
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=f"已向目標用戶發送換班請求。請等待確認。\n日期：{formatted_date}\n時段：{time_period}{time_str}")
    )
    
    # 向目標用戶發送確認請求
    requester_name = user_manager.get_user_name(user_id)
    target_name = user_manager.get_user_name(target_user_id)
    
    confirm_template = ConfirmTemplate(
        text=f"{requester_name} 希望在 {formatted_date} {time_period}{time_str} 與您換班\n\n您的排班：{user_b_shift}\n{requester_name} 的排班：{user_a_shift}\n\n是否同意換班？",
        actions=[
            PostbackAction(
                label="同意換班",
                data=f"action=approve&request_id={request_id}"
            ),
            PostbackAction(
                label="拒絕換班",
                data=f"action=reject&request_id={request_id}"
            )
        ]
    )
    
    line_bot_api.push_message(
        target_user_id,
        TemplateSendMessage(alt_text="換班請求", template=confirm_template)
    )

@handler.add(PostbackEvent)
def handle_postback(event):
    """
    處理按鈕回調事件
    """
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    # 解析回調數據
    data = event.postback.data
    params = dict(item.split("=") for item in data.split("&"))
    
    action = params.get("action")
    request_id = params.get("request_id")
    
    if not request_id or request_id not in shift_requests:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="無效的請求或請求已過期。")
        )
        return
    
    request = shift_requests[request_id]
    
    # 檢查回覆者是否為目標用戶
    if user_id != request["target_id"]:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="您無權回應此請求。")
        )
        return
    
    # 格式化日期和時間
    date_str = request["date"]
    formatted_date = f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"
    time_period = request["time_period"]
    time_str = request["time"]
    
    if action == "approve":
        # 同意換班
        try:
            # 交換排班
            calendar_manager.swap_shifts(
                request["requester_id"], 
                request["target_id"],
                date_str, 
                time_period, 
                time_str
            )
            
            # 通知兩位用戶
            requester_name = user_manager.get_user_name(request["requester_id"])
            target_name = user_manager.get_user_name(request["target_id"])
            
            # 回覆目標用戶
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=f"您已同意與 {requester_name} 在 {formatted_date} {time_period}{time_str} 換班。日曆已更新。")
            )
            
            # 通知請求者
            line_bot_api.push_message(
                request["requester_id"],
                TextSendMessage(text=f"{target_name} 已同意您在 {formatted_date} {time_period}{time_str} 的換班請求。日曆已更新。")
            )
            
        except Exception as e:
            # 處理錯誤
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=f"換班操作失敗：{str(e)}")
            )
        
    elif action == "reject":
        # 拒絕換班
        requester_name = user_manager.get_user_name(request["requester_id"])
        target_name = user_manager.get_user_name(request["target_id"])
        
        # 回覆目標用戶
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"您已拒絕與 {requester_name} 在 {formatted_date} {time_period}{time_str} 換班。")
        )
        
        # 通知請求者
        line_bot_api.push_message(
            request["requester_id"],
            TextSendMessage(text=f"{target_name} 已拒絕您在 {formatted_date} {time_period}{time_str} 的換班請求。")
        )
    
    # 刪除請求
    del shift_requests[request_id]

def extract_mentioned_users(text):
    """
    從文本中提取被 @ 提及的用戶
    """
    # 這裡需要根據 LINE 的實際 @ 提及格式進行調整
    # 假設格式為 "@用戶名"
    mentioned = []
    
    # 在實際應用中，這裡需要從 LINE 的 mention 對象中提取用戶 ID
    # 這裡僅為示例，實際實現可能需要調整
    mentions = re.findall(r"@(\w+)", text)
    for mention in mentions:
        user_id = user_manager.get_user_id_by_name(mention)
        if user_id:
            mentioned.append(user_id)
    
    return mentioned

def show_help(reply_token):
    """
    顯示幫助信息
    """
    help_text = (
        "📅 排班換班助手 - 指令說明\n\n"
        "1. 換班請求：\n"
        "   格式：我希望在YYYYMMDD[早/下/晚]午HH:MM跟你換班 @用戶名\n"
        "   例如：我希望在20250530早上08:00跟你換班 @小明\n\n"
        "2. 其他指令：\n"
        "   - 幫助：顯示此幫助信息\n\n"
        "注意：只有管理員可以發起換班請求。"
    )
    
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=help_text)
    )
