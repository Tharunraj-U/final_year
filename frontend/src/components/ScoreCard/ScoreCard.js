import React from 'react';
import './ScoreCard.css';

const ScoreCard = ({ title, value, subtitle, icon, color = 'blue' }) => {
  return (
    <div className={`score-card score-card-${color}`}>
      <div className="score-card-icon">{icon}</div>
      <div className="score-card-content">
        <h3 className="score-card-title">{title}</h3>
        <p className="score-card-value">{value}</p>
        {subtitle && <span className="score-card-subtitle">{subtitle}</span>}
      </div>
    </div>
  );
};

export default ScoreCard;
