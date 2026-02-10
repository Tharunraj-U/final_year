import React, { useState, useEffect } from 'react';
import { getStreakDetails } from '../../services/api';
import { Flame, Snowflake, Calendar, TrendingUp, Target, Award } from 'lucide-react';
import './StreakCounter.css';

const StreakCounter = ({ streak = 0 }) => {
  const [streakDetails, setStreakDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStreakDetails();
  }, [streak]);

  const fetchStreakDetails = async () => {
    try {
      const details = await getStreakDetails();
      setStreakDetails(details);
    } catch (error) {
      console.error('Failed to load streak details:', error);
    }
    setLoading(false);
  };

  // Generate last 12 weeks of calendar data (84 days)
  const generateCalendarData = () => {
    const practiceDates = new Set(streakDetails?.practice_dates || []);
    const today = new Date();
    const calendar = [];
    
    // Start from 83 days ago to today
    for (let i = 83; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      calendar.push({
        date: dateStr,
        active: practiceDates.has(dateStr),
        dayOfWeek: date.getDay(),
        isToday: i === 0
      });
    }
    
    return calendar;
  };

  const getStreakLevel = (current) => {
    if (current >= 30) return { level: 'legendary', title: 'Legendary', icon: '👑' };
    if (current >= 14) return { level: 'master', title: 'Master', icon: '⭐' };
    if (current >= 7) return { level: 'pro', title: 'Pro', icon: '🔥' };
    if (current >= 3) return { level: 'rising', title: 'Rising', icon: '💪' };
    if (current >= 1) return { level: 'beginner', title: 'Starting', icon: '🌱' };
    return { level: 'none', title: 'No Streak', icon: '💤' };
  };

  const getMotivationalMessage = () => {
    if (!streakDetails) return "Loading...";
    
    const currentStreak = streakDetails.current_streak || streak;
    
    if (currentStreak === 0) return "Start your coding journey today! 🚀";
    if (currentStreak === 1) return "Day 1 complete! The beginning of greatness!";
    if (currentStreak < 3) return "Building momentum! Keep going!";
    if (currentStreak < 7) return "You're on fire! Don't break the chain!";
    if (currentStreak < 14) return "A week strong! You're unstoppable!";
    if (currentStreak < 30) return "Incredible dedication! You inspire us!";
    return "Legendary status achieved! 👑";
  };

  const calendarData = generateCalendarData();
  const currentStreak = streakDetails?.current_streak || streak;
  const streakLevel = getStreakLevel(currentStreak);

  // Group calendar by weeks
  const weeks = [];
  for (let i = 0; i < calendarData.length; i += 7) {
    weeks.push(calendarData.slice(i, i + 7));
  }

  return (
    <div className="streak-container-compact">
      {/* Compact Streak Card */}
      <div className={`streak-card-compact ${streakLevel.level}`}>
        <div className="streak-left">
          <div className="streak-icon-compact">
            {currentStreak > 0 ? <Flame size={28} /> : <Snowflake size={28} />}
          </div>
          <div className="streak-info-compact">
            <div className="streak-number-compact">
              <span className="number">{currentStreak}</span>
              <span className="unit">day streak</span>
            </div>
            <div className="streak-level-compact">
              <span className="level-badge">{streakLevel.icon} {streakLevel.title}</span>
            </div>
          </div>
        </div>
        
        <div className="streak-stats-compact">
          <div className="stat-compact">
            <TrendingUp size={14} />
            <span className="stat-value">{streakDetails?.weekly_submissions || 0}</span>
            <span className="stat-label">Week</span>
          </div>
          <div className="stat-compact">
            <Target size={14} />
            <span className="stat-value">{streakDetails?.monthly_submissions || 0}</span>
            <span className="stat-label">Month</span>
          </div>
          <div className="stat-compact">
            <Award size={14} />
            <span className="stat-value">{streakDetails?.total_practice_days || 0}</span>
            <span className="stat-label">Total</span>
          </div>
        </div>
      </div>

      {/* Activity Heatmap */}
      <div className="activity-heatmap-compact">
        <div className="heatmap-header-compact">
          <h4><Calendar size={14} /> Activity</h4>
          <div className="heatmap-legend-compact">
            <div className="legend-box level-0"></div>
            <div className="legend-box level-1"></div>
            <div className="legend-box level-2"></div>
            <div className="legend-box level-3"></div>
          </div>
        </div>
        
        <div className="heatmap-grid-compact">
          {weeks.map((week, weekIndex) => (
            <div key={weekIndex} className="heatmap-week">
              {week.map((day, dayIndex) => (
                <div
                  key={`${weekIndex}-${dayIndex}`}
                  className={`heatmap-day ${day.active ? 'active' : ''} ${day.isToday ? 'today' : ''}`}
                  title={`${day.date}${day.active ? ' - Practiced!' : ''}`}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StreakCounter;
