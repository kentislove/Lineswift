import { motion } from 'framer-motion';

const Home = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <motion.section 
        className="py-16 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-blue-600">
          LINE@ 機器人與 Google Calendar 整合系統
        </h1>
        <p className="text-xl md:text-2xl mb-8 text-gray-600">
          簡化排班管理，提升團隊協作效率
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <a 
            href="/features" 
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
          >
            了解更多
          </a>
          <a 
            href="/guide" 
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-6 rounded-lg transition-colors"
          >
            查看演示
          </a>
        </div>
      </motion.section>

      {/* Core Values Section */}
      <section className="py-16">
        <h2 className="text-3xl font-bold mb-12 text-center">核心價值</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3 text-blue-600">簡化排班管理</h3>
            <p className="text-gray-600">
              透過直觀的 LINE 介面，輕鬆管理團隊排班，無需複雜的操作流程。
            </p>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3 text-blue-600">減少人工協調</h3>
            <p className="text-gray-600">
              自動化換班流程，減少管理者的協調工作，提高團隊運作效率。
            </p>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3 text-blue-600">提高資料準確性</h3>
            <p className="text-gray-600">
              自動更新 Google Calendar，確保排班資料的一致性與準確性。
            </p>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md"
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3 text-blue-600">增強團隊協作</h3>
            <p className="text-gray-600">
              透明的換班流程與確認機制，促進團隊成員間的有效溝通與協作。
            </p>
          </motion.div>
        </div>
      </section>

      {/* Feature Highlights Section */}
      <section className="py-16 bg-gray-50 rounded-xl p-8">
        <h2 className="text-3xl font-bold mb-12 text-center">功能亮點</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div className="flex flex-col md:flex-row gap-4 items-start">
            <div className="bg-blue-100 p-3 rounded-full">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-2">直觀的 LINE 介面</h3>
              <p className="text-gray-600">
                使用熟悉的 LINE 平台進行所有操作，無需學習新的系統，降低使用門檻。
              </p>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row gap-4 items-start">
            <div className="bg-blue-100 p-3 rounded-full">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-2">自動化日曆更新</h3>
              <p className="text-gray-600">
                換班確認後自動更新 Google Calendar，確保所有人都能看到最新的排班資訊。
              </p>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row gap-4 items-start">
            <div className="bg-blue-100 p-3 rounded-full">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-2">權限管理與確認機制</h3>
              <p className="text-gray-600">
                嚴格的權限控制確保只有管理員可以發起換班請求，並需經過對方確認才能生效。
              </p>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row gap-4 items-start">
            <div className="bg-blue-100 p-3 rounded-full">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-2">完整操作記錄</h3>
              <p className="text-gray-600">
                系統自動記錄所有換班操作，方便追蹤歷史變更，提高管理透明度。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-16">
        <h2 className="text-3xl font-bold mb-12 text-center">適用場景</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-600"
            whileHover={{ x: 5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3">醫療團隊排班</h3>
            <p className="text-gray-600">
              醫院、診所等醫療機構可使用本系統管理醫護人員的輪班安排，確保醫療服務的連續性。
            </p>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-600"
            whileHover={{ x: 5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3">客服中心人員調度</h3>
            <p className="text-gray-600">
              客服中心可透過本系統靈活調整客服人員的工作時段，確保服務時間的完整覆蓋。
            </p>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md border-l-4 border-orange-600"
            whileHover={{ x: 5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3">零售店面人力安排</h3>
            <p className="text-gray-600">
              零售店可使用本系統管理店員的排班，並在人員臨時無法上班時快速找到替補。
            </p>
          </motion.div>
          
          <motion.div 
            className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-600"
            whileHover={{ x: 5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h3 className="text-xl font-semibold mb-3">教育機構課表管理</h3>
            <p className="text-gray-600">
              學校、補習班等教育機構可使用本系統管理教師的課表，並在需要調課時簡化協調流程。
            </p>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-blue-600 text-white rounded-xl p-8 text-center">
        <h2 className="text-3xl font-bold mb-6">準備好提升您的排班管理了嗎？</h2>
        <p className="text-xl mb-8 max-w-3xl mx-auto">
          立即了解如何將 LINE@ 機器人與 Google Calendar 整合系統應用到您的團隊中，
          簡化排班流程，提高管理效率。
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <a 
            href="/deployment" 
            className="bg-white text-blue-600 hover:bg-gray-100 font-bold py-3 px-6 rounded-lg transition-colors"
          >
            部署指南
          </a>
          <a 
            href="/guide" 
            className="bg-blue-700 hover:bg-blue-800 text-white font-bold py-3 px-6 rounded-lg transition-colors"
          >
            操作手冊
          </a>
        </div>
      </section>
    </div>
  );
};

export default Home;
