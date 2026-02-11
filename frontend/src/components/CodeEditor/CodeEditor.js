import React, { useState, useEffect, useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import { getProblem, runCode, submitCode, getRecommendations, saveCodeDraft, getCodeDraft, getProblemSubmissions } from '../../services/api';
import AIHelper from '../AIHelper/AIHelper';
import './CodeEditor.css';

const LANGUAGES = [
  { id: 'python', name: 'Python', monaco: 'python' },
  { id: 'javascript', name: 'JavaScript', monaco: 'javascript' },
  { id: 'java', name: 'Java', monaco: 'java' },
  { id: 'c', name: 'C', monaco: 'c' },
  { id: 'cpp', name: 'C++', monaco: 'cpp' },
];

// -------- Type mapping from Python hints to other languages --------
const PY_TO_JAVA = { 'list': 'int[]', 'str': 'String', 'int': 'int', 'float': 'double', 'bool': 'boolean' };
const PY_TO_C    = { 'list': 'int*', 'str': 'char*', 'int': 'int', 'float': 'double', 'bool': 'int' };
const PY_TO_CPP  = { 'list': 'vector<int>', 'str': 'string', 'int': 'int', 'float': 'double', 'bool': 'bool' };
const PY_RET_JAVA = { 'list': 'int[]', 'str': 'String', 'int': 'int', 'float': 'double', 'bool': 'boolean' };
const PY_RET_CPP  = { 'list': 'vector<int>', 'str': 'string', 'int': 'int', 'float': 'double', 'bool': 'bool' };
const PY_RET_C    = { 'list': 'int*', 'str': 'char*', 'int': 'int', 'float': 'double', 'bool': 'int' };

const JAVA_DEFAULTS = { 'int': '0', 'double': '0.0', 'boolean': 'false', 'String': '""', 'int[]': 'new int[]{}' };
const C_DEFAULTS    = { 'int': '0', 'double': '0.0', 'char*': '""', 'int*': 'NULL' };
const CPP_DEFAULTS  = { 'int': '0', 'double': '0.0', 'bool': 'false', 'string': '""', 'vector<int>': '{}' };

/**
 * Parse the Python starter_code to extract function name, parameters with types, and return type.
 * e.g. "def two_sum(nums: list, target: int) -> list:" =>
 *   { funcName: 'two_sum', params: [{name:'nums',type:'list'},{name:'target',type:'int'}], returnType: 'list' }
 */
const parsePythonSignature = (starterCode) => {
  if (!starterCode) return null;
  const m = starterCode.match(/def\s+(\w+)\(([^)]*)\)\s*(?:->\s*(\w+))?/);
  if (!m) return null;
  const funcName = m[1];
  const returnType = m[3] || 'int';
  const rawParams = m[2].split(',').map(p => p.trim()).filter(Boolean);
  const params = rawParams.map(p => {
    const parts = p.split(':').map(s => s.trim());
    return { name: parts[0], type: parts[1] || 'int' };
  });
  return { funcName, params, returnType };
};

/** Generate Java starter code from parsed Python signature */
const genJava = (sig) => {
  const retType = PY_RET_JAVA[sig.returnType] || 'Object';
  const params = sig.params.map(p => `${PY_TO_JAVA[p.type] || 'Object'} ${p.name}`).join(', ');
  const defaultRet = JAVA_DEFAULTS[retType] || 'null';
  return `import java.util.*;\n\nclass Solution {\n    public ${retType} ${sig.funcName}(${params}) {\n        // Write your code here\n        return ${defaultRet};\n    }\n}`;
};

/** Generate JavaScript starter code from parsed Python signature */
const genJS = (sig) => {
  const params = sig.params.map(p => p.name).join(', ');
  return `function ${sig.funcName}(${params}) {\n    // Write your code here\n    \n}`;
};

