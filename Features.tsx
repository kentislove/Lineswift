import { motion } from 'framer-motion';

const Features = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header Section */}
      <motion.section 
        className="py-12 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold mb-4 text-blue-600">功能介紹</h1>
        <p className="text-xl mb-8 text-gray-600 max-w-3xl mx-auto">
          LINE@ 機器人與 Google Calendar 整合系統提供全方位的排班管理功能，
          從換班請求到日曆同步，一應俱全。
        </p>
      </motion.section>

      {/* Exchange Request Section */}
      <section className="py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-3xl font-bold mb-6 text-blue-600">換班請求與確認流程</h2>
            <p className="text-gray-600 mb-4">
              系統提供直觀的換班請求流程，管理員可以在 LINE 中發送格式化的換班請求，
              系統會自動處理並向目標用戶發送確認請求。
            </p>
            <ul className="space-y-3">
              <li className="flex items-start">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">1</span>
                <span className="text-gray-700">管理員發送換班請求，格式：「我希望在YYYYMMDD早上08:00跟你換班 @用戶名」</span>
              </li>
              <li className="flex items-start">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">2</span>
                <span className="text-gray-700">系統檢查雙方在指定時段是否都有排班</span>
              </li>
              <li className="flex items-start">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">3</span>
                <span className="text-gray-700">系統向目標用戶發送確認請求，顯示雙方排班詳情</span>
              </li>
              <li className="flex items-start">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">4</span>
                <span className="text-gray-700">目標用戶可選擇「同意換班」或「拒絕換班」</span>
              </li>
              <li className="flex items-start">
                <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-1">5</span>
                <span className="text-gray-700">若同意，系統自動更新 Google Calendar；若拒絕，通知請求者</span>
              </li>
            </ul>
          </div>
          <div>
            <img 
              src="/images/shift_exchange_flow.png" 
              alt="換班流程圖" 
              className="w-full h-auto rounded-lg shadow-md"
            />
            <p className="text-center text-gray-500 mt-2">換班請求與確認流程</p>
          </div>
        </div>
      </section>

      {/* Admin Features Section */}
      <section className="py-12 bg-gray-50 rounded-xl p-8">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">管理員權限管理</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="bg-gray-100 p-4 rounded-lg h-80 flex items-center justify-center order-2 md:order-1">
            <div className="text-center text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <p>管理員權限示意圖</p>
              <p className="text-sm">(將在視覺設計階段加入)</p>
            </div>
          </div>
          <div className="order-1 md:order-2">
            <p className="text-gray-600 mb-6">
              系統提供嚴格的權限控制，確保只有被授權的管理員可以發起換班請求，
              防止未授權的操作影響排班安排。
            </p>
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">管理員設置</h3>
                <p className="text-gray-600">
                  在 LINE@ 管理後台可以設置特定用戶為管理員，賦予其發起換班請求的權限。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">權限驗證</h3>
                <p className="text-gray-600">
                  系統會在每次換班請求時自動驗證發送者的管理員身份，確保安全性。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-2 text-blue-600">操作記錄</h3>
                <p className="text-gray-600">
                  所有管理操作都會被記錄，方便後續審計與問題排查。
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Google Calendar Integration Section */}
      <section className="py-12">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">Google Calendar 整合</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div>
            <p className="text-gray-600 mb-6">
              系統與 Google Calendar 深度整合，實現排班資料的自動同步與更新，
              確保所有團隊成員都能看到最新的排班安排。
            </p>
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-600">
                <h3 className="text-lg font-semibold mb-2">資料同步機制</h3>
                <p className="text-gray-600">
                  換班確認後，系統會自動更新 Google Calendar 上的排班資料，
                  確保日曆顯示的是最新的排班安排。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-600">
                <h3 className="text-lg font-semibold mb-2">事件格式標準化</h3>
                <p className="text-gray-600">
                  系統使用標準化的事件格式，包含排班人員、時間與詳細資訊，
                  便於團隊成員快速了解排班情況。
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-600">
                <h3 className="text-lg font-semibold mb-2">歷史記錄追蹤</h3>
                <p className="text-gray-600">
                  系統會在日曆事件中記錄換班歷史，方便追蹤排班變更的來龍去脈。
                </p>
              </div>
            </div>
          </div>
          <div className="bg-gray-100 p-4 rounded-lg h-80 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p>Google Calendar 整合示意圖</p>
              <p className="text-sm">(將在視覺設計階段加入)</p>
            </div>
          </div>
        </div>
      </section>

      {/* Automated Scheduling Section */}
      <section className="py-12 bg-gray-50 rounded-xl p-8">
        <h2 className="text-3xl font-bold mb-8 text-blue-600">自動化排班管理</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <div className="bg-blue-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-3">自動檢查排班衝突</h3>
            <p className="text-gray-600">
              系統會自動檢查換班請求是否會導致排班衝突，確保排班安排的合理性。
            </p>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <div className="bg-blue-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-3">自動通知機制</h3>
            <p className="text-gray-600">
              系統會自動向相關人員發送換班請求、確認結果等通知，確保信息及時傳達。
            </p>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <div className="bg-blue-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-3">自動同步更新</h3>
            <p className="text-gray-600">
              換班確認後，系統會自動更新 Google Calendar，無需人工干預，減少錯誤風險。
            </p>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 text-center">
        <h2 className="text-3xl font-bold mb-6">想了解更多功能細節？</h2>
        <p className="text-xl mb-8 max-w-3xl mx-auto text-gray-600">
          查看我們的操作指南，了解如何充分利用 LINE@ 機器人與 Google Calendar 整合系統的所有功能。
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <a 
            href="/guide" 
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
          >
            查看操作指南
          </a>
          <a 
            href="/architecture" 
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-6 rounded-lg transition-colors"
          >
            了解技術架構
          </a>
        </div>
      </section>
    </div>
  );
};

export default Features;
