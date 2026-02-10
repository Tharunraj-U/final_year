import React from 'react';
import { Trash2, CheckCircle, XCircle, Clock, Zap } from 'lucide-react';
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
        <h2><Clock size={18} /> Submission History <span className="count">({submissions.length})</span></h2>
        <button className="clear-btn" onClick={onClear}>
          <Trash2 size={14} />
          Clear All
        </button>
      </div>
      <div className="history-list">
        {submissions.slice().reverse().map((sub, index) => (
          <div key={index} className={`history-item ${sub.solved ? 'solved' : 'unsolved'}`}>
            <div className="history-status">
              {sub.solved ? <CheckCircle size={20} /> : <XCircle size={20} />}
            </div>
            <div className="history-details">
              <span className="history-title">{sub.problem_title}</span>
              <span className="history-meta">
                <span className="meta-tag topic">{formatTopic(sub.topic)}</span>
                <span className={`meta-tag difficulty ${sub.difficulty?.toLowerCase()}`}>{sub.difficulty}</span>
                <span className="meta-tag">{sub.attempts} attempt(s)</span>
                <span className="meta-tag">{sub.time_taken_minutes} min</span>
              </span>
            </div>
            <div className="history-complexity">
              <Zap size={12} />
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
