import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import { getProblem, runCode, submitCode, getRecommendations } from '../../services/api';
import './CodeEditor.css';

const LANGUAGES = [
  { id: 'python', name: 'Python', monaco: 'python' },
  { id: 'javascript', name: 'JavaScript', monaco: 'javascript' },
  { id: 'java', name: 'Java', monaco: 'java' },
  { id: 'cpp', name: 'C++', monaco: 'cpp' },
];

const STARTER_CODE = {
  python: (funcName, params) => `def ${funcName}(${params}):\n    # Write your code here\n    pass`,
  javascript: (funcName, params) => `function ${funcName}(${params}) {\n    // Write your code here\n    \n}`,
  java: (funcName, params) => `class Solution {\n    public Object ${funcName}(${params}) {\n        // Write your code here\n        return null;\n    }\n}`,
  cpp: (funcName, params) => `class Solution {\npublic:\n    auto ${funcName}(${params}) {\n        // Write your code here\n        \n    }\n};`,
};

const CodeEditor = ({ problemId, onBack, onSubmitSuccess, onSelectProblem }) => {
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [activeTab, setActiveTab] = useState('description');
  const startTimeRef = useRef(Date.now());
  const codeByLanguage = useRef({});

  useEffect(() => {
    // Reset all state when problem changes
    setResult(null);
    setAiAnalysis(null);
    setRecommendations(null);
    setActiveTab('description');
    setLanguage('python');
    
    loadProblem();
    startTimeRef.current = Date.now();
    codeByLanguage.current = {};
  }, [problemId]);

  const getStarterCode = (lang, funcName) => {
    const generator = STARTER_CODE[lang] || STARTER_CODE.python;
    return generator(funcName || 'solution', 'args');
  };

  const loadProblem = async () => {
    setLoading(true);
    try {
      const data = await getProblem(problemId);
      setProblem(data);
      const starterCode = data.starter_code || getStarterCode('python', data.function_name);
      setCode(starterCode);
      codeByLanguage.current = { python: starterCode };
    } catch (error) {
      console.error('Failed to load problem:', error);
    }
    setLoading(false);
  };

  const handleLanguageChange = (newLang) => {
    // Save current code for current language
    codeByLanguage.current[language] = code;
    
    // Load code for new language or generate starter code
    const savedCode = codeByLanguage.current[newLang];
    if (savedCode) {
      setCode(savedCode);
    } else {
      const starterCode = getStarterCode(newLang, problem?.function_name);
      setCode(starterCode);
      codeByLanguage.current[newLang] = starterCode;
    }
    
    setLanguage(newLang);
  };

  const handleRun = async () => {
    setRunning(true);
    setResult(null);
    setAiAnalysis(null);
    setRecommendations(null);
    setActiveTab('result');
    
    try {
      const data = await runCode(problemId, code, language);
      setResult(data);
    } catch (error) {
      setResult({ error: error.message || 'Failed to run code' });
    }
    setRunning(false);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setResult(null);
    setAiAnalysis(null);
    setRecommendations(null);
    setActiveTab('result');
    
    const timeTaken = Math.round((Date.now() - startTimeRef.current) / 60000);
    
    try {
      const data = await submitCode(problemId, code, timeTaken, language);
      setResult(data.execution_result);
      setAiAnalysis(data.ai_analysis);
      
      // Fetch recommendations after submission
      try {
        const recs = await getRecommendations();
        setRecommendations(recs);
      } catch (e) {
        console.error('Failed to load recommendations:', e);
      }
      
      if (data.execution_result?.passed) {
        onSubmitSuccess && onSubmitSuccess(data);
      }
    } catch (error) {
      setResult({ error: error.message || 'Failed to submit code' });
    }
    setSubmitting(false);
  };

  const getDifficultyClass = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'difficulty-easy';
      case 'medium': return 'difficulty-medium';
      case 'hard': return 'difficulty-hard';
      default: return '';
    }
  };

  if (loading) {
    return <div className="loading-editor">Loading problem...</div>;
  }

  if (!problem) {
    return <div className="error-message">Problem not found</div>;
  }

  return (
    <div className="code-editor-container">
      {/* Left Panel - Problem Description */}
      <div className="problem-panel">
        <div className="problem-header">
          <button className="back-btn" onClick={onBack}>← Back</button>
          <h2>{problem.title}</h2>
          <span className={`difficulty-badge ${getDifficultyClass(problem.difficulty)}`}>
            {problem.difficulty?.charAt(0).toUpperCase() + problem.difficulty?.slice(1)}
          </span>
        </div>

        <div className="problem-tabs">
          <button
            className={`tab ${activeTab === 'description' ? 'active' : ''}`}
            onClick={() => setActiveTab('description')}
          >
            Description
          </button>
          <button
            className={`tab ${activeTab === 'result' ? 'active' : ''}`}
            onClick={() => setActiveTab('result')}
          >
            Result
          </button>
        </div>

        <div className="problem-content">
          {activeTab === 'description' ? (
            <div className="description">
              <ReactMarkdown>{problem.description}</ReactMarkdown>
              
              <div className="problem-meta">
                <p><strong>Topic:</strong> {problem.topic?.replace('_', ' ')}</p>
                <p><strong>Expected Time:</strong> {problem.expected_time_minutes} minutes</p>
                <p><strong>Optimal Complexity:</strong> {problem.expected_complexity}</p>
              </div>
            </div>
          ) : (
            <div className="result-panel">
              {(running || submitting) && (
                <div className="running-indicator">
                  {running ? 'Running tests...' : 'Submitting...'}
                </div>
              )}

              {result && (
                <div className={`result-box ${result.passed ? 'success' : 'failure'}`}>
                  {result.error ? (
                    <div className="error">
                      <h4>Error</h4>
                      <pre>{result.error}</pre>
                    </div>
                  ) : (
                    <>
                      <div className="result-header">
                        <span className={result.passed ? 'passed' : 'failed'}>
                          {result.passed ? '✓ All Tests Passed!' : '✗ Some Tests Failed'}
                        </span>
                        <span className="test-count">
                          {result.passed_count}/{result.total_count} tests passed
                        </span>
                      </div>

                      <div className="test-results">
                        {result.test_results?.map((test, idx) => (
                          <div key={idx} className={`test-case ${test.passed ? 'passed' : 'failed'}`}>
                            <div className="test-header">
                              <span>{test.passed ? '✓' : '✗'} Test Case {idx + 1}</span>
                            </div>
                            {!test.passed && (
                              <div className="test-details">
                                {test.error ? (
                                  <pre className="error-output">{test.error}</pre>
                                ) : (
                                  <>
                                    <p><strong>Expected:</strong> {JSON.stringify(test.expected)}</p>
                                    <p><strong>Got:</strong> {JSON.stringify(test.actual)}</p>
                                  </>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}

              {aiAnalysis && (
                <div className="ai-analysis">
                  <h4>🤖 AI Analysis</h4>
                  
                  {/* Score and Mastery Level */}
                  <div className="analysis-header">
                    <div className="analysis-score">
                      <span className="score-label">Score:</span>
                      <span className="score-value">{aiAnalysis.score}/100</span>
                    </div>
                    {aiAnalysis.mastery_level && (
                      <div className={`mastery-badge mastery-${aiAnalysis.mastery_level?.toLowerCase()}`}>
                        {aiAnalysis.mastery_level}
                      </div>
                    )}
                  </div>

                  {/* Algorithm Type Detection */}
                  {aiAnalysis.algorithm_type && (
                    <div className="algorithm-section">
                      <h5>🔍 Algorithm Detected</h5>
                      <div className="algorithm-info">
                        <span className="algorithm-primary">{aiAnalysis.algorithm_type.primary || aiAnalysis.algorithm_type}</span>
                        {aiAnalysis.algorithm_type.secondary && aiAnalysis.algorithm_type.secondary.length > 0 && (
                          <div className="algorithm-secondary">
                            Also uses: {aiAnalysis.algorithm_type.secondary.join(', ')}
                          </div>
                        )}
                        {aiAnalysis.algorithm_type.is_appropriate === false && aiAnalysis.algorithm_type.better_approach && (
                          <div className="algorithm-suggestion">
                            💡 Consider: {aiAnalysis.algorithm_type.better_approach}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Complexity Analysis */}
                  <div className="complexity-section">
                    <h5>⚡ Complexity Analysis</h5>
                    <div className="complexity-grid">
                      <div className="complexity-card">
                        <span className="complexity-type">Time</span>
                        <span className="complexity-value">
                          {aiAnalysis.time_complexity?.estimate || aiAnalysis.time_complexity}
                        </span>
                        {aiAnalysis.time_complexity?.is_optimal !== undefined && (
                          <span className={`optimal-badge ${aiAnalysis.time_complexity.is_optimal ? 'optimal' : 'suboptimal'}`}>
                            {aiAnalysis.time_complexity.is_optimal ? '✓ Optimal' : '⚠ Can improve'}
                          </span>
                        )}
                        {aiAnalysis.time_complexity?.explanation && (
                          <p className="complexity-explanation">{aiAnalysis.time_complexity.explanation}</p>
                        )}
                      </div>
                      <div className="complexity-card">
                        <span className="complexity-type">Space</span>
                        <span className="complexity-value">
                          {aiAnalysis.space_complexity?.estimate || aiAnalysis.space_complexity}
                        </span>
                        {aiAnalysis.space_complexity?.is_optimal !== undefined && (
                          <span className={`optimal-badge ${aiAnalysis.space_complexity.is_optimal ? 'optimal' : 'suboptimal'}`}>
                            {aiAnalysis.space_complexity.is_optimal ? '✓ Optimal' : '⚠ Can improve'}
                          </span>
                        )}
                        {aiAnalysis.space_complexity?.explanation && (
                          <p className="complexity-explanation">{aiAnalysis.space_complexity.explanation}</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Test Case Analysis */}
                  {aiAnalysis.test_case_analysis && (
                    <div className="test-analysis-section">
                      <h5>🧪 Test Case Analysis</h5>
                      <div className="test-summary">
                        <span className="test-passed">{aiAnalysis.test_case_analysis.passed_tests || 0} Passed</span>
                        <span className="test-failed">{aiAnalysis.test_case_analysis.failed_tests || 0} Failed</span>
                        <span className="test-total">of {aiAnalysis.test_case_analysis.total_tests || 0} Total</span>
                      </div>
                      {aiAnalysis.test_case_analysis.failure_patterns && aiAnalysis.test_case_analysis.failure_patterns.length > 0 && (
                        <div className="failure-patterns">
                          <strong>Failure Patterns:</strong>
                          <ul>
                            {aiAnalysis.test_case_analysis.failure_patterns.map((pattern, idx) => (
                              <li key={idx}>{pattern}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {aiAnalysis.test_case_analysis.failure_reasons && aiAnalysis.test_case_analysis.failure_reasons.length > 0 && (
                        <div className="failure-reasons">
                          <strong>Why tests failed:</strong>
                          <ul>
                            {aiAnalysis.test_case_analysis.failure_reasons.map((reason, idx) => (
                              <li key={idx}>{reason}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Code Quality */}
                  {aiAnalysis.code_quality && (
                    <div className="code-quality-section">
                      <h5>📝 Code Quality</h5>
                      <div className="quality-grid">
                        <div className="quality-item">
                          <span className="quality-label">Readability</span>
                          <span className="quality-value">{aiAnalysis.code_quality.readability || 'N/A'}</span>
                        </div>
                        <div className="quality-item">
                          <span className="quality-label">Variable Naming</span>
                          <span className="quality-value">{aiAnalysis.code_quality.variable_naming || 'N/A'}</span>
                        </div>
                        <div className="quality-item">
                          <span className="quality-label">Code Structure</span>
                          <span className="quality-value">{aiAnalysis.code_quality.code_structure || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Concepts */}
                  {(aiAnalysis.concepts_demonstrated && aiAnalysis.concepts_demonstrated.length > 0) && (
                    <div className="concepts-section">
                      <h5>✅ Concepts Demonstrated</h5>
                      <div className="concepts-list">
                        {aiAnalysis.concepts_demonstrated.map((concept, idx) => (
                          <span key={idx} className="concept-tag demonstrated">{concept}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {(aiAnalysis.concepts_to_learn && aiAnalysis.concepts_to_learn.length > 0) && (
                    <div className="concepts-section">
                      <h5>📚 Concepts to Learn</h5>
                      <div className="concepts-list">
                        {aiAnalysis.concepts_to_learn.map((concept, idx) => (
                          <span key={idx} className="concept-tag to-learn">{concept}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Feedback */}
                  {aiAnalysis.feedback && (
                    <div className="feedback">
                      <h5>💬 Feedback</h5>
                      <p>{aiAnalysis.feedback}</p>
                    </div>
                  )}

                  {/* Improvement Tips */}
                  {aiAnalysis.improvement_tips && aiAnalysis.improvement_tips.length > 0 && (
                    <div className="improvements">
                      <h5>🚀 Improvement Tips</h5>
                      <ul>
                        {aiAnalysis.improvement_tips.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Legacy improvements support */}
                  {aiAnalysis.improvements && aiAnalysis.improvements.length > 0 && !aiAnalysis.improvement_tips && (
                    <div className="improvements">
                      <h5>🚀 Suggestions for Improvement</h5>
                      <ul>
                        {aiAnalysis.improvements.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Next Problem Link inside AI Analysis */}
                  {recommendations && recommendations.recommended_problems && recommendations.recommended_problems.length > 0 && (
                    <div className="next-problem-section">
                      <h5>➡️ Try Next Problem</h5>
                      <div 
                        className="next-problem-link"
                        onClick={() => {
                          const nextProblem = recommendations.recommended_problems[0];
                          if (onSelectProblem && nextProblem.problem_id) {
                            onSelectProblem(nextProblem.problem_id);
                          }
                        }}
                      >
                        <div className="next-problem-info">
                          <span className="next-problem-title">{recommendations.recommended_problems[0].title}</span>
                          <span className={`next-problem-difficulty ${recommendations.recommended_problems[0].difficulty}`}>
                            {recommendations.recommended_problems[0].difficulty}
                          </span>
                        </div>
                        <span className="next-problem-topic">
                          {recommendations.recommended_problems[0].topic?.replace('_', ' ')}
                        </span>
                        {recommendations.recommended_problems[0].reason && (
                          <p className="next-problem-reason">{recommendations.recommended_problems[0].reason}</p>
                        )}
                        <span className="next-problem-arrow">→ Start Problem</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* AI Recommendations after submission */}
              {recommendations && recommendations.recommended_problems && recommendations.recommended_problems.length > 0 && (
                <div className="inline-recommendations">
                  <h4>🎯 Recommended Next Problems</h4>
                  {recommendations.message && (
                    <p className="rec-message">{recommendations.message}</p>
                  )}
                  <div className="rec-problems">
                    {recommendations.recommended_problems.slice(0, 3).map((rec, idx) => (
                      <div 
                        key={idx} 
                        className="rec-problem" 
                        onClick={() => {
                          if (onSelectProblem && rec.problem_id) {
                            onSelectProblem(rec.problem_id);
                          }
                        }}
                      >
                        <span className="rec-title">{rec.title}</span>
                        <span className={`rec-difficulty ${rec.difficulty}`}>{rec.difficulty}</span>
                        <span className="rec-topic">{rec.topic?.replace('_', ' ')}</span>
                        {rec.reason && <p className="rec-reason">{rec.reason}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right Panel - Code Editor */}
      <div className="editor-panel">
        <div className="editor-header">
          <div className="language-selector">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.id}
                className={`lang-btn ${language === lang.id ? 'active' : ''}`}
                onClick={() => handleLanguageChange(lang.id)}
              >
                {lang.name}
              </button>
            ))}
          </div>
        </div>

        <div className="editor-wrapper">
          <Editor
            height="100%"
            language={LANGUAGES.find(l => l.id === language)?.monaco || 'python'}
            value={code}
            onChange={(value) => setCode(value || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
            }}
          />
        </div>

        <div className="editor-actions">
          <button
            className="run-btn"
            onClick={handleRun}
            disabled={running || submitting}
          >
            {running ? 'Running...' : '▶ Run'}
          </button>
          <button
            className="submit-btn"
            onClick={handleSubmit}
            disabled={running || submitting}
          >
            {submitting ? 'Submitting...' : '✓ Submit'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;
