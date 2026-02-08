import React, { useState, useEffect } from 'react';
import { getProblems, getTopics } from '../../services/api';
import './ProblemList.css';

// Topic icons and display names
const TOPIC_CONFIG = {
  arrays: { icon: '📊', name: 'Arrays', color: '#3498db' },
  strings: { icon: '🔤', name: 'Strings', color: '#9b59b6' },
  sliding_window: { icon: '🪟', name: 'Sliding Window', color: '#1abc9c' },
  two_pointers: { icon: '👆', name: 'Two Pointers', color: '#e67e22' },
  binary_search: { icon: '🔍', name: 'Binary Search', color: '#2ecc71' },
  linked_lists: { icon: '🔗', name: 'Linked Lists', color: '#e74c3c' },
  trees: { icon: '🌳', name: 'Trees', color: '#27ae60' },
  graphs: { icon: '🕸️', name: 'Graphs', color: '#8e44ad' },
  dynamic_programming: { icon: '📈', name: 'Dynamic Programming', color: '#f39c12' },
  backtracking: { icon: '↩️', name: 'Backtracking', color: '#c0392b' },
  greedy: { icon: '🎯', name: 'Greedy', color: '#16a085' },
  stacks: { icon: '📚', name: 'Stacks', color: '#2980b9' },
  hashing: { icon: '#️⃣', name: 'Hashing', color: '#8e44ad' },
  heap: { icon: '⛰️', name: 'Heap / Priority Queue', color: '#d35400' },
  bit_manipulation: { icon: '🔢', name: 'Bit Manipulation', color: '#7f8c8d' },
};

