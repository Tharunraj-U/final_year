import React, { useState } from 'react';
import './SubmissionForm.css';

const SubmissionForm = ({ problems, onSubmit }) => {
  const [formData, setFormData] = useState({
    problem_id: '',
    solved: true,
    attempts: 1,
    time_taken_minutes: 15,
    user_complexity: 'O(n)'
  });

  const complexityOptions = [
    'O(1)',
    'O(log n)',
    'O(n)',
    'O(n log n)',
    'O(n^2)',
    'O(n^3)',
    'O(2^n)'
  ];

  const selectedProblem = problems?.find(p => p.problem_id === formData.problem_id);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedProblem) return;

    const submission = {
      problem_id: formData.problem_id,
      problem_title: selectedProblem.title,
      topic: selectedProblem.topic,
      difficulty: selectedProblem.difficulty,
      solved: formData.solved,
      attempts: parseInt(formData.attempts),
      time_taken_minutes: parseInt(formData.time_taken_minutes),
      user_complexity: formData.user_complexity,
      expected_complexity: selectedProblem.expected_complexity
    };

    onSubmit(submission);
    
    // Reset form
    setFormData({
      problem_id: '',
      solved: true,
      attempts: 1,
      time_taken_minutes: 15,
      user_complexity: 'O(n)'
    });
  };

  return (
    <div className="submission-form">
      <h2>📝 Log a Submission</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Select Problem</label>
          <select 
            name="problem_id" 
            value={formData.problem_id} 
            onChange={handleChange}
            required
          >
            <option value="">Choose a problem...</option>
            {problems?.map(p => (
              <option key={p.problem_id} value={p.problem_id}>
                [{p.difficulty.toUpperCase()}] {p.title} - {p.topic}
              </option>
            ))}
          </select>
        </div>

        {selectedProblem && (
          <div className="problem-info">
            <span>Expected: {selectedProblem.expected_complexity}</span>
            <span>Time limit: {selectedProblem.expected_time_minutes} min</span>
          </div>
        )}

        <div className="form-row">
          <div className="form-group">
            <label>Solved?</label>
            <div className="toggle-container">
              <input 
                type="checkbox" 
                name="solved" 
                checked={formData.solved}
                onChange={handleChange}
                id="solved-toggle"
              />
              <label htmlFor="solved-toggle" className="toggle-label">
                {formData.solved ? '✅ Yes' : '❌ No'}
              </label>
            </div>
          </div>

          <div className="form-group">
            <label>Attempts</label>
            <input 
              type="number" 
              name="attempts" 
              min="1" 
              max="20"
              value={formData.attempts}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Time (minutes)</label>
            <input 
              type="number" 
              name="time_taken_minutes" 
              min="1" 
              max="180"
              value={formData.time_taken_minutes}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Your Solution Complexity</label>
          <select 
            name="user_complexity" 
            value={formData.user_complexity}
            onChange={handleChange}
          >
            {complexityOptions.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <button type="submit" className="submit-btn" disabled={!formData.problem_id}>
          Add Submission
        </button>
      </form>
    </div>
  );
};

export default SubmissionForm;
