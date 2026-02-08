import React, { useState } from 'react';
import { getDemoUsers } from '../../services/api';
import './Header.css';

const Header = ({ 
  currentView, 
  onNavClick, 
  onUserChange, 
  currentUser, 
  onLogout,
  darkMode,
  onToggleDarkMode,
  onShowAchievements,
  onShowLeaderboard,
  streak = 0
}) => {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const demoUsers = getDemoUsers();

  const getUserEmoji = () => {
    if (currentUser && demoUsers[currentUser.user_id]) {
      return demoUsers[currentUser.user_id].emoji;
    }
    return '👤';
  };

  const getUserName = () => {
    if (currentUser) {
      return currentUser.name || currentUser.user_id;
    }
    return 'Guest';
  };

  const handleLogout = () => {
    setShowUserMenu(false);
    onLogout();
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo" onClick={() => onNavClick('problems')}>
          <span className="logo-icon">🧠</span>
          <h1>CodeMaster AI</h1>
        </div>
        
        <nav className="nav-menu">
          <button 
            className={`nav-item ${currentView === 'problems' ? 'active' : ''}`}
            onClick={() => onNavClick('problems')}
          >
            📝 Problems
          </button>
          <button 
            className={`nav-item ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => onNavClick('dashboard')}
          >
            📊 Dashboard
          </button>
          <button 
            className={`nav-item ${currentView === 'custom' ? 'active' : ''}`}
            onClick={() => onNavClick('custom')}
          >
            ➕ Create
          </button>
          <button 
            className={`nav-item ${currentView === 'recommendations' ? 'active' : ''}`}
            onClick={() => onNavClick('recommendations')}
          >
            🤖 AI Insights
          </button>
        </nav>

        <div className="header-actions">
          {/* Streak indicator */}
          {streak > 0 && (
            <div className="streak-badge" title={`${streak} day streak!`}>
              <span className="streak-fire">🔥</span>
              <span className="streak-count">{streak}</span>
            </div>
          )}

          {/* Quick action buttons */}
          <button 
            className="action-btn" 
            onClick={onShowLeaderboard}
            title="Leaderboard"
          >
            🏅
          </button>
          <button 
            className="action-btn" 
            onClick={onShowAchievements}
            title="Achievements"
          >
            🏆
          </button>
          <button 
            className="action-btn dark-mode-toggle" 
            onClick={onToggleDarkMode}
            title={darkMode ? 'Light Mode' : 'Dark Mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>

        <div className="user-section">
          <div 
            className="user-profile" 
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <span className="user-emoji">{getUserEmoji()}</span>
            <span className="user-name">{getUserName()}</span>
            <span className="dropdown-arrow">▼</span>
          </div>
          
          {showUserMenu && (
            <div className="user-menu">
              <div className="user-menu-header">
                <span>👤 {getUserName()}</span>
                <small>{currentUser?.email || currentUser?.user_id}</small>
              </div>
              <div className="user-menu-divider"></div>
              <div 
                className="user-menu-item"
                onClick={() => { onNavClick('dashboard'); setShowUserMenu(false); }}
              >
                <span className="user-emoji">📊</span>
                <span>My Stats</span>
              </div>
              <div 
                className="user-menu-item"
                onClick={() => { onShowAchievements(); setShowUserMenu(false); }}
              >
                <span className="user-emoji">🏆</span>
                <span>Achievements</span>
              </div>
              <div className="user-menu-divider"></div>
              <div 
                className="user-menu-item logout"
                onClick={handleLogout}
              >
                <span className="user-emoji">🚪</span>
                <span>Logout</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
