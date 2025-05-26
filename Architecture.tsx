import { motion } from 'framer-motion';

const Architecture = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header Section */}
      <motion.section 
        className="py-12 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold mb-4 text-blue-600">技術架構</h1>
        <p className="text-xl mb-8 text-gray-600 max-w-3xl mx-auto">
          深入了解 LINE@ 機器人與 Google Calendar 整合系統的技術架構、
          模組設計與 API 整合流程。
        </p>
      </motion.section>

      {/* System Architecture Section */}
      <section className="py-12">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">系統架構概覽</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div>
            <p className="text-gray-600 mb-6">
              本系統採用模組化設計，主要由 FastAPI 後端服務、LINE Bot 模組、用戶管理模組與
              日曆管理模組組成，通過 API 整合實現完整的排班管理功能。
            </p>
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">前後端分離設計</h3>
                <p className="text-gray-600">
                  系統採用前後端分離架構，後端使用 FastAPI 提供 RESTful API，
                  前端通過 LINE 介面與用戶互動，確保系統的靈活性與可擴展性。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">API 整合流程</h3>
                <p className="text-gray-600">
                  系統整合 LINE Messaging API 與 Google Calendar API，
                  實現訊息處理與日曆資料同步，確保資料的一致性與即時性。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">資料庫設計</h3>
                <p className="text-gray-600">
                  使用 SQLite 資料庫儲存用戶資訊與操作記錄，確保系統在輕量級環境下也能高效運行。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">安全性考量</h3>
                <p className="text-gray-600">
                  系統實現嚴格的權限控制與資料加密，確保用戶資訊與排班資料的安全性。
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <img 
              src="/images/system_architecture.png" 
              alt="系統架構圖" 
              className="w-full h-auto rounded-lg"
            />
            <p className="text-center text-gray-500 mt-2">LINE@ 機器人與 Google Calendar 整合系統架構</p>
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-12 bg-gray-50 rounded-xl p-8">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">技術堆疊</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3 text-blue-600">後端框架</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                FastAPI
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                Uvicorn
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                Python 3.8+
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                SQLite
              </li>
            </ul>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3 text-blue-600">LINE 整合</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                LINE Messaging API
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                Webhook
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                line-bot-sdk
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                Template Messages
              </li>
            </ul>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3 text-blue-600">Google 整合</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                Google Calendar API
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                OAuth 2.0
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                Service Account
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                google-api-python-client
              </li>
            </ul>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3 text-blue-600">部署環境</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                Render Professional Plan
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                GitHub 整合
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                自動部署
              </li>
              <li className="flex items-center">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-2">✓</span>
                HTTPS 安全連接
              </li>
            </ul>
          </motion.div>
        </div>
      </section>

      {/* Module Design Section */}
      <section className="py-12">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">模組設計</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-blue-600">LINE Bot 模組</h3>
            <p className="text-gray-600 mb-4">
              負責處理 LINE Messaging API 的整合，包含訊息解析、回覆生成與 Webhook 處理。
            </p>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="font-medium mb-2">主要功能：</p>
              <ul className="list-disc pl-5 space-y-1 text-gray-600">
                <li>處理 Webhook 回調</li>
                <li>解析換班請求訊息</li>
                <li>生成確認請求</li>
                <li>處理用戶回覆</li>
                <li>發送通知訊息</li>
              </ul>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-blue-600">用戶管理模組</h3>
            <p className="text-gray-600 mb-4">
              負責處理用戶資訊與權限管理，確保只有授權用戶可以執行特定操作。
            </p>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="font-medium mb-2">主要功能：</p>
              <ul className="list-disc pl-5 space-y-1 text-gray-600">
                <li>用戶資訊儲存</li>
                <li>管理員權限驗證</li>
                <li>用戶名稱與 ID 查詢</li>
                <li>用戶存在性檢查</li>
                <li>管理員列表管理</li>
              </ul>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-blue-600">日曆管理模組</h3>
            <p className="text-gray-600 mb-4">
              負責處理 Google Calendar API 的整合，包含排班查詢、更新與同步。
            </p>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="font-medium mb-2">主要功能：</p>
              <ul className="list-disc pl-5 space-y-1 text-gray-600">
                <li>日曆事件查詢</li>
                <li>排班資訊獲取</li>
                <li>排班交換處理</li>
                <li>新排班創建</li>
                <li>排班刪除</li>
                <li>操作記錄追蹤</li>
              </ul>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-blue-600">核心業務邏輯</h3>
            <p className="text-gray-600 mb-4">
              負責協調各模組的運作，實現完整的換班流程與業務邏輯。
            </p>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="font-medium mb-2">主要功能：</p>
              <ul className="list-disc pl-5 space-y-1 text-gray-600">
                <li>換班請求處理</li>
                <li>排班衝突檢查</li>
                <li>確認流程管理</li>
                <li>日曆更新協調</li>
                <li>通知發送管理</li>
                <li>錯誤處理與恢復</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* API Integration Section */}
      <section className="py-12 bg-gray-50 rounded-xl p-8">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">API 整合流程</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <img 
              src="/images/google_calendar_integration.png" 
              alt="Google Calendar 整合示意圖" 
              className="w-full h-auto rounded-lg"
            />
            <p className="text-center text-gray-500 mt-2">LINE 訊息與 Google Calendar 整合流程</p>
          </div>
          <div className="order-1 md:order-2">
            <p className="text-gray-600 mb-6">
              系統通過 API 整合實現 LINE 訊息處理與 Google Calendar 資料同步，
              確保用戶可以通過熟悉的 LINE 介面管理排班，同時保持日曆資料的一致性。
            </p>
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">LINE Messaging API</h3>
                <p className="text-gray-600">
                  系統使用 LINE Messaging API 接收用戶訊息與事件，並通過 Webhook 處理這些請求，
                  實現即時的用戶互動。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">Google Calendar API</h3>
                <p className="text-gray-600">
                  系統使用 Google Calendar API 查詢與更新排班資料，通過服務帳號實現安全的 API 存取，
                  確保資料的準確性與即時性。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">資料流程</h3>
                <p className="text-gray-600">
                  用戶訊息 → LINE Webhook → 訊息解析 → 業務邏輯處理 → 
                  Google Calendar 操作 → 結果通知 → 用戶反饋
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 text-center">
        <h2 className="text-3xl font-bold mb-6">想了解如何部署此系統？</h2>
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
            href="/guide" 
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-6 rounded-lg transition-colors"
          >
            返回操作指南
          </a>
        </div>
      </section>
    </div>
  );
};

export default Architecture;
