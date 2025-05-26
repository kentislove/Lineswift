import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useState } from 'react';
import Home from './pages/Home';
import Features from './pages/Features';
import Guide from './pages/Guide';
import Architecture from './pages/Architecture';
import Deployment from './pages/Deployment';
import About from './pages/About';
import './App.css';

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <header className="bg-white shadow-md">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <Link to="/" className="text-2xl font-bold text-blue-600">LINE Bot Calendar</Link>
            
            {/* Mobile menu button */}
            <button 
              className="md:hidden p-2 rounded-md text-gray-600 hover:text-blue-600 focus:outline-none" 
              onClick={toggleMenu}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-6">
              <Link to="/" className="text-gray-600 hover:text-blue-600">首頁</Link>
              <Link to="/features" className="text-gray-600 hover:text-blue-600">功能介紹</Link>
              <Link to="/guide" className="text-gray-600 hover:text-blue-600">操作指南</Link>
              <Link to="/architecture" className="text-gray-600 hover:text-blue-600">技術架構</Link>
              <Link to="/deployment" className="text-gray-600 hover:text-blue-600">部署說明</Link>
              <Link to="/about" className="text-gray-600 hover:text-blue-600">關於我們</Link>
            </nav>
          </div>
          
          {/* Mobile Navigation */}
          <div className={`md:hidden ${isMenuOpen ? 'block' : 'hidden'}`}>
            <nav className="flex flex-col space-y-2 px-4 py-2 bg-gray-50">
              <Link to="/" className="text-gray-600 hover:text-blue-600 py-2" onClick={toggleMenu}>首頁</Link>
              <Link to="/features" className="text-gray-600 hover:text-blue-600 py-2" onClick={toggleMenu}>功能介紹</Link>
              <Link to="/guide" className="text-gray-600 hover:text-blue-600 py-2" onClick={toggleMenu}>操作指南</Link>
              <Link to="/architecture" className="text-gray-600 hover:text-blue-600 py-2" onClick={toggleMenu}>技術架構</Link>
              <Link to="/deployment" className="text-gray-600 hover:text-blue-600 py-2" onClick={toggleMenu}>部署說明</Link>
              <Link to="/about" className="text-gray-600 hover:text-blue-600 py-2" onClick={toggleMenu}>關於我們</Link>
            </nav>
          </div>
        </header>
        
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/features" element={<Features />} />
            <Route path="/guide" element={<Guide />} />
            <Route path="/architecture" element={<Architecture />} />
            <Route path="/deployment" element={<Deployment />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        
        <footer className="bg-gray-800 text-white py-8">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <h3 className="text-xl font-semibold mb-4">LINE Bot Calendar</h3>
                <p className="text-gray-300">
                  簡化排班管理，提升團隊協作效率。
                </p>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-4">快速連結</h3>
                <ul className="space-y-2">
                  <li><Link to="/features" className="text-gray-300 hover:text-white">功能介紹</Link></li>
                  <li><Link to="/guide" className="text-gray-300 hover:text-white">操作指南</Link></li>
                  <li><Link to="/deployment" className="text-gray-300 hover:text-white">部署說明</Link></li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-4">聯絡我們</h3>
                <p className="text-gray-300">
                  有任何問題或建議，請隨時與我們聯繫。
                </p>
                <p className="text-gray-300 mt-2">
                  support@example.com
                </p>
              </div>
            </div>
            <div className="border-t border-gray-700 mt-8 pt-6 text-center text-gray-400">
              <p>&copy; {new Date().getFullYear()} LINE Bot Calendar. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
