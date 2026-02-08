import React from 'react';
import './SubmissionHistory.css';

const SubmissionHistory = ({ submissions, onClear }) => {
  if (!submissions || submissions.length === 0) {
    return null;
  }

  const formatTopic = (topic) => {
    return topic
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="submission-history">
      <div className="history-header">
        <h2>📋 Submission History ({submissions.length})</h2>
        <button className="clear-btn" onClick={onClear}>Clear All</button>
      </div>
      <div className="history-list">
        {submissions.slice().reverse().map((sub, index) => (
          <div key={index} className={`history-item ${sub.solved ? 'solved' : 'unsolved'}`}>
            <div className="history-status">
              {sub.solved ? '✅' : '❌'}
            </div>
            <div className="history-details">
              <span className="history-title">{sub.problem_title}</span>
              <span className="history-meta">
                {formatTopic(sub.topic)} • {sub.difficulty} • {sub.attempts} attempt(s) • {sub.time_taken_minutes} min
              </span>
            </div>
            <div className="history-complexity">
              <span className={sub.user_complexity === sub.expected_complexity ? 'optimal' : 'suboptimal'}>
                {sub.user_complexity}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubmissionHistory;
