import React, { useState, useEffect } from 'react';
import './StreakCounter.css';

const StreakCounter = ({ streak = 0, lastPractice }) => {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (streak > 0) {
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [streak]);

  const getStreakMessage = () => {
    if (streak === 0) return "Start your streak today!";
    if (streak < 3) return "Great start! Keep it up!";
    if (streak < 7) return "You're on fire! 🔥";
    if (streak < 14) return "Incredible dedication!";
    if (streak < 30) return "Unstoppable! 💪";
    return "Legendary coder! 👑";
  };

  const getFireIntensity = () => {
    if (streak < 3) return 1;
    if (streak < 7) return 2;
    if (streak < 14) return 3;
    return 4;
  };

  return (
    <div className={`streak-counter ${isAnimating ? 'animate' : ''}`}>
      <div className="streak-fire">
        {[...Array(getFireIntensity())].map((_, i) => (
          <span key={i} className={`fire fire-${i + 1}`}>🔥</span>
        ))}
      </div>
      <div className="streak-info">
        <div className="streak-number">
          <span className="count">{streak}</span>
          <span className="label">day streak</span>
        </div>
        <div className="streak-message">{getStreakMessage()}</div>
      </div>
      <div className="streak-calendar">
        {[...Array(7)].map((_, i) => (
          <div 
            key={i} 
            className={`calendar-day ${i < Math.min(streak, 7) ? 'active' : ''}`}
            title={i < streak ? 'Practiced!' : 'Upcoming'}
          >
            {i < Math.min(streak, 7) ? '✓' : '○'}
          </div>
        ))}
      </div>
    </div>
  );
};

export default StreakCounter;
