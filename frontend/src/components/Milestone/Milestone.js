import React from 'react';
import './Milestone.css';

const Milestone = ({ milestone }) => {
  if (!milestone) return null;

  const progress = Math.min(milestone.progress, 100);

  return (
    <div className="milestone">
      <div className="milestone-header">
        <span className="milestone-icon">🏆</span>
        <h3>Next Milestone</h3>
      </div>
      <p className="milestone-desc">{milestone.description}</p>
      <div className="milestone-progress-container">
        <div className="milestone-progress-bar">
          <div 
            className="milestone-progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="milestone-percentage">{progress.toFixed(0)}%</span>
      </div>
      {milestone.requirements && (
        <div className="milestone-requirements">
          <span>Score: {milestone.requirements.current_score}/{milestone.requirements.score_target}</span>
          <span>Problems: {milestone.requirements.current_problems}/{milestone.requirements.problems_target}</span>
        </div>
      )}
    </div>
  );
};

export default Milestone;
