import React from 'react';
import './Sidebar.css';
import { usePage, PAGES } from '../context/PageContext';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { activePage, setActivePage } = usePage();
  const { logout, user } = useAuth();

  const handleNavClick = (page) => {
    setActivePage(page);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="sidebar">
      <div className="logo">
        <span>✦</span>
      </div>
      <nav className="sidebar-nav">
        <button 
          className={`sidebar-btn ${activePage === PAGES.CHAT ? 'active' : ''}`} 
          title="Chat"
          onClick={() => handleNavClick(PAGES.CHAT)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </button>
        <button 
          className={`sidebar-btn ${activePage === PAGES.DOCUMENTS ? 'active' : ''}`} 
          title="Documents"
          onClick={() => handleNavClick(PAGES.DOCUMENTS)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        </button>
        <button 
          className={`sidebar-btn ${activePage === PAGES.UPLOAD ? 'active' : ''}`} 
          title="Upload"
          onClick={() => handleNavClick(PAGES.UPLOAD)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </button>
        <button 
          className={`sidebar-btn ${activePage === PAGES.MONITORING ? 'active' : ''}`} 
          title="Monitoring"
          onClick={() => handleNavClick(PAGES.MONITORING)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 12h4l3-8 4 16 3-8h4"></path>
            <circle cx="12" cy="4" r="2"></circle>
            <circle cx="12" cy="20" r="2"></circle>
          </svg>
        </button>
        <button 
          className={`sidebar-btn ${activePage === PAGES.FEEDBACK ? 'active' : ''}`} 
          title="Feedback Analytics"
          onClick={() => handleNavClick(PAGES.FEEDBACK)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
          </svg>
        </button>
      </nav>
      <div className="sidebar-footer">
        <div className="user-info">
          <span className="username">{user?.username}</span>
        </div>
        <button className="sidebar-btn logout-btn" title="Logout" onClick={handleLogout}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Sidebar; 