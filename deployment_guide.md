"""
操作與部署說明文件 - LINE@ 機器人與 Google Calendar 整合系統
"""

# LINE@ 機器人與 Google Calendar 整合系統
## 操作與部署說明文件

### 目錄
1. [系統概述](#1-系統概述)
2. [環境需求](#2-環境需求)
3. [部署步驟](#3-部署步驟)
4. [API 憑證設置](#4-api-憑證設置)
5. [系統功能說明](#5-系統功能說明)
6. [管理員操作指南](#6-管理員操作指南)
7. [用戶操作指南](#7-用戶操作指南)
8. [常見問題排查](#8-常見問題排查)
9. [系統維護](#9-系統維護)

---

### 1. 系統概述

本系統整合 LINE@ 機器人與 Google Calendar，實現管理員用戶間的排班變更與確認功能。系統架設於 Render 的 Professional Plan 上，並透過 GitHub 進行版本控制與自動部署。

主要功能：
- 管理員可在 LINE@ 中發送換班請求
- 系統自動檢查兩位用戶在指定日期的排班情況
- 目標用戶收到換班請求並可選擇同意或拒絕
- 經確認後，系統自動更新 Google Calendar 上的排班資料

---

### 2. 環境需求

- Render Professional Plan 標準實例
- GitHub 儲存庫
- LINE 開發者帳號與 Messaging API Channel
- Google Cloud 專案與 Calendar API 存取權限
- Python 3.8 或更高版本

相依套件：
- fastapi
- uvicorn
- line-bot-sdk
- google-auth
- google-api-python-client
- langchain
- langchain-community
- openai
- gradio
- 其他套件詳見 requirements.txt

---

### 3. 部署步驟

#### 3.1 準備 GitHub 儲存庫

1. 將專案程式碼上傳至 GitHub 儲存庫
2. 確保儲存庫包含以下檔案：
   - main.py
   - src/ 目錄（包含 line_bot.py, user_manager.py, calendar_manager.py）
   - utils.py
   - requirements.txt
   - render.yaml

#### 3.2 設置 Render 服務

1. 登入 Render 平台
2. 選擇「New Web Service」
3. 連接 GitHub 儲存庫
4. 設置服務名稱與環境變數（詳見 [API 憑證設置](#4-api-憑證設置)）
5. 選擇 Professional Plan 標準實例
6. 設置啟動命令：`uvicorn main:app --host 0.0.0.0 --port 10000`
7. 點擊「Create Web Service」

#### 3.3 初始化系統

1. 部署完成後，通過 Render 的 Shell 功能執行初始化腳本：
   ```
   python init.py
   ```
2. 確認初始化成功，系統顯示「初始化完成，系統準備就緒」

#### 3.4 設置 LINE Webhook

1. 登入 LINE Developers Console
2. 進入您的 Messaging API Channel
3. 在 Webhook URL 欄位中輸入：`https://您的Render服務網址/line/callback`
4. 開啟「Use webhook」選項
5. 點擊「Verify」確認連接成功

---

### 4. API 憑證設置

#### 4.1 LINE Messaging API 憑證

1. 登入 [LINE Developers Console](https://developers.line.biz/)
2. 創建或選擇現有的 Provider
3. 創建一個新的 Messaging API Channel
4. 取得以下資訊：
   - Channel Secret
   - Channel Access Token

5. 在 Render 平台設置以下環境變數：
   - `LINE_CHANNEL_SECRET`：您的 Channel Secret
   - `LINE_CHANNEL_ACCESS_TOKEN`：您的 Channel Access Token

#### 4.2 Google Calendar API 憑證

1. 登入 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新專案或選擇現有專案
3. 啟用 Google Calendar API
4. 創建服務帳號：
   - 進入「IAM 與管理」>「服務帳號」
   - 點擊「創建服務帳號」
   - 設置服務帳號名稱與描述
   - 授予「Calendar API」的編輯權限
   - 創建並下載 JSON 格式的金鑰檔案

5. 在 Google Calendar 中共享日曆：
   - 開啟 Google Calendar
   - 找到目標日曆，點擊「設定與共享」
   - 在「與特定人員共享」中，添加服務帳號的電子郵件地址
   - 授予「變更與管理共享設定」權限

6. 在 Render 平台上傳服務帳號金鑰：
   - 使用 Render 的「Files」功能上傳 JSON 金鑰檔案
   - 記錄上傳後的檔案路徑

7. 在 Render 平台設置以下環境變數：
   - `GOOGLE_SERVICE_ACCOUNT_FILE`：服務帳號金鑰檔案的路徑
   - `GOOGLE_CALENDAR_ID`：目標日曆的 ID（通常是日曆的電子郵件地址）

#### 4.3 OpenAI API 憑證

1. 登入 [OpenAI 平台](https://platform.openai.com/)
2. 創建 API 金鑰
3. 在 Render 平台設置環境變數：
   - `OPENAI_API_KEY`：您的 OpenAI API 金鑰

---

### 5. 系統功能說明

#### 5.1 LINE@ 機器人功能

- **換班請求**：管理員可發送換班請求給其他用戶
- **換班確認**：目標用戶可同意或拒絕換班請求
- **幫助指令**：顯示可用指令與格式說明

#### 5.2 Google Calendar 整合功能

- **排班查詢**：查詢用戶在指定日期的排班資訊
- **排班交換**：在用戶確認後自動交換排班資訊
- **操作記錄**：在日曆事件中記錄換班歷史

#### 5.3 用戶管理功能

- **管理員權限**：識別與驗證管理員身份
- **用戶識別**：通過 LINE ID 識別用戶身份

---

### 6. 管理員操作指南

#### 6.1 發送換班請求

1. 在 LINE@ 中，使用以下格式發送訊息：
   ```
   我希望在YYYYMMDD[早/下/晚]午HH:MM跟你換班 @用戶名
   ```
   
   例如：
   ```
   我希望在20250530早上08:00跟你換班 @小明
   ```

2. 系統會自動檢查：
   - 您是否為管理員
   - 您與目標用戶在指定時段是否都有排班
   - 目標用戶是否存在

3. 若條件符合，系統會向目標用戶發送換班請求

#### 6.2 查看幫助

在 LINE@ 中發送「幫助」或「help」，系統會回覆可用指令與格式說明。

---

### 7. 用戶操作指南

#### 7.1 回應換班請求

當收到換班請求時：

1. 系統會發送一則訊息，包含：
   - 請求者資訊
   - 換班日期與時間
   - 雙方的排班詳情
   - 「同意換班」與「拒絕換班」按鈕

2. 點擊「同意換班」：
   - 系統會自動交換雙方的排班資訊
   - 雙方都會收到換班成功的通知

3. 點擊「拒絕換班」：
   - 系統會通知請求者換班被拒絕
   - 不會進行任何排班變更

---

### 8. 常見問題排查

#### 8.1 LINE Webhook 連接失敗

**問題**：LINE Webhook 驗證失敗或無法接收訊息

**解決方案**：
1. 確認 Webhook URL 是否正確設置
2. 檢查 Channel Secret 與 Channel Access Token 是否正確
3. 確認 Render 服務是否正常運行
4. 檢查 Render 日誌中是否有錯誤訊息

#### 8.2 Google Calendar API 連接失敗

**問題**：無法查詢或更新 Google Calendar 資料

**解決方案**：
1. 確認服務帳號金鑰檔案是否正確上傳
2. 檢查服務帳號是否有足夠權限
3. 確認日曆 ID 是否正確
4. 檢查 Render 日誌中是否有 API 錯誤訊息

#### 8.3 換班請求無法發送

**問題**：管理員無法發送換班請求

**解決方案**：
1. 確認用戶是否已被設置為管理員
2. 檢查訊息格式是否正確
3. 確認 @ 提及的用戶是否存在
4. 檢查雙方在指定時段是否都有排班記錄

#### 8.4 系統無響應

**問題**：系統沒有回應用戶訊息

**解決方案**：
1. 檢查 Render 服務狀態
2. 查看 Render 日誌中是否有錯誤
3. 確認 LINE Webhook 是否正常連接
4. 重新啟動 Render 服務

---

### 9. 系統維護

#### 9.1 日常維護

1. **監控系統日誌**：
   - 定期檢查 Render 平台的日誌
   - 關注錯誤訊息與警告

2. **更新依賴套件**：
   - 定期更新 requirements.txt 中的套件版本
   - 測試更新後的系統功能

3. **備份資料**：
   - 定期備份用戶資料庫
   - 保存重要的系統配置

#### 9.2 故障恢復

1. **服務中斷**：
   - 檢查 Render 平台狀態
   - 查看錯誤日誌
   - 必要時重新部署服務

2. **資料不一致**：
   - 檢查用戶資料庫
   - 驗證 Google Calendar 資料
   - 必要時從備份恢復

#### 9.3 系統升級

1. **程式碼更新**：
   - 在測試環境中驗證新功能
   - 提交更新至 GitHub 儲存庫
   - Render 將自動部署更新

2. **環境變數更新**：
   - 在 Render 平台更新環境變數
   - 重新啟動服務以套用變更

---

如有任何問題或需要進一步協助，請聯繫系統管理員。
