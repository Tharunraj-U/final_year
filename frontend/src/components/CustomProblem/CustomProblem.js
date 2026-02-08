import React, { useState } from 'react';
import { addCustomProblem } from '../../services/api';
import './CustomProblem.css';

const TOPICS = [
  'arrays', 'strings', 'sliding_window', 'two_pointers', 'binary_search',
  'linked_lists', 'trees', 'graphs', 'dynamic_programming', 'backtracking',
  'greedy', 'stacks', 'hashing', 'heap', 'bit_manipulation'
];

const CustomProblem = ({ onBack, onProblemCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    difficulty: 'easy',
    topic: 'arrays',
    description: '',
    function_name: 'solution',
    expected_complexity: 'O(n)',
    expected_time_minutes: 30,
    starter_code: '',
    tags: ''
  });
  
  const [testCases, setTestCases] = useState([
    { input: '', expected: '' }
  ]);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Auto-generate starter code when function name changes
    if (name === 'function_name') {
      setFormData(prev => ({
        ...prev,
        [name]: value,
        starter_code: `def ${value}():\n    # Write your code here\n    pass`
      }));
    }
  };

  const handleTestCaseChange = (index, field, value) => {
    const updated = [...testCases];
    updated[index][field] = value;
    setTestCases(updated);
  };

  const addTestCase = () => {
    setTestCases([...testCases, { input: '', expected: '' }]);
  };

  const removeTestCase = (index) => {
    if (testCases.length > 1) {
      setTestCases(testCases.filter((_, i) => i !== index));
    }
  };

  const parseTestCaseValue = (value) => {
    try {
      return JSON.parse(value);
    } catch {
      return value;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Parse test cases
      const parsedTestCases = testCases.map(tc => ({
        input: parseTestCaseValue(tc.input),
        expected: parseTestCaseValue(tc.expected)
      }));

      const problemData = {
        ...formData,
        tags: formData.tags.split(',').map(t => t.trim()).filter(t => t),
        test_cases: parsedTestCases
      };

      const result = await addCustomProblem(problemData);
      setSuccess(true);
      
      // Reset form
      setFormData({
        title: '',
        difficulty: 'easy',
        topic: 'arrays',
        description: '',
        function_name: 'solution',
        expected_complexity: 'O(n)',
        expected_time_minutes: 30,
        starter_code: '',
        tags: ''
      });
      setTestCases([{ input: '', expected: '' }]);

      if (onProblemCreated) {
        onProblemCreated(result.problem);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create problem');
    }
    
    setLoading(false);
  };

  return (
    <div className="custom-problem">
      <div className="custom-problem-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <h2>📝 Create Custom Problem</h2>
      </div>

      {success && (
        <div className="success-banner">
          ✅ Problem created successfully! You can find it in the problem list.
        </div>
      )}

      {error && (
        <div className="error-banner">
          ❌ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="problem-form">
        <div className="form-section">
          <h3>📋 Basic Information</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label>Problem Title *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="e.g., Two Sum"
                required
              />
            </div>
            
            <div className="form-group">
              <label>Function Name *</label>
              <input
                type="text"
                name="function_name"
                value={formData.function_name}
                onChange={handleInputChange}
                placeholder="e.g., two_sum"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Difficulty *</label>
              <select
                name="difficulty"
                value={formData.difficulty}
                onChange={handleInputChange}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Topic *</label>
              <select
                name="topic"
                value={formData.topic}
                onChange={handleInputChange}
              >
                {TOPICS.map(topic => (
                  <option key={topic} value={topic}>
                    {topic.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label>Expected Time (min)</label>
              <input
                type="number"
                name="expected_time_minutes"
                value={formData.expected_time_minutes}
                onChange={handleInputChange}
                min="5"
                max="120"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe the problem, include examples..."
              rows={6}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Expected Complexity</label>
              <input
                type="text"
                name="expected_complexity"
                value={formData.expected_complexity}
                onChange={handleInputChange}
                placeholder="e.g., O(n), O(n log n)"
              />
            </div>
            
            <div className="form-group">
              <label>Tags (comma-separated)</label>
              <input
                type="text"
                name="tags"
                value={formData.tags}
                onChange={handleInputChange}
                placeholder="e.g., hash_map, two_pointers"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Starter Code (optional)</label>
            <textarea
              name="starter_code"
              value={formData.starter_code}
              onChange={handleInputChange}
              placeholder={`def ${formData.function_name}():\n    # Write your code here\n    pass`}
              rows={4}
              className="code-input"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>🧪 Test Cases</h3>
          <p className="hint">Enter input as JSON array and expected output as JSON value</p>
          
          {testCases.map((tc, index) => (
            <div key={index} className="test-case-row">
              <div className="test-case-number">#{index + 1}</div>
              <div className="test-case-inputs">
                <div className="form-group">
                  <label>Input (JSON)</label>
                  <input
                    type="text"
                    value={tc.input}
                    onChange={(e) => handleTestCaseChange(index, 'input', e.target.value)}
                    placeholder='e.g., [[2,7,11,15], 9]'
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Expected Output (JSON)</label>
                  <input
                    type="text"
                    value={tc.expected}
                    onChange={(e) => handleTestCaseChange(index, 'expected', e.target.value)}
                    placeholder='e.g., [0, 1]'
                    required
                  />
                </div>
              </div>
              <button
                type="button"
                className="remove-btn"
                onClick={() => removeTestCase(index)}
                disabled={testCases.length === 1}
              >
                ✕
              </button>
            </div>
          ))}
          
          <button type="button" className="add-test-btn" onClick={addTestCase}>
            + Add Test Case
          </button>
        </div>

        <div className="form-actions">
          <button type="button" className="cancel-btn" onClick={onBack}>
            Cancel
          </button>
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? '⏳ Creating...' : '✨ Create Problem'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CustomProblem;
