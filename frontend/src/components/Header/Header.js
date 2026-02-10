import React, { useState } from 'react';
import { getDemoUsers } from '../../services/api';
import { Code2, LayoutDashboard, History, PlusCircle, Bot, Trophy, Medal, Sun, Moon, LogOut, User, ChevronDown } from 'lucide-react';
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

  // Check if user has a Google profile picture
  const hasGooglePhoto = () => {
    return currentUser?.picture && currentUser.picture.startsWith('http');
  };

  const getUserEmoji = () => {
    if (currentUser && demoUsers[currentUser.user_id]) {
      return demoUsers[currentUser.user_id].emoji;
    }
    return '👤';
  };

  const getUserAvatar = () => {
    if (hasGooglePhoto()) {
      return (
        <img 
          src={currentUser.picture} 
          alt="Profile" 
          className="user-avatar"
          referrerPolicy="no-referrer"
        />
      );
    }
    return <span className="user-emoji">{getUserEmoji()}</span>;
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
          <Code2 className="logo-icon" size={28} />
          <h1>CodeMaster AI</h1>
        </div>
        
        <nav className="nav-menu">
          <button 
            className={`nav-item ${currentView === 'problems' ? 'active' : ''}`}
            onClick={() => onNavClick('problems')}
          >
            <Code2 size={18} />
            <span>Problems</span>
          </button>
          <button 
            className={`nav-item ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => onNavClick('dashboard')}
          >
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </button>
          <button 
            className={`nav-item ${currentView === 'history' ? 'active' : ''}`}
            onClick={() => onNavClick('history')}
          >
            <History size={18} />
            <span>History</span>
          </button>
          <button 
            className={`nav-item ${currentView === 'custom' ? 'active' : ''}`}
            onClick={() => onNavClick('custom')}
          >
            <PlusCircle size={18} />
            <span>Create</span>
          </button>
          <button 
            className={`nav-item ${currentView === 'recommendations' ? 'active' : ''}`}
            onClick={() => onNavClick('recommendations')}
          >
            <Bot size={18} />
            <span>AI Insights</span>
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
            <Medal size={20} />
          </button>
          <button 
            className="action-btn" 
            onClick={onShowAchievements}
            title="Achievements"
          >
            <Trophy size={20} />
          </button>
          <button 
            className="action-btn dark-mode-toggle" 
            onClick={onToggleDarkMode}
            title={darkMode ? 'Light Mode' : 'Dark Mode'}
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>

        <div className="user-section">
          <div 
            className="user-profile" 
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            {getUserAvatar()}
            <span className="user-name">{getUserName()}</span>
            <ChevronDown size={14} className="dropdown-arrow" />
          </div>
          
          {showUserMenu && (
            <div className="user-menu">
              <div className="user-menu-header">
                <span><User size={14} /> {getUserName()}</span>
                <small>{currentUser?.email || currentUser?.user_id}</small>
              </div>
              <div className="user-menu-divider"></div>
              <div 
                className="user-menu-item"
                onClick={() => { onNavClick('dashboard'); setShowUserMenu(false); }}
              >
                <LayoutDashboard size={16} />
                <span>My Stats</span>
              </div>
              <div 
                className="user-menu-item"
                onClick={() => { onShowAchievements(); setShowUserMenu(false); }}
              >
                <Trophy size={16} />
                <span>Achievements</span>
              </div>
              <div className="user-menu-divider"></div>
              <div 
                className="user-menu-item logout"
                onClick={handleLogout}
              >
                <LogOut size={16} />
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
