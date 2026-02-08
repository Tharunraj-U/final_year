import React from 'react';
import './TopicBreakdown.css';

const TopicBreakdown = ({ topics }) => {
  if (!topics || topics.length === 0) {
    return (
      <div className="topic-breakdown">
        <h2>📊 Topic Performance</h2>
        <p className="no-data">No topic data available yet. Start solving problems!</p>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 70) return '#10b981';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  const formatTopic = (topic) => {
    return topic
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="topic-breakdown">
      <h2>📊 Topic Performance</h2>
      <div className="topics-list">
        {topics.map((topic, index) => (
          <div key={index} className="topic-item">
            <div className="topic-header">
              <span className="topic-name">{formatTopic(topic.topic)}</span>
              <span 
                className="topic-score"
                style={{ color: getScoreColor(topic.score) }}
              >
                {topic.score.toFixed(1)}%
              </span>
            </div>
            <div className="topic-progress-bar">
              <div 
                className="topic-progress-fill"
                style={{ 
                  width: `${Math.min(topic.score, 100)}%`,
                  background: getScoreColor(topic.score)
                }}
              />
            </div>
            <div className="topic-stats">
              <span>✅ {topic.problems_solved}/{topic.problems_attempted} solved</span>
              <span>🎯 {(topic.accuracy * 100).toFixed(0)}% accuracy</span>
              <span>⚡ {(topic.avg_complexity_score * 100).toFixed(0)}% efficiency</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopicBreakdown;
