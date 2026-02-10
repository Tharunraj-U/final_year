import React, { useState, useEffect } from 'react';
import { getCodingHistory, getAllDrafts } from '../../services/api';
import './CodingHistory.css';

const CodingHistory = ({ onSelectProblem }) => {
  const [history, setHistory] = useState([]);
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('history');
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTopic, setFilterTopic] = useState('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [historyData, draftsData] = await Promise.all([
        getCodingHistory(100),
        getAllDrafts()
      ]);
      setHistory(historyData.history || []);
      setDrafts(draftsData.drafts || []);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
    setLoading(false);
  };

  const getUniqueTopics = () => {
    const topics = new Set(history.map(h => h.topic).filter(Boolean));
    return Array.from(topics);
  };

  const filteredHistory = history.filter(entry => {
    const matchesSearch = 
      entry.problem_title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.problem_id?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTopic = filterTopic === 'all' || entry.topic === filterTopic;
    return matchesSearch && matchesTopic;
  });

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getDifficultyClass = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'diff-easy';
      case 'medium': return 'diff-medium';
      case 'hard': return 'diff-hard';
      default: return '';
    }
  };

  const getScoreClass = (score) => {
    if (score >= 90) return 'score-excellent';
    if (score >= 70) return 'score-good';
    if (score >= 50) return 'score-average';
    return 'score-needs-work';
  };

  if (loading) {
    return (
      <div className="coding-history-loading">
        <div className="loading-spinner"></div>
        <p>Loading your coding history...</p>
      </div>
    );
  }

  return (
    <div className="coding-history-container">
      <div className="history-header">
        <h1>📜 Coding History</h1>
        <p>Review your past submissions and continue where you left off</p>
      </div>

      <div className="history-tabs">
        <button 
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <span>📚</span> All Submissions
          <span className="count-badge">{history.length}</span>
        </button>
        <button 
          className={`tab-btn ${activeTab === 'drafts' ? 'active' : ''}`}
          onClick={() => setActiveTab('drafts')}
        >
          <span>💾</span> Saved Drafts
          <span className="count-badge">{drafts.length}</span>
        </button>
      </div>

      {activeTab === 'history' && (
        <>
          <div className="history-filters">
            <div className="search-box">
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="Search problems..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <select 
              value={filterTopic} 
              onChange={(e) => setFilterTopic(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Topics</option>
              {getUniqueTopics().map(topic => (
                <option key={topic} value={topic}>
                  {topic?.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          <div className="history-list">
            {filteredHistory.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📭</span>
                <h3>No submissions yet</h3>
                <p>Start solving problems to build your history!</p>
              </div>
            ) : (
              filteredHistory.map((entry, index) => (
                <div 
                  key={index} 
                  className={`history-card ${entry.passed ? 'passed' : 'failed'}`}
                  onClick={() => setSelectedEntry(selectedEntry === index ? null : index)}
                >
                  <div className="card-header">
                    <div className="problem-info">
                      <h3>{entry.problem_title || entry.problem_id}</h3>
                      <div className="problem-meta">
                        <span className={`difficulty-tag ${getDifficultyClass(entry.difficulty)}`}>
                          {entry.difficulty}
                        </span>
                        <span className="topic-tag">{entry.topic?.replace('_', ' ')}</span>
                      </div>
                    </div>
                    <div className="submission-stats">
                      <div className={`score-badge ${getScoreClass(entry.score)}`}>
                        {entry.score || 0}%
                      </div>
                      <span className={`status-icon ${entry.passed ? 'passed' : 'failed'}`}>
                        {entry.passed ? '✓' : '✗'}
                      </span>
                    </div>
                  </div>

                  <div className="card-footer">
                    <span className="timestamp">
                      📅 {formatDate(entry.timestamp || entry.submitted_at)}
                    </span>
                    <span className="language-tag">
                      💻 {entry.language || 'Python'}
                    </span>
                    <button 
                      className="retry-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectProblem && onSelectProblem(entry.problem_id);
                      }}
                    >
                      Try Again →
                    </button>
                  </div>

                  {selectedEntry === index && (
                    <div className="code-preview" onClick={(e) => e.stopPropagation()}>
                      <div className="code-header">
                        <span>Your Solution</span>
                        <button 
                          className="copy-btn"
                          onClick={() => navigator.clipboard.writeText(entry.code)}
                        >
                          📋 Copy
                        </button>
                      </div>
                      <pre><code>{entry.code}</code></pre>
                      
                      {entry.time_complexity && (
                        <div className="complexity-info">
                          <span>⏱️ Time: {entry.time_complexity.detected || 'N/A'}</span>
                          <span>💾 Space: {entry.space_complexity?.detected || 'N/A'}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}

      {activeTab === 'drafts' && (
        <div className="drafts-list">
          {drafts.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">📝</span>
              <h3>No saved drafts</h3>
              <p>Your code is automatically saved as you type!</p>
            </div>
          ) : (
            drafts.map((draft, index) => (
              <div key={index} className="draft-card">
                <div className="draft-info">
                  <h3>{draft.problem_id}</h3>
                  <span className="draft-time">
                    Last edited: {formatDate(draft.updated_at)}
                  </span>
                </div>
                <div className="draft-actions">
                  <button 
                    className="continue-btn"
                    onClick={() => onSelectProblem && onSelectProblem(draft.problem_id)}
                  >
                    Continue Editing →
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default CodingHistory;