const ProblemList = ({ onSelectProblem }) => {
  const [problems, setProblems] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [expandedTopics, setExpandedTopics] = useState({});
  const [viewMode, setViewMode] = useState('category');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadTopics();
    loadProblems();
  }, []);

  useEffect(() => {
    loadProblems();
  }, [selectedDifficulty]);

  const loadTopics = async () => {
    try {
      const data = await getTopics();
      setTopics(data.topics || []);
      const defaultExpanded = {};
      (data.topics || []).slice(0, 3).forEach(t => {
        defaultExpanded[t] = true;
      });
      setExpandedTopics(defaultExpanded);
    } catch (error) {
      console.error('Failed to load topics:', error);
    }
  };

  const loadProblems = async () => {
    setLoading(true);
    try {
      const data = await getProblems(null, selectedDifficulty || null);
      setProblems(data.problems || []);
    } catch (error) {
      console.error('Failed to load problems:', error);
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

  const toggleTopic = (topic) => {
    setExpandedTopics(prev => ({ ...prev, [topic]: !prev[topic] }));
  };

  const expandAll = () => {
    const allExpanded = {};
    topics.forEach(t => { allExpanded[t] = true; });
    setExpandedTopics(allExpanded);
  };

  const collapseAll = () => setExpandedTopics({});

  const filteredProblems = searchQuery
    ? problems.filter(p => 
        p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.topic?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : problems;

  const filteredGrouped = filteredProblems.reduce((acc, problem) => {
    const topic = problem.topic || 'other';
    if (!acc[topic]) acc[topic] = [];
    acc[topic].push(problem);
    return acc;
  }, {});

  const getTopicConfig = (topic) => {
    return TOPIC_CONFIG[topic] || { icon: '📝', name: topic.replace('_', ' '), color: '#666' };
  };

  const getTopicStats = (topicProblems) => {
    const solved = topicProblems.filter(p => p.solved).length;
    const easy = topicProblems.filter(p => p.difficulty === 'easy').length;
    const medium = topicProblems.filter(p => p.difficulty === 'medium').length;
    const hard = topicProblems.filter(p => p.difficulty === 'hard').length;
    return { solved, total: topicProblems.length, easy, medium, hard };
  };

  return (
    <div className="problem-list">
      <div className="problem-list-header">
        <h2>📚 Problem Library</h2>
        <div className="header-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="🔍 Search problems..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="view-toggle">
            <button className={viewMode === 'category' ? 'active' : ''} onClick={() => setViewMode('category')}>
              📂 Categories
            </button>
            <button className={viewMode === 'list' ? 'active' : ''} onClick={() => setViewMode('list')}>
              📋 List
            </button>
          </div>
          <select value={selectedDifficulty} onChange={(e) => setSelectedDifficulty(e.target.value)} className="difficulty-filter">
            <option value="">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
      </div>

      <div className="stats-summary">
        <div className="stat-item"><span className="stat-number">{problems.length}</span><span className="stat-label">Total</span></div>
        <div className="stat-item"><span className="stat-number solved">{problems.filter(p => p.solved).length}</span><span className="stat-label">Solved</span></div>
        <div className="stat-item easy"><span className="stat-number">{problems.filter(p => p.difficulty === 'easy').length}</span><span className="stat-label">Easy</span></div>
        <div className="stat-item medium"><span className="stat-number">{problems.filter(p => p.difficulty === 'medium').length}</span><span className="stat-label">Medium</span></div>
        <div className="stat-item hard"><span className="stat-number">{problems.filter(p => p.difficulty === 'hard').length}</span><span className="stat-label">Hard</span></div>
      </div>

      {loading ? (
        <div className="loading">Loading problems...</div>
      ) : viewMode === 'category' ? (
        <div className="category-view">
          <div className="expand-controls">
            <button onClick={expandAll}>Expand All</button>
            <button onClick={collapseAll}>Collapse All</button>
          </div>
          
          {Object.keys(filteredGrouped).sort().map((topic) => {
            const config = getTopicConfig(topic);
            const topicProblems = filteredGrouped[topic];
            const stats = getTopicStats(topicProblems);
            const isExpanded = expandedTopics[topic];

            return (
              <div key={topic} className="topic-section">
                <div className="topic-header" onClick={() => toggleTopic(topic)} style={{ borderLeftColor: config.color }}>
                  <div className="topic-title">
                    <span className="topic-icon">{config.icon}</span>
                    <span className="topic-name">{config.name}</span>
                    <span className="topic-count">{stats.total} problems</span>
                  </div>
                  <div className="topic-stats">
                    <span className="stat-solved">{stats.solved}/{stats.total}</span>
                    <span className="difficulty-dots">
                      <span className="dot easy">{stats.easy}</span>
                      <span className="dot medium">{stats.medium}</span>
                      <span className="dot hard">{stats.hard}</span>
                    </span>
                    <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▼</span>
                  </div>
                </div>
                
                {isExpanded && (
                  <div className="topic-problems">
                    {topicProblems.sort((a, b) => {
                      const order = { easy: 0, medium: 1, hard: 2 };
                      return order[a.difficulty] - order[b.difficulty];
                    }).map((problem) => (
                      <div key={problem.problem_id} className="problem-card" onClick={() => onSelectProblem(problem.problem_id)}>
                        <div className="problem-status">
                          {problem.solved ? <span className="solved-icon">✓</span> : <span className="unsolved-icon">○</span>}
                        </div>
                        <div className="problem-info">
                          <span className="problem-title">{problem.title}</span>
                          {problem.tags && problem.tags.length > 0 && (
                            <div className="problem-tags">
                              {problem.tags.slice(0, 3).map((tag, i) => <span key={i} className="tag">{tag}</span>)}
                            </div>
                          )}
                        </div>
                        <div className={`problem-difficulty ${getDifficultyClass(problem.difficulty)}`}>{problem.difficulty}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="problems-table">
          <div className="table-header">
            <span className="col-status">Status</span>
            <span className="col-title">Title</span>
            <span className="col-topic">Topic</span>
            <span className="col-difficulty">Difficulty</span>
          </div>
          {filteredProblems.map((problem) => (
            <div key={problem.problem_id} className="table-row" onClick={() => onSelectProblem(problem.problem_id)}>
              <span className="col-status">
                {problem.solved ? <span className="solved-icon">✓</span> : <span className="unsolved-icon">○</span>}
              </span>
              <span className="col-title">{problem.title}</span>
              <span className="col-topic">{getTopicConfig(problem.topic).icon} {getTopicConfig(problem.topic).name}</span>
              <span className={`col-difficulty ${getDifficultyClass(problem.difficulty)}`}>
                {problem.difficulty?.charAt(0).toUpperCase() + problem.difficulty?.slice(1)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProblemList;
