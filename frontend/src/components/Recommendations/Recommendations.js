import React from 'react';
import { Target, Lightbulb } from 'lucide-react';
import './Recommendations.css';

const Recommendations = ({ recommendations, onSelectProblem }) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="recommendations">
        <h2><Target size={22} /> Recommended Problems</h2>
        <p className="no-data">Complete some problems to get personalized recommendations!</p>
      </div>
    );
  }

  const getDifficultyClass = (difficulty) => {
    return `difficulty-${difficulty}`;
  };

  const formatTopic = (topic) => {
    return topic
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="recommendations">
      <h2><Target size={22} /> Recommended Problems</h2>
      <div className="recommendations-list">
        {recommendations.map((rec, index) => (
          <div 
            key={index} 
            className="recommendation-card"
            onClick={() => onSelectProblem && onSelectProblem(rec)}
          >
            <div className="rec-header">
              <span className={`difficulty-badge ${getDifficultyClass(rec.difficulty)}`}>
                {rec.difficulty.toUpperCase()}
              </span>
              <span className="complexity-badge">{rec.expected_complexity}</span>
            </div>
            <h3 className="rec-title">{rec.title}</h3>
            <span className="rec-topic">{formatTopic(rec.topic)}</span>
            <p className="rec-reason"><Lightbulb size={14} /> {rec.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Recommendations;
