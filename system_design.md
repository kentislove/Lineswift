# LINE@ 機器人與 Google Calendar 整合系統設計

## 系統架構概述

本系統將整合 LINE@ 機器人與 Google Calendar，實現管理員用戶間的排班變更與確認功能。系統架設於 Render 的 Professional Plan 上，並透過 GitHub 進行版本控制與自動部署。

### 主要元件

1. **LINE@ 機器人**：處理用戶訊息、指令解析與回應
2. **後端伺服器**：運行於 Render 平台，處理業務邏輯
3. **Google Calendar API**：查詢與更新日曆資料
4. **資料庫**：儲存用戶資訊、權限與操作記錄

## 流程設計

### 1. 訊息指令格式與解析邏輯

#### 換班請求格式
管理員 A 發送的換班請求訊息格式：
```
我希望在[YYYYMMDD][時段]跟你換班
```

例如：`我希望在20250530早上08:00跟你換班`

系統將解析以下關鍵資訊：
- 日期：YYYYMMDD 格式（如 20250530）
- 時段：包含「早上」、「下午」、「晚上」等關鍵詞
- 時間：具體時間點（如 08:00）

#### 解析邏輯
1. 使用正則表達式匹配日期、時段與時間
2. 驗證日期格式與有效性
3. 將時段與時間轉換為 Google Calendar 可用的時間格式

### 2. 用戶身份辨識與權限驗證流程

#### 管理員身份驗證
1. 透過 LINE@ 內建的管理員設定功能識別管理員身份
2. 在收到訊息時，檢查發送者是否具有管理員權限
3. 非管理員用戶的請求將被拒絕並收到相應提示

#### 用戶 B 身份識別
1. 管理員 A 在 LINE@ 群組中直接 @ 提及用戶 B
2. 系統識別被 @ 的用戶為目標用戶 B
3. 若在私聊中，管理員需明確指定用戶 B 的 LINE ID 或顯示名稱

### 3. Google Calendar 資料查詢與更新流程

#### 日曆資料查詢
1. 根據解析出的日期與時間，查詢 Google Calendar 上指定帳號的排班資料
2. 檢查用戶 A 在該時段是否有排班資料
3. 檢查用戶 B 在該時段是否有排班資料
4. 若兩位用戶都有排班資料，則繼續確認流程；否則通知無法換班的原因

#### 日曆資料更新
1. 獲取用戶 A 與用戶 B 在指定日期的排班詳細資訊
2. 交換兩位用戶的排班資料
3. 使用 Google Calendar API 更新日曆事件
4. 記錄變更操作，包含時間、用戶與變更內容

### 4. 用戶確認機制與回覆格式

#### 確認請求
系統向用戶 B 發送確認請求，格式如下：
```
[用戶 A 名稱] 希望在 [YYYY/MM/DD] [時段] [時間] 與您換班
您在該時段的排班為：[用戶 B 排班詳情]
用戶 A 在該時段的排班為：[用戶 A 排班詳情]

請回覆「同意換班」或「拒絕換班」
```

#### 確認回覆
1. 用戶 B 可回覆「同意換班」或「拒絕換班」
2. 若用戶 B 同意，系統執行日曆資料更新流程
3. 若用戶 B 拒絕，系統通知用戶 A 換班請求被拒絕
4. 若用戶 B 在指定時間內未回覆，系統將發送提醒或自動拒絕請求

#### 操作結果通知
1. 換班成功：通知兩位用戶換班已完成，並提供更新後的排班資訊
2. 換班失敗：通知相關用戶換班失敗的原因，並提供可能的解決方案

## 技術實現

### LINE Messaging API 整合
1. 使用 LINE Messaging API 接收與發送訊息
2. 實現 Webhook 接收用戶訊息與事件
3. 使用 LINE 的 Reply 與 Push 功能發送回應與通知

### Google Calendar API 整合
1. 使用 OAuth 2.0 進行身份驗證與授權
2. 實現日曆事件的查詢、創建、更新與刪除功能
3. 處理日曆資料的同步與衝突解決

### 資料庫設計
1. 用戶表：儲存用戶資訊與權限
2. 操作記錄表：記錄所有換班請求與結果
3. 排班資料表：緩存當前排班資訊，提高查詢效率

## 安全性考量

1. 使用 HTTPS 確保所有通訊加密
2. 實現 API 請求的驗證與授權
3. 敏感資訊（如 API 金鑰）使用環境變數儲存
4. 實現請求頻率限制，防止濫用
5. 記錄所有操作，便於審計與問題排查

## 擴展性考量

1. 模組化設計，便於新增功能
2. 支援多種日期與時間格式的解析
3. 可配置的通知與提醒機制
4. 支援未來整合其他日曆系統或排班系統
