import React, { useState, useEffect } from 'react';
import { sendWeeklyReport } from '../../services/api';
import './StatsDashboard.css';

const StatsDashboard = ({ stats }) => {
  const [animatedStats, setAnimatedStats] = useState({
    problems_solved: 0,
    total_submissions: 0,
    accuracy: 0,
    avg_score: 0
  });
  const [sendingReport, setSendingReport] = useState(false);
  const [reportMessage, setReportMessage] = useState(null);

  useEffect(() => {
    if (stats) {
      // Animate numbers counting up
      const duration = 1500;
      const steps = 60;
      const interval = duration / steps;
      
      let step = 0;
      const timer = setInterval(() => {
        step++;
        const progress = step / steps;
        const easeOut = 1 - Math.pow(1 - progress, 3);
        
        setAnimatedStats({
          problems_solved: Math.round(stats.problems_solved * easeOut),
          total_submissions: Math.round(stats.total_submissions * easeOut),
          accuracy: Math.round(stats.accuracy * easeOut),
          avg_score: Math.round(stats.avg_score * easeOut)
        });
        
        if (step >= steps) {
          clearInterval(timer);
          setAnimatedStats(stats);
        }
      }, interval);
      
      return () => clearInterval(timer);
    }
  }, [stats]);

  const defaultStats = {
    problems_solved: 0,
    total_submissions: 0,
    accuracy: 0,
    avg_score: 0,
    easy_solved: 0,
    medium_solved: 0,
    hard_solved: 0,
    ...stats
  };

  const getDifficultyProgress = () => {
    const total = defaultStats.problems_solved || 1;
    return {
      easy: (defaultStats.easy_solved / total) * 100,
      medium: (defaultStats.medium_solved / total) * 100,
      hard: (defaultStats.hard_solved / total) * 100
    };
  };

  const diffProgress = getDifficultyProgress();

  return (
    <div className="stats-dashboard">
      <h3 className="dashboard-title">📊 Your Statistics</h3>
      
      <div className="stats-grid">
        <div className="stat-card problems">
          <div className="stat-icon">📝</div>
          <div className="stat-value">{animatedStats.problems_solved}</div>
          <div className="stat-label">Problems Solved</div>
          <div className="stat-ring">
            <svg viewBox="0 0 36 36">
              <path
                className="ring-bg"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="ring-fill"
                strokeDasharray={`${Math.min(animatedStats.problems_solved, 100)}, 100`}
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
          </div>
        </div>

        <div className="stat-card submissions">
          <div className="stat-icon">🚀</div>
          <div className="stat-value">{animatedStats.total_submissions}</div>
          <div className="stat-label">Total Submissions</div>
        </div>

        <div className="stat-card accuracy">
          <div className="stat-icon">🎯</div>
          <div className="stat-value">{animatedStats.accuracy}%</div>
          <div className="stat-label">Accuracy</div>
          <div className="accuracy-bar">
            <div 
              className="accuracy-fill" 
              style={{ width: `${animatedStats.accuracy}%` }}
            ></div>
          </div>
        </div>

        <div className="stat-card score">
          <div className="stat-icon">⭐</div>
          <div className="stat-value">{animatedStats.avg_score}</div>
          <div className="stat-label">Average Score</div>
        </div>
      </div>

      <div className="difficulty-breakdown">
        <h4>Difficulty Breakdown</h4>
        <div className="difficulty-bars">
          <div className="difficulty-item">
            <div className="diff-label">
              <span className="diff-dot easy"></span>
              Easy
            </div>
            <div className="diff-bar">
              <div 
                className="diff-fill easy" 
                style={{ width: `${diffProgress.easy}%` }}
              ></div>
            </div>
            <span className="diff-count">{defaultStats.easy_solved}</span>
          </div>
          <div className="difficulty-item">
            <div className="diff-label">
              <span className="diff-dot medium"></span>
              Medium
            </div>
            <div className="diff-bar">
              <div 
                className="diff-fill medium" 
                style={{ width: `${diffProgress.medium}%` }}
              ></div>
            </div>
            <span className="diff-count">{defaultStats.medium_solved}</span>
          </div>
          <div className="difficulty-item">
            <div className="diff-label">
              <span className="diff-dot hard"></span>
              Hard
            </div>
            <div className="diff-bar">
              <div 
                className="diff-fill hard" 
                style={{ width: `${diffProgress.hard}%` }}
              ></div>
            </div>
            <span className="diff-count">{defaultStats.hard_solved}</span>
          </div>
        </div>
      </div>

      <div className="weekly-activity">
        <h4>This Week's Activity</h4>
        <div className="activity-graph">
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => {
            const height = Math.random() * 80 + 20; // Demo data
            return (
              <div key={day} className="activity-bar-container">
                <div 
                  className="activity-bar" 
                  style={{ height: `${height}%` }}
                ></div>
                <span className="day-label">{day}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Weekly Report Section */}
      <div className="weekly-report-section">
        <h4>📧 Weekly Progress Report</h4>
        <p>Get your progress summary sent to your email!</p>
        {reportMessage && (
          <div className={`report-message ${reportMessage.type}`}>
            {reportMessage.text}
          </div>
        )}
        <button 
          className="send-report-btn"
          onClick={async () => {
            setSendingReport(true);
            setReportMessage(null);
            try {
              const result = await sendWeeklyReport();
              setReportMessage({ type: 'success', text: '✅ Report sent to your email!' });
            } catch (error) {
              setReportMessage({ type: 'error', text: '❌ Failed to send report. Please try again.' });
            }
            setSendingReport(false);
          }}
          disabled={sendingReport}
        >
          {sendingReport ? '📤 Sending...' : '📤 Send Report Now'}
        </button>
      </div>
    </div>
  );
};

export default StatsDashboard;