/** Generate C starter code from parsed Python signature */
const genC = (sig) => {
  const retType = PY_RET_C[sig.returnType] || 'int';
  const paramList = [];
  sig.params.forEach(p => {
    paramList.push(`${PY_TO_C[p.type] || 'int'} ${p.name}`);
    if (p.type === 'list') paramList.push(`int ${p.name}_size`);
  });
  const defaultRet = C_DEFAULTS[retType] || '0';
  return `#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\n${retType} ${sig.funcName}(${paramList.join(', ')}) {\n    // Write your code here\n    return ${defaultRet};\n}`;
};

/** Generate C++ starter code from parsed Python signature */
const genCPP = (sig) => {
  const retType = PY_RET_CPP[sig.returnType] || 'int';
  const params = sig.params.map(p => `${PY_TO_CPP[p.type] || 'int'} ${p.name}`).join(', ');
  const defaultRet = CPP_DEFAULTS[retType] || '0';
  return `#include <iostream>\n#include <vector>\n#include <string>\n#include <algorithm>\n#include <unordered_map>\n#include <unordered_set>\nusing namespace std;\n\n${retType} ${sig.funcName}(${params}) {\n    // Write your code here\n    return ${defaultRet};\n}`;
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
  const [draftStatus, setDraftStatus] = useState(''); // 'saving', 'saved', ''
  const [submissionHistory, setSubmissionHistory] = useState([]);
  const [viewingCode, setViewingCode] = useState(null);
  const [showAIHelper, setShowAIHelper] = useState(false);
  const startTimeRef = useRef(Date.now());
  const codeByLanguage = useRef({});
  const autoSaveTimeoutRef = useRef(null);
  const keystrokeCountRef = useRef(0);
  const pasteCountRef = useRef(0);
  const pastedCharsRef = useRef(0);
  const totalTypedCharsRef = useRef(0);

  // Auto-save debounced function - saves to both API and localStorage
  const autoSave = useCallback(async (codeToSave, lang) => {
    if (!codeToSave || codeToSave.trim().length < 10) return;
    
    setDraftStatus('saving');
    
    // Always save to localStorage as backup
    const localKey = `code_draft_${problemId}`;
    localStorage.setItem(localKey, JSON.stringify({
      code: codeToSave,
      language: lang,
      updatedAt: new Date().toISOString()
    }));
    
    try {
      // Also try to save to API/MongoDB
      await saveCodeDraft(problemId, codeToSave, lang);
      setDraftStatus('saved');
      setTimeout(() => setDraftStatus(''), 2000);
    } catch (error) {
      // API failed but localStorage saved
      console.error('API auto-save failed, saved to local:', error);
      setDraftStatus('saved locally');
      setTimeout(() => setDraftStatus(''), 2000);
    }
  }, [problemId]);

  // Handle code change with debounced auto-save
  const handleCodeChange = (value) => {
    const oldLen = code.length;
    const newLen = (value || '').length;
    const diff = newLen - oldLen;
    if (diff > 0) {
      totalTypedCharsRef.current += diff;
      keystrokeCountRef.current += 1;
    }
    setCode(value);
    codeByLanguage.current[language] = value;
    
    // Clear existing timeout
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    
    // Set new timeout for auto-save (1.5 seconds after user stops typing)
    autoSaveTimeoutRef.current = setTimeout(() => {
      autoSave(value, language);
    }, 1500);
  };

  useEffect(() => {
    // Reset all state when problem changes
    setResult(null);
    setAiAnalysis(null);
    setRecommendations(null);
    setActiveTab('description');
    setLanguage('python');
    setDraftStatus('');
    setSubmissionHistory([]);
    setViewingCode(null);
    
    // Clear any pending auto-save
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    
    loadProblem();
    loadSubmissionHistory();
    startTimeRef.current = Date.now();
    codeByLanguage.current = {};
    keystrokeCountRef.current = 0;
    pasteCountRef.current = 0;
    pastedCharsRef.current = 0;
    totalTypedCharsRef.current = 0;
    
    return () => {
      // Cleanup timeout on unmount
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [problemId]);

  const loadSubmissionHistory = async () => {
    try {
      const data = await getProblemSubmissions(problemId);
      setSubmissionHistory(data.submissions || []);
    } catch (error) {
      console.error('Failed to load submission history:', error);
    }
  };

  const getStarterCode = (lang, funcName, pythonStarterCode) => {
    // If we have the Python starter_code, parse it and generate proper typed code
    const sig = parsePythonSignature(pythonStarterCode);
    if (sig) {
      switch (lang) {
        case 'python':  return pythonStarterCode;
        case 'java':    return genJava(sig);
        case 'javascript': return genJS(sig);
        case 'c':       return genC(sig);
        case 'cpp':     return genCPP(sig);
        default:        return pythonStarterCode;
      }
    }
    // Fallback if no starter_code available
    const fallback = {
      python: `def ${funcName || 'solution'}(args):\n    # Write your code here\n    pass`,
      javascript: `function ${funcName || 'solution'}(args) {\n    // Write your code here\n    \n}`,
      java: `import java.util.*;\n\nclass Solution {\n    public int ${funcName || 'solution'}(int[] args) {\n        // Write your code here\n        return 0;\n    }\n}`,
      c: `#include <stdio.h>\n#include <stdlib.h>\n\nint ${funcName || 'solution'}(int* args, int size) {\n    // Write your code here\n    return 0;\n}`,
      cpp: `#include <iostream>\n#include <vector>\nusing namespace std;\n\nint ${funcName || 'solution'}(vector<int> args) {\n    // Write your code here\n    return 0;\n}`,
    };
    return fallback[lang] || fallback.python;
  };

  const loadProblem = async () => {
    setLoading(true);
    try {
      const data = await getProblem(problemId);
      setProblem(data);
      
      // Try to load saved draft - first from API, then from localStorage
      let savedDraft = null;
      
      try {
        savedDraft = await getCodeDraft(problemId);
      } catch (error) {
        console.log('API draft fetch failed, checking localStorage');
      }
      
      // If no API draft, check localStorage
      if (!savedDraft || !savedDraft.code) {
        const localKey = `code_draft_${problemId}`;
        const localDraft = localStorage.getItem(localKey);
        if (localDraft) {
          try {
            savedDraft = JSON.parse(localDraft);
          } catch (e) {
            console.error('Failed to parse local draft:', e);
          }
        }
      }
      
      if (savedDraft && savedDraft.code) {
        // Use saved draft
        setCode(savedDraft.code);
        setLanguage(savedDraft.language || 'python');
        codeByLanguage.current = { [savedDraft.language || 'python']: savedDraft.code };
        setDraftStatus('Draft restored');
        setTimeout(() => setDraftStatus(''), 2000);
      } else {
        // Use starter code
        const starterCode = data.starter_code || getStarterCode('python', data.function_name, data.starter_code);
        setCode(starterCode);
        codeByLanguage.current = { python: starterCode };
      }
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
      const starterCode = getStarterCode(newLang, problem?.function_name, problem?.starter_code);
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
      const typingMetrics = {
        keystroke_count: keystrokeCountRef.current,
        paste_count: pasteCountRef.current,
        pasted_chars: pastedCharsRef.current,
        total_typed_chars: totalTypedCharsRef.current,
        time_spent_seconds: Math.round((Date.now() - startTimeRef.current) / 1000)
      };
      const data = await submitCode(problemId, code, timeTaken, language, typingMetrics);
      setResult(data.execution_result);
      setAiAnalysis(data.ai_analysis);
      
      // Refresh submission history after submission
      loadSubmissionHistory();
      
      // Fetch recommendations after submission
      try {
        const recs = await getRecommendations();
        setRecommendations(recs);
      } catch (e) {
        console.error('Failed to load recommendations:', e);
      }
      
      if (data.execution_result?.passed) {
        // Clear draft from localStorage on successful submission
        const localKey = `code_draft_${problemId}`;
        localStorage.removeItem(localKey);
        
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
          <button
            className={`tab ${activeTab === 'submissions' ? 'active' : ''}`}
            onClick={() => setActiveTab('submissions')}
          >
            Submissions {submissionHistory.length > 0 && `(${submissionHistory.length})`}
          </button>
        </div>

        <div className="problem-content">
          {activeTab === 'description' ? (
            <div className="description">
              <ReactMarkdown>{problem.description}</ReactMarkdown>
              
              <div className="problem-meta">
                <div className="meta-tags-row">
                  <span className="meta-tag topic-tag">📂 {problem.topic?.replace(/_/g, ' ')}</span>
                  <span className="meta-tag difficulty-tag" data-difficulty={problem.difficulty?.toLowerCase()}>
                    {problem.difficulty === 'easy' ? '🟢' : problem.difficulty === 'medium' ? '🟡' : '🔴'} {problem.difficulty}
                  </span>
                  <span className="meta-tag time-tag">⏳ {problem.expected_time_minutes} min</span>
                  <span className="meta-tag tests-tag">📝 {problem.test_cases?.length || 0} tests</span>
                </div>
                <div className="expected-complexity-badges">
                  <div className="complexity-badge-item">
                    <span className="complexity-badge-label">⏱ Expected Time Complexity</span>
                    <span className="complexity-badge-value">{problem.expected_complexity}</span>
                  </div>
                  <div className="complexity-badge-item">
                    <span className="complexity-badge-label">💾 Expected Space Complexity</span>
                    <span className="complexity-badge-value">{problem.expected_space_complexity || 'O(n)'}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : activeTab === 'result' ? (
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

                  {/* Score Breakdown */}
                  {aiAnalysis.score_breakdown && (
                    <div className="score-breakdown-section">
                      <h5>📊 Score Breakdown</h5>
                      <div className="score-breakdown-grid">
                        {[
                          { label: 'Correctness', key: 'correctness', max: 25 },
                          { label: 'Time Efficiency', key: 'time_efficiency', max: 20 },
                          { label: 'Space Efficiency', key: 'space_efficiency', max: 15 },
                          { label: 'Code Quality', key: 'code_quality_score', max: 15 },
                          { label: 'Attempt Bonus', key: 'attempt_bonus', max: 10 },
                          { label: 'Typing Speed', key: 'typing_speed_score', max: 10 },
                          { label: 'Originality', key: 'originality_score', max: 5 },
                        ].map(({ label, key, max }) => (
                          <div className="score-breakdown-item" key={key}>
                            <span className="breakdown-label">{label}</span>
                            <div className="breakdown-bar-container">
                              <div className="breakdown-bar" style={{width: `${((aiAnalysis.score_breakdown[key] || 0) / max) * 100}%`}}></div>
                            </div>
                            <span className="breakdown-value">{aiAnalysis.score_breakdown[key] ?? '-'}/{max}</span>
                          </div>
                        ))}
                      </div>
                      {aiAnalysis.score_breakdown.copy_paste_detected && (
                        <div className="copy-paste-warning">⚠️ Copy-paste detected ({aiAnalysis.score_breakdown.paste_count} paste{aiAnalysis.score_breakdown.paste_count !== 1 ? 's' : ''})</div>
                      )}
                    </div>
                  )}

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
          ) : activeTab === 'submissions' ? (
            <div className="submissions-history-tab">
              <h3>📋 Submission History</h3>
              
              {submissionHistory.length === 0 ? (
                <div className="no-submissions">
                  <p>No submissions yet for this problem.</p>
                  <p>Submit your solution to see your history here!</p>
                </div>
              ) : (
                <>
                  <table className="submissions-table">
                    <thead>
                      <tr>
                        <th>Time (IST)</th>
                        <th>Status</th>
                        <th>Score</th>
                        <th>Lang</th>
                        <th>Test Cases</th>
                        <th>Code</th>
                      </tr>
                    </thead>
                    <tbody>
                      {submissionHistory.map((sub, idx) => (
                        <tr key={idx} className={sub.passed ? 'passed-row' : 'failed-row'}>
                          <td className="time-cell">
                            {new Date(sub.submitted_at).toLocaleString('en-IN', { 
                              timeZone: 'Asia/Kolkata',
                              year: 'numeric',
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                              second: '2-digit'
                            })}
                          </td>
                          <td className={`status-cell ${sub.passed ? 'correct' : 'wrong'}`}>
                            {sub.passed ? '✅ Correct' : '❌ Wrong'}
                          </td>
                          <td className="score-cell">
                            <span className={`score-badge ${sub.score >= 80 ? 'high' : sub.score >= 50 ? 'medium' : 'low'}`}>
                              {sub.score || 0}
                            </span>
                          </td>
                          <td className="lang-cell">{sub.language || 'python'}</td>
                          <td className="tests-cell">
                            {sub.passed_count || 0} / {sub.total_count || 0}
                          </td>
                          <td className="code-cell">
                            <button 
                              className="view-code-btn"
                              onClick={() => setViewingCode(viewingCode === idx ? null : idx)}
                            >
                              {viewingCode === idx ? 'Hide' : 'View'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {/* Code Viewer Modal */}
                  {viewingCode !== null && submissionHistory[viewingCode] && (
                    <div className="code-viewer">
                      <div className="code-viewer-header">
                        <h4>Submitted Code</h4>
                        <button onClick={() => setViewingCode(null)}>✕ Close</button>
                      </div>
                      <pre className="code-content">
                        {submissionHistory[viewingCode].code || 'Code not available'}
                      </pre>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : null}
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
          {draftStatus && (
            <span className={`draft-status ${draftStatus === 'saving' ? 'saving' : 'saved'}`}>
              {draftStatus === 'saving' ? '💾 Saving...' : draftStatus === 'saved' ? '✓ Saved' : draftStatus}
            </span>
          )}
        </div>

        <div className="editor-wrapper">
          <Editor
            height="100%"
            language={LANGUAGES.find(l => l.id === language)?.monaco || 'python'}
            value={code}
            onChange={(value) => handleCodeChange(value || '')}
            theme="vs-dark"
            beforeMount={(monaco) => {
              // ---- Java autocomplete suggestions ----
              monaco.languages.registerCompletionItemProvider('java', {
                provideCompletionItems: (model, position) => {
                  const word = model.getWordUntilPosition(position);
                  const range = {
                    startLineNumber: position.lineNumber, endLineNumber: position.lineNumber,
                    startColumn: word.startColumn, endColumn: word.endColumn,
                  };
                  const suggestions = [
                    // Collections
                    { label: 'HashMap', kind: monaco.languages.CompletionItemKind.Class, insertText: 'HashMap<${1:String}, ${2:Integer}> ${3:map} = new HashMap<>();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.util.HashMap', range },
                    { label: 'ArrayList', kind: monaco.languages.CompletionItemKind.Class, insertText: 'ArrayList<${1:Integer}> ${2:list} = new ArrayList<>();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.util.ArrayList', range },
                    { label: 'HashSet', kind: monaco.languages.CompletionItemKind.Class, insertText: 'HashSet<${1:Integer}> ${2:set} = new HashSet<>();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.util.HashSet', range },
                    { label: 'LinkedList', kind: monaco.languages.CompletionItemKind.Class, insertText: 'LinkedList<${1:Integer}> ${2:list} = new LinkedList<>();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.util.LinkedList', range },
                    { label: 'Stack', kind: monaco.languages.CompletionItemKind.Class, insertText: 'Stack<${1:Integer}> ${2:stack} = new Stack<>();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.util.Stack', range },
                    { label: 'Queue', kind: monaco.languages.CompletionItemKind.Interface, insertText: 'Queue<${1:Integer}> ${2:queue} = new LinkedList<>();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.util.Queue', range },
                    { label: 'PriorityQueue', kind: monaco.languages.CompletionItemKind.Class, insertText: 'PriorityQueue<${1:Integer}> ${2:pq} = new PriorityQueue<>();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.util.PriorityQueue', range },
                    { label: 'TreeMap', kind: monaco.languages.CompletionItemKind.Class, insertText: 'TreeMap<${1:Integer}, ${2:Integer}> ${3:map} = new TreeMap<>();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.util.TreeMap', range },
                    { label: 'Deque', kind: monaco.languages.CompletionItemKind.Interface, insertText: 'Deque<${1:Integer}> ${2:deque} = new ArrayDeque<>();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.util.Deque', range },
                    // Types
                    { label: 'Integer', kind: monaco.languages.CompletionItemKind.Class, insertText: 'Integer', detail: 'java.lang.Integer', range },
                    { label: 'String', kind: monaco.languages.CompletionItemKind.Class, insertText: 'String', detail: 'java.lang.String', range },
                    { label: 'Boolean', kind: monaco.languages.CompletionItemKind.Class, insertText: 'Boolean', detail: 'java.lang.Boolean', range },
                    { label: 'Character', kind: monaco.languages.CompletionItemKind.Class, insertText: 'Character', detail: 'java.lang.Character', range },
                    { label: 'Long', kind: monaco.languages.CompletionItemKind.Class, insertText: 'Long', detail: 'java.lang.Long', range },
                    { label: 'Double', kind: monaco.languages.CompletionItemKind.Class, insertText: 'Double', detail: 'java.lang.Double', range },
                    // Common patterns
                    { label: 'for-loop', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n    $0\n}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'For loop', range },
                    { label: 'for-each', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'for (${1:int} ${2:item} : ${3:collection}) {\n    $0\n}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Enhanced for loop', range },
                    { label: 'while', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'while (${1:condition}) {\n    $0\n}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'While loop', range },
                    { label: 'if-else', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'if (${1:condition}) {\n    $0\n} else {\n    \n}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'If-else block', range },
                    // Utility methods
                    { label: 'Arrays.sort', kind: monaco.languages.CompletionItemKind.Method, insertText: 'Arrays.sort(${1:arr});', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Sort array', range },
                    { label: 'Arrays.fill', kind: monaco.languages.CompletionItemKind.Method, insertText: 'Arrays.fill(${1:arr}, ${2:val});', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Fill array', range },
                    { label: 'Collections.sort', kind: monaco.languages.CompletionItemKind.Method, insertText: 'Collections.sort(${1:list});', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Sort collection', range },
                    { label: 'Math.max', kind: monaco.languages.CompletionItemKind.Method, insertText: 'Math.max(${1:a}, ${2:b})', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Maximum of two values', range },
                    { label: 'Math.min', kind: monaco.languages.CompletionItemKind.Method, insertText: 'Math.min(${1:a}, ${2:b})', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Minimum of two values', range },
                    { label: 'StringBuilder', kind: monaco.languages.CompletionItemKind.Class, insertText: 'StringBuilder ${1:sb} = new StringBuilder();', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'java.lang.StringBuilder', range },
                    { label: 'System.out.println', kind: monaco.languages.CompletionItemKind.Method, insertText: 'System.out.println(${1:});', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Print line', range },
                    { label: 'Integer.MAX_VALUE', kind: monaco.languages.CompletionItemKind.Constant, insertText: 'Integer.MAX_VALUE', detail: '2147483647', range },
                    { label: 'Integer.MIN_VALUE', kind: monaco.languages.CompletionItemKind.Constant, insertText: 'Integer.MIN_VALUE', detail: '-2147483648', range },
                  ];
                  return { suggestions };
                }
              });
              // ---- C++ autocomplete suggestions ----
              monaco.languages.registerCompletionItemProvider('cpp', {
                provideCompletionItems: (model, position) => {
                  const word = model.getWordUntilPosition(position);
                  const range = {
                    startLineNumber: position.lineNumber, endLineNumber: position.lineNumber,
                    startColumn: word.startColumn, endColumn: word.endColumn,
                  };
                  const suggestions = [
                    { label: 'vector', kind: monaco.languages.CompletionItemKind.Class, insertText: 'vector<${1:int}> ${2:v};', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::vector', range },
                    { label: 'unordered_map', kind: monaco.languages.CompletionItemKind.Class, insertText: 'unordered_map<${1:int}, ${2:int}> ${3:mp};', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::unordered_map', range },
                    { label: 'unordered_set', kind: monaco.languages.CompletionItemKind.Class, insertText: 'unordered_set<${1:int}> ${2:s};', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::unordered_set', range },
                    { label: 'map', kind: monaco.languages.CompletionItemKind.Class, insertText: 'map<${1:int}, ${2:int}> ${3:mp};', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::map', range },
                    { label: 'set', kind: monaco.languages.CompletionItemKind.Class, insertText: 'set<${1:int}> ${2:s};', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::set', range },
                    { label: 'stack', kind: monaco.languages.CompletionItemKind.Class, insertText: 'stack<${1:int}> ${2:st};', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::stack', range },
                    { label: 'queue', kind: monaco.languages.CompletionItemKind.Class, insertText: 'queue<${1:int}> ${2:q};', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::queue', range },
                    { label: 'priority_queue', kind: monaco.languages.CompletionItemKind.Class, insertText: 'priority_queue<${1:int}> ${2:pq};', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::priority_queue', range },
                    { label: 'pair', kind: monaco.languages.CompletionItemKind.Class, insertText: 'pair<${1:int}, ${2:int}> ${3:p};', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::pair', range },
                    { label: 'sort', kind: monaco.languages.CompletionItemKind.Method, insertText: 'sort(${1:v}.begin(), ${1:v}.end());', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::sort', range },
                    { label: 'reverse', kind: monaco.languages.CompletionItemKind.Method, insertText: 'reverse(${1:v}.begin(), ${1:v}.end());', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'std::reverse', range },
                    { label: 'for-loop', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n    $0\n}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'For loop', range },
                    { label: 'for-each', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'for (auto& ${1:item} : ${2:collection}) {\n    $0\n}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Range-based for', range },
                    { label: 'INT_MAX', kind: monaco.languages.CompletionItemKind.Constant, insertText: 'INT_MAX', detail: '2147483647', range },
                    { label: 'INT_MIN', kind: monaco.languages.CompletionItemKind.Constant, insertText: 'INT_MIN', detail: '-2147483648', range },
                    { label: 'cout', kind: monaco.languages.CompletionItemKind.Method, insertText: 'cout << ${1:} << endl;', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Print output', range },
                    { label: 'make_pair', kind: monaco.languages.CompletionItemKind.Method, insertText: 'make_pair(${1:a}, ${2:b})', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Create pair', range },
                    { label: 'push_back', kind: monaco.languages.CompletionItemKind.Method, insertText: 'push_back(${1:val})', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Add to end', range },
                    { label: 'max', kind: monaco.languages.CompletionItemKind.Method, insertText: 'max(${1:a}, ${2:b})', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Maximum', range },
                    { label: 'min', kind: monaco.languages.CompletionItemKind.Method, insertText: 'min(${1:a}, ${2:b})', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, detail: 'Minimum', range },
                  ];
                  return { suggestions };
                }
              });
            }}
            onMount={(editor) => {
              editor.onDidPaste((e) => {
                pasteCountRef.current += 1;
                const pastedLen = e.range.endColumn - e.range.startColumn + (e.range.endLineNumber - e.range.startLineNumber) * 40;
                pastedCharsRef.current += Math.max(pastedLen, 1);
              });
            }}
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
            className="ai-help-btn"
            onClick={() => setShowAIHelper(true)}
          >
            🤖 AI Help
          </button>
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

      {/* AI Helper Modal */}
      {showAIHelper && (
        <AIHelper
          problemId={problemId}
          code={code}
          onClose={() => setShowAIHelper(false)}
        />
      )}
    </div>
  );
};

export default CodeEditor;
