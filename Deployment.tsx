import { motion } from 'framer-motion';

const Deployment = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header Section */}
      <motion.section 
        className="py-12 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold mb-4 text-blue-600">部署說明</h1>
        <p className="text-xl mb-8 text-gray-600 max-w-3xl mx-auto">
          詳細了解如何在您的環境中部署 LINE@ 機器人與 Google Calendar 整合系統，
          從環境設置到 API 憑證配置，一應俱全。
        </p>
      </motion.section>

      {/* Environment Requirements Section */}
      <section className="py-12">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">環境需求</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div>
            <h3 className="text-2xl font-semibold mb-6">基本需求</h3>
            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <ul className="space-y-3">
                <li className="flex items-start">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">✓</span>
                  <span className="text-gray-700">Render Professional Plan 標準實例</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">✓</span>
                  <span className="text-gray-700">GitHub 儲存庫</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">✓</span>
                  <span className="text-gray-700">LINE 開發者帳號與 Messaging API Channel</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">✓</span>
                  <span className="text-gray-700">Google Cloud 專案與 Calendar API 存取權限</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">✓</span>
                  <span className="text-gray-700">Python 3.8 或更高版本</span>
                </li>
              </ul>
            </div>
          </div>
          <div>
            <h3 className="text-2xl font-semibold mb-6">相依套件</h3>
            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <div className="bg-gray-50 p-4 rounded-lg font-mono text-sm mb-4 overflow-auto max-h-60">
                <p>fastapi</p>
                <p>uvicorn</p>
                <p>line-bot-sdk</p>
                <p>google-auth</p>
                <p>google-api-python-client</p>
                <p>langchain</p>
                <p>langchain-community</p>
                <p>openai</p>
                <p>gradio</p>
                <p>httpx</p>
                <p>python-docx</p>
                <p>xlrd</p>
                <p>faiss-cpu</p>
                <p>unstructured</p>
                <p>pypdf</p>
              </div>
              <p className="text-gray-600 text-sm">
                完整相依套件列表請參考專案中的 requirements.txt 檔案。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Deployment Steps Section */}
      <section className="py-12 bg-gray-50 rounded-xl p-8">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">部署步驟</h2>
        <div className="space-y-8">
          <div>
            <h3 className="text-2xl font-semibold mb-4">1. 準備 GitHub 儲存庫</h3>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <ol className="list-decimal pl-5 space-y-3 text-gray-600">
                <li>
                  <p className="font-medium">將專案程式碼上傳至 GitHub 儲存庫</p>
                  <p className="text-sm mt-1">確保您已將所有必要的程式碼檔案上傳至 GitHub 儲存庫。</p>
                </li>
                <li>
                  <p className="font-medium">確保儲存庫包含以下檔案：</p>
                  <ul className="list-disc pl-5 mt-1 text-sm">
                    <li>main.py</li>
                    <li>src/ 目錄（包含 line_bot.py, user_manager.py, calendar_manager.py）</li>
                    <li>utils.py</li>
                    <li>requirements.txt</li>
                    <li>render.yaml</li>
                  </ul>
                </li>
                <li>
                  <p className="font-medium">確認 .gitignore 設定</p>
                  <p className="text-sm mt-1">確保敏感資訊（如 API 金鑰）不會被上傳至儲存庫。</p>
                </li>
              </ol>
            </div>
          </div>
          
          <div>
            <h3 className="text-2xl font-semibold mb-4">2. 設置 Render 服務</h3>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <ol className="list-decimal pl-5 space-y-3 text-gray-600">
                <li>
                  <p className="font-medium">登入 Render 平台</p>
                  <p className="text-sm mt-1">前往 <a href="https://dashboard.render.com" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">https://dashboard.render.com</a> 並登入您的帳號。</p>
                </li>
                <li>
                  <p className="font-medium">選擇「New Web Service」</p>
                  <p className="text-sm mt-1">在儀表板中點擊「New +」按鈕，然後選擇「Web Service」。</p>
                </li>
                <li>
                  <p className="font-medium">連接 GitHub 儲存庫</p>
                  <p className="text-sm mt-1">選擇包含專案程式碼的 GitHub 儲存庫。</p>
                </li>
                <li>
                  <p className="font-medium">設置服務名稱與環境變數</p>
                  <p className="text-sm mt-1">輸入服務名稱，並設置必要的環境變數（詳見 API 憑證設置部分）。</p>
                </li>
                <li>
                  <p className="font-medium">選擇 Professional Plan 標準實例</p>
                  <p className="text-sm mt-1">在實例類型中選擇 Professional Plan 標準實例。</p>
                </li>
                <li>
                  <p className="font-medium">設置啟動命令</p>
                  <p className="text-sm mt-1">設置啟動命令為：<code>uvicorn main:app --host 0.0.0.0 --port 10000</code></p>
                </li>
                <li>
                  <p className="font-medium">點擊「Create Web Service」</p>
                  <p className="text-sm mt-1">確認所有設定後，點擊「Create Web Service」按鈕創建服務。</p>
                </li>
              </ol>
            </div>
          </div>
          
          <div>
            <h3 className="text-2xl font-semibold mb-4">3. 初始化系統</h3>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <ol className="list-decimal pl-5 space-y-3 text-gray-600">
                <li>
                  <p className="font-medium">部署完成後，通過 Render 的 Shell 功能執行初始化腳本</p>
                  <p className="text-sm mt-1">在 Render 儀表板中，選擇您的服務，點擊「Shell」標籤，然後執行：</p>
                  <div className="bg-gray-100 p-2 rounded mt-1 font-mono text-sm">
                    python init.py
                  </div>
                </li>
                <li>
                  <p className="font-medium">確認初始化成功</p>
                  <p className="text-sm mt-1">確認系統顯示「初始化完成，系統準備就緒」訊息。</p>
                </li>
              </ol>
            </div>
          </div>
          
          <div>
            <h3 className="text-2xl font-semibold mb-4">4. 設置 LINE Webhook</h3>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <ol className="list-decimal pl-5 space-y-3 text-gray-600">
                <li>
                  <p className="font-medium">登入 LINE Developers Console</p>
                  <p className="text-sm mt-1">前往 <a href="https://developers.line.biz" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">https://developers.line.biz</a> 並登入您的帳號。</p>
                </li>
                <li>
                  <p className="font-medium">進入您的 Messaging API Channel</p>
                  <p className="text-sm mt-1">選擇您的 Provider，然後選擇您的 Messaging API Channel。</p>
                </li>
                <li>
                  <p className="font-medium">設置 Webhook URL</p>
                  <p className="text-sm mt-1">在 Webhook URL 欄位中輸入：</p>
                  <div className="bg-gray-100 p-2 rounded mt-1 font-mono text-sm">
                    https://您的Render服務網址/line/callback
                  </div>
                </li>
                <li>
                  <p className="font-medium">開啟「Use webhook」選項</p>
                  <p className="text-sm mt-1">確保「Use webhook」選項已開啟。</p>
                </li>
                <li>
                  <p className="font-medium">點擊「Verify」確認連接成功</p>
                  <p className="text-sm mt-1">點擊「Verify」按鈕，確認 Webhook 連接成功。</p>
                </li>
              </ol>
            </div>
          </div>
        </div>
      </section>

      {/* API Credentials Section */}
      <section className="py-12">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">API 憑證設置</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div>
            <h3 className="text-2xl font-semibold mb-6">LINE Messaging API 憑證</h3>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <ol className="list-decimal pl-5 space-y-3 text-gray-600">
                <li>
                  <p className="font-medium">登入 LINE Developers Console</p>
                  <p className="text-sm mt-1">前往 <a href="https://developers.line.biz" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">https://developers.line.biz</a> 並登入您的帳號。</p>
                </li>
                <li>
                  <p className="font-medium">創建或選擇現有的 Provider</p>
                  <p className="text-sm mt-1">如果您還沒有 Provider，請點擊「Create a new provider」創建一個。</p>
                </li>
                <li>
                  <p className="font-medium">創建一個新的 Messaging API Channel</p>
                  <p className="text-sm mt-1">點擊「Create a new channel」，然後選擇「Messaging API」。</p>
                </li>
                <li>
                  <p className="font-medium">取得 Channel Secret 與 Channel Access Token</p>
                  <p className="text-sm mt-1">在 Channel 設定頁面中，您可以找到 Channel Secret 與 Channel Access Token。</p>
                </li>
                <li>
                  <p className="font-medium">在 Render 平台設置環境變數</p>
                  <p className="text-sm mt-1">在 Render 服務的「Environment」標籤中，添加以下環境變數：</p>
                  <ul className="list-disc pl-5 mt-1 text-sm">
                    <li><code>LINE_CHANNEL_SECRET</code>：您的 Channel Secret</li>
                    <li><code>LINE_CHANNEL_ACCESS_TOKEN</code>：您的 Channel Access Token</li>
                  </ul>
                </li>
              </ol>
            </div>
          </div>
          <div>
            <h3 className="text-2xl font-semibold mb-6">Google Calendar API 憑證</h3>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <ol className="list-decimal pl-5 space-y-3 text-gray-600">
                <li>
                  <p className="font-medium">登入 Google Cloud Console</p>
                  <p className="text-sm mt-1">前往 <a href="https://console.cloud.google.com" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">https://console.cloud.google.com</a> 並登入您的帳號。</p>
                </li>
                <li>
                  <p className="font-medium">創建新專案或選擇現有專案</p>
                  <p className="text-sm mt-1">點擊頁面頂部的專案選擇器，然後點擊「NEW PROJECT」或選擇現有專案。</p>
                </li>
                <li>
                  <p className="font-medium">啟用 Google Calendar API</p>
                  <p className="text-sm mt-1">在左側選單中，選擇「APIs &amp; Services」{'>'}「Library」，搜尋「Google Calendar API」並啟用它。</p>
                </li>
                <li>
                  <p className="font-medium">創建服務帳號</p>
                  <p className="text-sm mt-1">在左側選單中，選擇「IAM &amp; Admin」{'>'}「Service Accounts」，然後點擊「CREATE SERVICE ACCOUNT」。</p>
                </li>
                <li>
                  <p className="font-medium">設置服務帳號權限</p>
                  <p className="text-sm mt-1">授予服務帳號「Calendar API」的編輯權限。</p>
                </li>
                <li>
                  <p className="font-medium">創建並下載 JSON 格式的金鑰檔案</p>
                  <p className="text-sm mt-1">在服務帳號詳情頁面中，選擇「KEYS」標籤，點擊「ADD KEY」{'>'}「Create new key」，選擇 JSON 格式，然後點擊「CREATE」下載金鑰檔案。</p>
                </li>
                <li>
                  <p className="font-medium">在 Google Calendar 中共享日曆</p>
                  <p className="text-sm mt-1">開啟 Google Calendar，找到目標日曆，點擊「設定與共享」，在「與特定人員共享」中，添加服務帳號的電子郵件地址，並授予「變更與管理共享設定」權限。</p>
                </li>
                <li>
                  <p className="font-medium">在 Render 平台上傳服務帳號金鑰</p>
                  <p className="text-sm mt-1">使用 Render 的「Files」功能上傳 JSON 金鑰檔案，記錄上傳後的檔案路徑。</p>
                </li>
                <li>
                  <p className="font-medium">在 Render 平台設置環境變數</p>
                  <p className="text-sm mt-1">在 Render 服務的「Environment」標籤中，添加以下環境變數：</p>
                  <ul className="list-disc pl-5 mt-1 text-sm">
                    <li><code>GOOGLE_SERVICE_ACCOUNT_FILE</code>：服務帳號金鑰檔案的路徑</li>
                    <li><code>GOOGLE_CALENDAR_ID</code>：目標日曆的 ID（通常是日曆的電子郵件地址）</li>
                  </ul>
                </li>
              </ol>
            </div>
          </div>
        </div>
      </section>

      {/* Troubleshooting Section */}
      <section className="py-12 bg-gray-50 rounded-xl p-8">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">常見問題排查</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-blue-600">LINE Webhook 連接失敗</h3>
            <p className="text-gray-600 mb-4">
              如果 LINE Webhook 驗證失敗或無法接收訊息，請檢查以下項目：
            </p>
            <ul className="list-disc pl-5 space-y-2 text-gray-600">
              <li>確認 Webhook URL 是否正確設置</li>
              <li>檢查 Channel Secret 與 Channel Access Token 是否正確</li>
              <li>確認 Render 服務是否正常運行</li>
              <li>檢查 Render 日誌中是否有錯誤訊息</li>
            </ul>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-blue-600">Google Calendar API 連接失敗</h3>
            <p className="text-gray-600 mb-4">
              如果無法查詢或更新 Google Calendar 資料，請檢查以下項目：
            </p>
            <ul className="list-disc pl-5 space-y-2 text-gray-600">
              <li>確認服務帳號金鑰檔案是否正確上傳</li>
              <li>檢查服務帳號是否有足夠權限</li>
              <li>確認日曆 ID 是否正確</li>
              <li>檢查 Render 日誌中是否有 API 錯誤訊息</li>
            </ul>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-blue-600">換班請求無法發送</h3>
            <p className="text-gray-600 mb-4">
              如果管理員無法發送換班請求，請檢查以下項目：
            </p>
            <ul className="list-disc pl-5 space-y-2 text-gray-600">
              <li>確認用戶是否已被設置為管理員</li>
              <li>檢查訊息格式是否正確</li>
              <li>確認 @ 提及的用戶是否存在</li>
              <li>檢查雙方在指定時段是否都有排班記錄</li>
            </ul>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-blue-600">系統無響應</h3>
            <p className="text-gray-600 mb-4">
              如果系統沒有回應用戶訊息，請檢查以下項目：
            </p>
            <ul className="list-disc pl-5 space-y-2 text-gray-600">
              <li>檢查 Render 服務狀態</li>
              <li>查看 Render 日誌中是否有錯誤</li>
              <li>確認 LINE Webhook 是否正常連接</li>
             
(Content truncated due to size limit. Use line ranges to read in chunks)