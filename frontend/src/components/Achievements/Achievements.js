import React, { useState, useEffect } from 'react';
import './Achievements.css';

const ACHIEVEMENTS = [
  { id: 'first_solve', icon: '🎯', title: 'First Blood', description: 'Solve your first problem', requirement: (stats) => stats.problems_solved >= 1 },
  { id: 'five_solved', icon: '⭐', title: 'Rising Star', description: 'Solve 5 problems', requirement: (stats) => stats.problems_solved >= 5 },
  { id: 'ten_solved', icon: '🔥', title: 'On Fire', description: 'Solve 10 problems', requirement: (stats) => stats.problems_solved >= 10 },
  { id: 'twentyfive_solved', icon: '💎', title: 'Diamond Coder', description: 'Solve 25 problems', requirement: (stats) => stats.problems_solved >= 25 },
  { id: 'fifty_solved', icon: '👑', title: 'Code Master', description: 'Solve 50 problems', requirement: (stats) => stats.problems_solved >= 50 },
  { id: 'perfect_score', icon: '💯', title: 'Perfectionist', description: 'Get 100% on a problem', requirement: (stats) => stats.has_perfect_score },
  { id: 'streak_3', icon: '🔥', title: 'Hot Streak', description: '3-day practice streak', requirement: (stats) => stats.streak >= 3 },
  { id: 'streak_7', icon: '🌟', title: 'Weekly Warrior', description: '7-day practice streak', requirement: (stats) => stats.streak >= 7 },
  { id: 'streak_30', icon: '🏆', title: 'Monthly Champion', description: '30-day practice streak', requirement: (stats) => stats.streak >= 30 },
  { id: 'speed_demon', icon: '⚡', title: 'Speed Demon', description: 'Solve a problem in under 5 minutes', requirement: (stats) => stats.fastest_solve < 5 },
  { id: 'all_topics', icon: '🎓', title: 'Well Rounded', description: 'Solve problems from 5+ topics', requirement: (stats) => stats.topics_count >= 5 },
  { id: 'hard_solver', icon: '💪', title: 'Challenge Accepted', description: 'Solve a hard problem', requirement: (stats) => stats.hard_solved >= 1 },
];

const Achievements = ({ stats, onClose }) => {
  const [unlockedAchievements, setUnlockedAchievements] = useState([]);
  const [newlyUnlocked, setNewlyUnlocked] = useState(null);

  useEffect(() => {
    if (stats) {
      const unlocked = ACHIEVEMENTS.filter(a => a.requirement(stats)).map(a => a.id);
      setUnlockedAchievements(unlocked);
    }
  }, [stats]);

  const getProgress = () => {
    return Math.round((unlockedAchievements.length / ACHIEVEMENTS.length) * 100);
  };

  return (
    <div className="achievements-overlay">
      <div className="achievements-modal">
        <div className="achievements-header">
          <h2>🏆 Achievements</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="achievements-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${getProgress()}%` }}
            ></div>
          </div>
          <span className="progress-text">
            {unlockedAchievements.length}/{ACHIEVEMENTS.length} Unlocked ({getProgress()}%)
          </span>
        </div>

        <div className="achievements-grid">
          {ACHIEVEMENTS.map(achievement => {
            const isUnlocked = unlockedAchievements.includes(achievement.id);
            return (
              <div 
                key={achievement.id} 
                className={`achievement-card ${isUnlocked ? 'unlocked' : 'locked'}`}
              >
                <div className="achievement-icon">
                  {isUnlocked ? achievement.icon : '🔒'}
                </div>
                <div className="achievement-info">
                  <h4>{achievement.title}</h4>
                  <p>{achievement.description}</p>
                </div>
                {isUnlocked && <div className="unlocked-badge">✓</div>}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Achievements;
