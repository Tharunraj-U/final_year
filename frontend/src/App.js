import React, { useState, useEffect } from 'react';
import './App.css';

// Components
import Header from './components/Header/Header';
import ProblemList from './components/ProblemList/ProblemList';
import CodeEditor from './components/CodeEditor/CodeEditor';
import AIRecommendations from './components/AIRecommendations/AIRecommendations';
import { ComparisonDemo, CustomProblem } from './components';
import Auth from './components/Auth/Auth';
import Achievements from './components/Achievements/Achievements';
import Leaderboard from './components/Leaderboard/Leaderboard';
import StreakCounter from './components/StreakCounter/StreakCounter';
import StatsDashboard from './components/StatsDashboard/StatsDashboard';
import { getCurrentUser, logout, getDetailedStats, getUserStreak, getUserAchievementStats } from './services/api';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [currentView, setCurrentView] = useState('problems'); // 'problems', 'editor', 'recommendations', 'comparison', 'custom', 'dashboard'
  const [selectedProblemId, setSelectedProblemId] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [darkMode, setDarkMode] = useState(false);
  const [showAchievements, setShowAchievements] = useState(false);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [userStats, setUserStats] = useState(null);
  const [userStreak, setUserStreak] = useState({ streak: 0 });
  const [achievementStats, setAchievementStats] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const user = getCurrentUser();
    if (user) {
      setCurrentUser(user);
    }
    // Check for dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.body.classList.add('dark-mode');
    }
  }, []);

  useEffect(() => {
    if (currentUser) {
      fetchUserData();
    }
  }, [currentUser, refreshTrigger]);

  const fetchUserData = async () => {
    try {
      const [stats, streak, achievements] = await Promise.all([
        getDetailedStats(),
        getUserStreak(),
        getUserAchievementStats()
      ]);
      setUserStats(stats);
      setUserStreak(streak);
      setAchievementStats(achievements);
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', String(newMode));
    document.body.classList.toggle('dark-mode', newMode);
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setRefreshTrigger(prev => prev + 1);
  };

  const handleLogout = () => {
    logout();
    setCurrentUser(null);
    setCurrentView('problems');
  };

  const handleSelectProblem = (problemId) => {
    setSelectedProblemId(problemId);
    setCurrentView('editor');
  };

  const handleBack = () => {
    setCurrentView('problems');
    setSelectedProblemId(null);
  };

  const handleSubmitSuccess = (data) => {
    // Trigger a refresh of recommendations when a problem is submitted
    setRefreshTrigger(prev => prev + 1);
  };

  const handleNavClick = (view) => {
    setCurrentView(view);
    if (view !== 'editor') {
      setSelectedProblemId(null);
    }
  };

  const handleUserChange = (userId) => {
    // Refresh data when user changes
    setRefreshTrigger(prev => prev + 1);
  };

  // Show login page if not authenticated
  if (!currentUser) {
    return <Auth onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      <Header 
        currentView={currentView}
        onNavClick={handleNavClick}
        onUserChange={handleUserChange}
        currentUser={currentUser}
        onLogout={handleLogout}
        darkMode={darkMode}
        onToggleDarkMode={toggleDarkMode}
        onShowAchievements={() => setShowAchievements(true)}
        onShowLeaderboard={() => setShowLeaderboard(true)}
        streak={userStreak?.streak || 0}
      />
      
      <main className="main-content">
        {currentView === 'problems' && (
          <ProblemList onSelectProblem={handleSelectProblem} />
        )}
        
        {currentView === 'editor' && selectedProblemId && (
          <CodeEditor
            problemId={selectedProblemId}
            onBack={handleBack}
            onSubmitSuccess={handleSubmitSuccess}
            onSelectProblem={handleSelectProblem}
          />
        )}
        
        {currentView === 'recommendations' && (
          <AIRecommendations
            onSelectProblem={handleSelectProblem}
            refreshTrigger={refreshTrigger}
          />
        )}

        {currentView === 'comparison' && (
          <ComparisonDemo />
        )}

        {currentView === 'custom' && (
          <CustomProblem 
            onBack={() => setCurrentView('problems')}
            onProblemCreated={() => {
              setRefreshTrigger(prev => prev + 1);
              setCurrentView('problems');
            }}
          />
        )}

        {currentView === 'dashboard' && (
          <div className="dashboard-view">
            <StreakCounter streak={userStreak?.streak || 0} />
            <StatsDashboard stats={userStats} />
          </div>
        )}
      </main>

      {/* Modals */}
      {showAchievements && (
        <Achievements 
          stats={achievementStats} 
          onClose={() => setShowAchievements(false)} 
        />
      )}

      {showLeaderboard && (
        <Leaderboard 
          currentUser={currentUser?.user_id}
          onClose={() => setShowLeaderboard(false)} 
        />
      )}
    </div>
  );
}

export default App;
