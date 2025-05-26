import { motion } from 'framer-motion';

const Guide = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header Section */}
      <motion.section 
        className="py-12 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold mb-4 text-blue-600">操作指南</h1>
        <p className="text-xl mb-8 text-gray-600 max-w-3xl mx-auto">
          詳細了解如何使用 LINE@ 機器人與 Google Calendar 整合系統，
          從管理員設置到日常操作，一應俱全。
        </p>
      </motion.section>

      {/* Admin Guide Section */}
      <section className="py-12">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">管理員操作指南</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-start">
          <div>
            <h3 className="text-2xl font-semibold mb-6">發送換班請求</h3>
            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <h4 className="text-lg font-medium mb-3 text-blue-600">訊息格式</h4>
              <div className="bg-gray-100 p-4 rounded-lg font-mono text-sm mb-4">
                我希望在YYYYMMDD[早/下/晚]午HH:MM跟你換班 @用戶名
              </div>
              <p className="text-gray-600 mb-2">例如：</p>
              <div className="bg-gray-100 p-4 rounded-lg font-mono text-sm">
                我希望在20250530早上08:00跟你換班 @小明
              </div>
              <img 
                src="/images/line_message_simulation.png" 
                alt="LINE 訊息模擬" 
                className="w-full h-auto rounded-lg mt-4"
              />
              <p className="text-center text-gray-500 mt-2">LINE 換班請求與確認訊息模擬</p>
            </div>
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">步驟 1：確認排班</h4>
                <p className="text-gray-600">
                  在發送換班請求前，請先確認您和目標用戶在指定時段都有排班安排。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">步驟 2：發送請求</h4>
                <p className="text-gray-600">
                  在 LINE 群組中，使用上述格式發送換班請求，確保 @ 提及目標用戶。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">步驟 3：等待確認</h4>
                <p className="text-gray-600">
                  系統會自動向目標用戶發送確認請求，您將收到請求已發送的通知。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">步驟 4：查看結果</h4>
                <p className="text-gray-600">
                  目標用戶確認後，您將收到換班結果的通知，並可在 Google Calendar 中查看更新後的排班。
                </p>
              </div>
            </div>
          </div>
          <div>
            <h3 className="text-2xl font-semibold mb-6">其他管理功能</h3>
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-3 text-blue-600">查看幫助信息</h4>
                <p className="text-gray-600 mb-3">
                  在 LINE 中發送「幫助」或「help」指令，系統會回覆可用指令與格式說明。
                </p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="font-medium mb-2">幫助信息包含：</p>
                  <ul className="list-disc pl-5 space-y-1 text-gray-600">
                    <li>換班請求格式</li>
                    <li>可用指令列表</li>
                    <li>常見問題解答</li>
                    <li>聯絡支援方式</li>
                  </ul>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-3 text-blue-600">管理員設置</h4>
                <p className="text-gray-600 mb-3">
                  在 LINE@ 管理後台可以設置特定用戶為管理員，賦予其發起換班請求的權限。
                </p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="font-medium mb-2">設置步驟：</p>
                  <ol className="list-decimal pl-5 space-y-1 text-gray-600">
                    <li>登入 LINE@ 管理後台</li>
                    <li>進入「帳號設定」{'>'}「管理員設定」</li>
                    <li>添加或移除管理員</li>
                    <li>儲存設定</li>
                  </ol>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-3 text-blue-600">排班數據查詢</h4>
                <p className="text-gray-600 mb-3">
                  管理員可以直接在 Google Calendar 中查看所有排班資訊，無需額外的查詢指令。
                </p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="font-medium mb-2">查詢方式：</p>
                  <ul className="list-disc pl-5 space-y-1 text-gray-600">
                    <li>登入 Google Calendar</li>
                    <li>選擇排班日曆</li>
                    <li>瀏覽日/週/月視圖查看排班</li>
                    <li>點擊事件查看詳細資訊</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* User Guide Section */}
      <section className="py-12 bg-gray-50 rounded-xl p-8">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">用戶操作指南</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div>
            <h3 className="text-2xl font-semibold mb-6">回應換班請求</h3>
            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <h4 className="text-lg font-medium mb-3 text-blue-600">確認請求格式</h4>
              <div className="bg-gray-100 p-4 rounded-lg text-sm mb-4">
                <p className="font-medium">[用戶 A 名稱] 希望在 [YYYY/MM/DD] [時段] [時間] 與您換班</p>
                <p>您在該時段的排班為：[用戶 B 排班詳情]</p>
                <p>用戶 A 在該時段的排班為：[用戶 A 排班詳情]</p>
                <p className="mt-2">請回覆「同意換班」或「拒絕換班」</p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">步驟 1：收到請求</h4>
                <p className="text-gray-600">
                  當有管理員向您發送換班請求時，您會收到一則包含雙方排班詳情的確認請求。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">步驟 2：確認排班</h4>
                <p className="text-gray-600">
                  檢查請求中的排班詳情，確認您是否能夠與對方交換排班。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">步驟 3：回覆請求</h4>
                <p className="text-gray-600">
                  點擊「同意換班」或「拒絕換班」按鈕，系統會根據您的選擇處理後續流程。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">步驟 4：查看結果</h4>
                <p className="text-gray-600">
                  若同意換班，系統會自動更新 Google Calendar；若拒絕，系統會通知請求者。
                </p>
              </div>
            </div>
          </div>
          <div>
            <h3 className="text-2xl font-semibold mb-6">查看排班資訊</h3>
            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <h4 className="text-lg font-medium mb-3 text-blue-600">Google Calendar 查看方式</h4>
              <p className="text-gray-600 mb-3">
                所有用戶都可以通過 Google Calendar 查看自己的排班資訊，方便安排個人時間。
              </p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-medium mb-2">查看步驟：</p>
                <ol className="list-decimal pl-5 space-y-1 text-gray-600">
                  <li>登入 Google Calendar</li>
                  <li>確認排班日曆已被添加到您的日曆列表</li>
                  <li>在日/週/月視圖中查看您的排班</li>
                  <li>點擊事件可查看詳細資訊</li>
                </ol>
              </div>
            </div>
            
            <h3 className="text-2xl font-semibold mb-6 mt-8">常見問題</h3>
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">無法收到換班請求？</h4>
                <p className="text-gray-600">
                  請確認您已加入 LINE 群組，並且在 LINE 的隱私設定中允許接收群組通知。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">換班後看不到更新？</h4>
                <p className="text-gray-600">
                  Google Calendar 可能需要一些時間同步，請嘗試重新整理頁面或等待幾分鐘。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">誤點了拒絕按鈕？</h4>
                <p className="text-gray-600">
                  請聯絡管理員重新發送換班請求，系統不支援撤回已拒絕的請求。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h4 className="text-lg font-medium mb-2 text-blue-600">需要技術支援？</h4>
                <p className="text-gray-600">
                  請在 LINE 群組中聯絡管理員，或發送「幫助」指令查看支援選項。
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 text-center">
        <h2 className="text-3xl font-bold mb-6">準備好開始使用了嗎？</h2>
        <p className="text-xl mb-8 max-w-3xl mx-auto text-gray-600">
          查看我們的部署指南，了解如何在您的環境中設置 LINE@ 機器人與 Google Calendar 整合系統。
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <a 
            href="/deployment" 
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
          >
            查看部署指南
          </a>
          <a 
            href="/features" 
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-6 rounded-lg transition-colors"
          >
            了解更多功能
          </a>
        </div>
      </section>
    </div>
  );
};

export default Guide;
