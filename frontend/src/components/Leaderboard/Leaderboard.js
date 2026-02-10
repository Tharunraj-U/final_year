import React, { useState, useEffect } from 'react';
import { getLeaderboard } from '../../services/api';
import { Medal, X, Flame } from 'lucide-react';
import './Leaderboard.css';

const Leaderboard = ({ currentUser, onClose }) => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('all');

  useEffect(() => {
    fetchLeaderboard();
  }, [timeframe]);

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const data = await getLeaderboard(timeframe);
      setLeaderboard(data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      // Demo data if API fails
      setLeaderboard([
        { rank: 1, username: 'student_tharun', problems_solved: 42, total_score: 3850, avatar: '🦁' },
        { rank: 2, username: 'student_vijay', problems_solved: 38, total_score: 3420, avatar: '🐯' },
        { rank: 3, username: 'student_irfan', problems_solved: 35, total_score: 3180, avatar: '🐻' },
        { rank: 4, username: 'student_jai', problems_solved: 30, total_score: 2750, avatar: '🦊' },
        { rank: 5, username: 'coder123', problems_solved: 28, total_score: 2540, avatar: '🐼' },
      ]);
    }
    setLoading(false);
  };

  const getRankBadge = (rank) => {
    switch(rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return `#${rank}`;
    }
  };

  const getRankClass = (rank) => {
    if (rank === 1) return 'gold';
    if (rank === 2) return 'silver';
    if (rank === 3) return 'bronze';
    return '';
  };

  return (
    <div className="leaderboard-overlay">
      <div className="leaderboard-modal">
        <div className="leaderboard-header">
          <h2><Medal size={22} /> Leaderboard</h2>
          <button className="close-btn" onClick={onClose}><X size={20} /></button>
        </div>

        <div className="timeframe-tabs">
          <button 
            className={timeframe === 'today' ? 'active' : ''} 
            onClick={() => setTimeframe('today')}
          >
            Today
          </button>
          <button 
            className={timeframe === 'week' ? 'active' : ''} 
            onClick={() => setTimeframe('week')}
          >
            This Week
          </button>
          <button 
            className={timeframe === 'month' ? 'active' : ''} 
            onClick={() => setTimeframe('month')}
          >
            This Month
          </button>
          <button 
            className={timeframe === 'all' ? 'active' : ''} 
            onClick={() => setTimeframe('all')}
          >
            All Time
          </button>
        </div>

        <div className="leaderboard-content">
          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Loading rankings...</p>
            </div>
          ) : (
            <div className="leaderboard-list">
              {leaderboard.map((user, index) => (
                <div 
                  key={user.username} 
                  className={`leaderboard-item ${getRankClass(user.rank)} ${currentUser === user.username ? 'current-user' : ''}`}
                >
                  <div className="rank-badge">
                    {getRankBadge(user.rank)}
                  </div>
                  <div className="user-avatar">
                    {user.avatar || '👤'}
                  </div>
                  <div className="user-info">
                    <span className="username">
                      {user.username}
                      {currentUser === user.username && <span className="you-badge">You</span>}
                    </span>
                    <span className="stats">
                      {user.problems_solved} problems solved
                    </span>
                  </div>
                  <div className="user-score">
                    <span className="score-value">{user.total_score.toLocaleString()}</span>
                    <span className="score-label">points</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="leaderboard-footer">
          <p><Flame size={16} /> Keep solving problems to climb the ranks!</p>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;
