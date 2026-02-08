import React from 'react';
import './StrengthsWeaknesses.css';

const StrengthsWeaknesses = ({ strengths, weaknesses }) => {
  const formatTopic = (topic) => {
    return topic
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="strengths-weaknesses">
      <div className="sw-section strengths">
        <h3>💪 Strengths</h3>
        {strengths && strengths.length > 0 ? (
          <ul>
            {strengths.map((s, i) => (
              <li key={i} className="strength-item">
                <span className="sw-icon">✓</span>
                {formatTopic(s)}
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-items">Keep practicing to discover your strengths!</p>
        )}
      </div>
      
      <div className="sw-section weaknesses">
        <h3>🎯 Areas to Improve</h3>
        {weaknesses && weaknesses.length > 0 ? (
          <ul>
            {weaknesses.map((w, i) => (
              <li key={i} className="weakness-item">
                <span className="sw-icon">→</span>
                {formatTopic(w)}
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-items">Great job! No major weaknesses detected.</p>
        )}
      </div>
    </div>
  );
};

export default StrengthsWeaknesses;
