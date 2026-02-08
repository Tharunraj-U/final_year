import React, { useState, useEffect } from 'react';
import { getDemoUsers } from '../../services/api';
import './ComparisonDemo.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const ComparisonDemo = () => {
  const [userRecommendations, setUserRecommendations] = useState({});
  const [userStats, setUserStats] = useState({});
  const [loading, setLoading] = useState(true);
  const demoUsers = getDemoUsers();

  useEffect(() => {
    loadAllUserData();
  }, []);

  const loadAllUserData = async () => {
    setLoading(true);
    const recommendations = {};
    const stats = {};

    for (const userId of Object.keys(demoUsers)) {
      try {
        // Fetch recommendations
        const recResponse = await fetch(`${API_BASE_URL}/recommendations?user_id=${userId}`);
        const recData = await recResponse.json();
        recommendations[userId] = recData;

        // Fetch stats
        const statsResponse = await fetch(`${API_BASE_URL}/user/${userId}/stats`);
        const statsData = await statsResponse.json();
        stats[userId] = statsData;
      } catch (error) {
        console.error(`Failed to load data for ${userId}:`, error);
        recommendations[userId] = { recommended_problems: [], learning_path: {}, strengths: {}, weaknesses: {} };
        stats[userId] = { total_submissions: 0, problems_solved: 0 };
      }
    }

    setUserRecommendations(recommendations);
    setUserStats(stats);
    setLoading(false);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return '#27ae60';
      case 'medium': return '#f39c12';
      case 'hard': return '#e74c3c';
      default: return '#666';
    }
  };

  const renderUserCard = (userId) => {
    const user = demoUsers[userId];
    const recs = userRecommendations[userId] || {};
    const stats = userStats[userId] || {};
    const problems = recs.recommended_problems || [];
    const learningPath = recs.learning_path || {};
    const strengths = recs.strengths || {};
    const weaknesses = recs.weaknesses || {};

    return (
      <div key={userId} className="user-comparison-card">
        <div className="user-header">
          <span className="user-avatar">{user.emoji}</span>
          <div className="user-info">
            <h3>{user.name}</h3>
            <p className="user-stats-summary">
              {stats.problems_solved || 0} solved • {stats.total_submissions || 0} submissions
            </p>
          </div>
        </div>

        <div className="user-metrics">
          <div className="metric">
            <span className="metric-value">{Math.round(stats.success_rate || 0)}%</span>
            <span className="metric-label">Success Rate</span>
          </div>
          <div className="metric">
            <span className="metric-value">{Math.round(stats.avg_score || 0)}</span>
            <span className="metric-label">Avg Score</span>
          </div>
        </div>

        <div className="user-analysis">
          <div className="analysis-section strengths">
            <h4>💪 Strengths</h4>
            <div className="tags">
              {(Array.isArray(strengths) ? strengths : strengths.topics || []).slice(0, 3).map((s, i) => (
                <span key={i} className="tag strength">{s}</span>
              ))}
              {(!strengths || (Array.isArray(strengths) ? strengths : strengths.topics || []).length === 0) && (
                <span className="empty-state">No data yet</span>
              )}
            </div>
          </div>

          <div className="analysis-section weaknesses">
            <h4>🎯 Areas to Improve</h4>
            <div className="tags">
              {(Array.isArray(weaknesses) ? weaknesses : weaknesses.topics || []).slice(0, 3).map((w, i) => (
                <span key={i} className="tag weakness">{w}</span>
              ))}
              {(!weaknesses || (Array.isArray(weaknesses) ? weaknesses : weaknesses.topics || []).length === 0) && (
                <span className="empty-state">No data yet</span>
              )}
            </div>
          </div>
        </div>

        <div className="learning-path-section">
          <h4>📚 Learning Path</h4>
          <p>{typeof learningPath === 'string' ? learningPath : learningPath.description || 'Start solving problems to get personalized recommendations!'}</p>
        </div>

        <div className="recommended-problems">
          <h4>🚀 Personalized Recommendations</h4>
          {problems.length > 0 ? (
            <ul>
              {problems.slice(0, 3).map((problem, i) => (
                <li key={problem.problem_id || i} className="problem-item">
                  <div className="problem-title-row">
                    <span className="problem-number">{i + 1}</span>
                    <span className="problem-title">{problem.title}</span>
                    <span 
                      className="problem-difficulty" 
                      style={{ color: getDifficultyColor(problem.difficulty) }}
                    >
                      {problem.difficulty}
                    </span>
                  </div>
                  {problem.reason && (
                    <p className="problem-reason">{problem.reason}</p>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-state">No submissions yet. Start solving problems to see personalized recommendations!</p>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="comparison-demo">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading comparison data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="comparison-demo">
      <div className="demo-header">
        <h2>🔬 Personalized Recommendations Demo</h2>
        <p>
          This demonstrates how different users get different recommendations based on their 
          <strong> individual performance</strong>, <strong>coding patterns</strong>, and <strong>learning needs</strong>.
        </p>
        <div className="demo-explanation">
          <div className="explanation-item">
            <span className="icon">👤</span>
            <div>
              <strong>Different Users</strong>
              <p>Each user has their own submission history and performance profile</p>
            </div>
          </div>
          <div className="explanation-item">
            <span className="icon">📊</span>
            <div>
              <strong>Different Analysis</strong>
              <p>AI analyzes code quality, complexity, algorithms used, and test failures</p>
            </div>
          </div>
          <div className="explanation-item">
            <span className="icon">🎯</span>
            <div>
              <strong>Different Recommendations</strong>
              <p>Problems are recommended based on individual weaknesses and skill level</p>
            </div>
          </div>
        </div>
      </div>

      <div className="comparison-grid">
        {Object.keys(demoUsers).map(userId => renderUserCard(userId))}
      </div>

      <div className="demo-footer">
        <p>
          💡 <strong>Try it yourself:</strong> Switch between users in the header, solve problems differently, 
          and see how the AI adapts recommendations for each user!
        </p>
        <button className="refresh-btn" onClick={loadAllUserData}>
          🔄 Refresh Comparison
        </button>
      </div>
    </div>
  );
};

export default ComparisonDemo;
