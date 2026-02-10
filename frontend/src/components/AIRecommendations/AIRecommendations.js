import React, { useState, useEffect } from 'react';
import { getRecommendations, getUserStats } from '../../services/api';
import { BarChart3, Bot, Dumbbell, TrendingUp, Target, Clock, BookOpen, ArrowRight } from 'lucide-react';
import './AIRecommendations.css';

const AIRecommendations = ({ onSelectProblem, refreshTrigger }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [recsData, statsData] = await Promise.all([
        getRecommendations(),
        getUserStats()
      ]);
      
      setRecommendations(recsData);
      setStats(statsData);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
      setError('Failed to load recommendations. Make sure the backend is running.');
    }
    
    setLoading(false);
  };

  const getDifficultyClass = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'difficulty-easy';
      case 'medium': return 'difficulty-medium';
      case 'hard': return 'difficulty-hard';
      default: return '';
    }
  };

  if (loading) {
    return (
      <div className="ai-recommendations loading">
        <div className="loading-container">
          <div className="loading-spinner-circle"></div>
          <p>Loading recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ai-recommendations error">
        <p>{error}</p>
        <button onClick={loadData}>Retry</button>
      </div>
    );
  }

  return (
    <div className="ai-recommendations">
      {/* User Stats */}
      {stats && (
        <div className="stats-section">
          <h3><BarChart3 size={20} /> Your Progress</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-value">{stats.total_submissions || 0}</span>
              <span className="stat-label">Problems Attempted</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{stats.problems_solved || 0}</span>
              <span className="stat-label">Problems Solved</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{stats.success_rate || 0}%</span>
              <span className="stat-label">Success Rate</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{stats.average_score || 0}</span>
              <span className="stat-label">Avg Score</span>
            </div>
          </div>

          {stats.topics_breakdown && Object.keys(stats.topics_breakdown).length > 0 && (
            <div className="topics-breakdown">
              <h4>Topics Practiced</h4>
              <div className="topics-list">
                {Object.entries(stats.topics_breakdown).map(([topic, count]) => (
                  <span key={topic} className="topic-tag">
                    {topic.replace('_', ' ')}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* AI Recommendations */}
      {recommendations && (
        <div className="recommendations-section">
          <h3><Bot size={20} /> AI Recommendations</h3>
          
          {recommendations.message && (
            <div className="ai-message">
              <p>{recommendations.message}</p>
            </div>
          )}

          {recommendations.analysis && (
            <div className="ai-analysis-summary">
              <h4>Performance Analysis</h4>
              <p>{recommendations.analysis}</p>
              
              {recommendations.strengths && (
                <div className="strengths">
                  <h5><Dumbbell size={16} /> Strengths</h5>
                  {Array.isArray(recommendations.strengths) ? (
                    <ul>
                      {recommendations.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  ) : (
                    <div className="strength-details">
                      {recommendations.strengths.topics && recommendations.strengths.topics.length > 0 && (
                        <p><strong>Topics:</strong> {recommendations.strengths.topics.join(', ')}</p>
                      )}
                      {recommendations.strengths.algorithms && recommendations.strengths.algorithms.length > 0 && (
                        <p><strong>Algorithms:</strong> {recommendations.strengths.algorithms.join(', ')}</p>
                      )}
                      {recommendations.strengths.patterns && recommendations.strengths.patterns.length > 0 && (
                        <p><strong>Patterns:</strong> {recommendations.strengths.patterns.join(', ')}</p>
                      )}
                    </div>
                  )}
                </div>
              )}
              
              {recommendations.weaknesses && (
                <div className="weaknesses">
                  <h5><TrendingUp size={16} /> Areas to Improve</h5>
                  {Array.isArray(recommendations.weaknesses) ? (
                    <ul>
                      {recommendations.weaknesses.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  ) : (
                    <div className="weakness-details">
                      {recommendations.weaknesses.topics && recommendations.weaknesses.topics.length > 0 && (
                        <p><strong>Topics:</strong> {recommendations.weaknesses.topics.join(', ')}</p>
                      )}
                      {recommendations.weaknesses.algorithms && recommendations.weaknesses.algorithms.length > 0 && (
                        <p><strong>Algorithms:</strong> {recommendations.weaknesses.algorithms.join(', ')}</p>
                      )}
                      {recommendations.weaknesses.patterns && recommendations.weaknesses.patterns.length > 0 && (
                        <p><strong>Patterns:</strong> {recommendations.weaknesses.patterns.join(', ')}</p>
                      )}
                    </div>
                  )}
                </div>
              )}

              {recommendations.next_steps && recommendations.next_steps.length > 0 && (
                <div className="next-steps">
                  <h5><Target size={16} /> Next Steps</h5>
                  <ol>
                    {recommendations.next_steps.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ol>
                </div>
              )}

              {recommendations.estimated_time_to_next_level && (
                <div className="time-estimate">
                  <h5><Clock size={16} /> Time to Next Level</h5>
                  <p>{recommendations.estimated_time_to_next_level}</p>
                </div>
              )}
            </div>
          )}

          {recommendations.learning_path && (
            <div className="learning-path">
              <h4><BookOpen size={18} /> Suggested Learning Path</h4>
              {typeof recommendations.learning_path === 'string' ? (
                <p>{recommendations.learning_path}</p>
              ) : (
                <>
                  {recommendations.learning_path.current_level && (
                    <p className="current-level">
                      <strong>Current Level:</strong> {recommendations.learning_path.current_level}
                    </p>
                  )}
                  {recommendations.learning_path.description && (
                    <p>{recommendations.learning_path.description}</p>
                  )}
                  {recommendations.learning_path.focus_areas && recommendations.learning_path.focus_areas.length > 0 && (
                    <div className="focus-areas">
                      <strong>Focus Areas:</strong>
                      <ul>
                        {recommendations.learning_path.focus_areas.map((area, i) => (
                          <li key={i}>{area}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {recommendations.recommended_problems && recommendations.recommended_problems.length > 0 && (
            <div className="recommended-problems">
              <h4>🎯 Recommended Problems</h4>
              {recommendations.recommended_problems.map((problem, idx) => (
                <div
                  key={problem.problem_id || idx}
                  className="recommended-problem"
                  onClick={() => onSelectProblem(problem.problem_id)}
                >
                  <div className="problem-info">
                    <span className="problem-title">{problem.title}</span>
                    <span className={`difficulty-badge ${getDifficultyClass(problem.difficulty)}`}>
                      {problem.difficulty}
                    </span>
                  </div>
                  <span className="problem-topic">{problem.topic?.replace('_', ' ')}</span>
                  {problem.reason && (
                    <p className="problem-reason">{problem.reason}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {!recommendations?.recommended_problems?.length && !stats?.total_submissions && (
        <div className="empty-state">
          <h3>👋 Welcome!</h3>
          <p>Start solving problems to get personalized AI recommendations based on your performance.</p>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;
