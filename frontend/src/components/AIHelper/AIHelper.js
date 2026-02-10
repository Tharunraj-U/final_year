import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { getAIExplanation, getAIHint, getAISolutionApproach, askAIDoubt, getAIDebugHelp } from '../../services/api';
import './AIHelper.css';

const AIHelper = ({ problemId, code, onClose }) => {
  const [activeMode, setActiveMode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [hintLevel, setHintLevel] = useState(1);
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const handleExplain = async () => {
    setLoading(true);
    setActiveMode('explain');
    try {
      const result = await getAIExplanation(problemId);
      setResponse(result);
    } catch (error) {
      setResponse({ success: false, error: error.message });
    }
    setLoading(false);
  };

  const handleHint = async () => {
    setLoading(true);
    setActiveMode('hint');
    try {
      const result = await getAIHint(problemId, hintLevel, code);
      setResponse(result);
    } catch (error) {
      setResponse({ success: false, error: error.message });
    }
    setLoading(false);
  };

  const handleApproach = async () => {
    setLoading(true);
    setActiveMode('approach');
    try {
      const result = await getAISolutionApproach(problemId);
      setResponse(result);
    } catch (error) {
      setResponse({ success: false, error: error.message });
    }
    setLoading(false);
  };

  const handleDebug = async () => {
    if (!code || code.trim().length < 10) {
      setResponse({ success: false, error: 'Please write some code first before asking for debug help.' });
      setActiveMode('debug');
      return;
    }
    setLoading(true);
    setActiveMode('debug');
    try {
      const result = await getAIDebugHelp(problemId, code);
      setResponse(result);
    } catch (error) {
      setResponse({ success: false, error: error.message });
    }
    setLoading(false);
  };

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    const userQuestion = question;
    setQuestion('');
    
    // Add user question to chat
    setChatHistory(prev => [...prev, { type: 'user', content: userQuestion }]);
    
    setLoading(true);
    setActiveMode('chat');
    try {
      const result = await askAIDoubt(problemId, userQuestion, code);
      setChatHistory(prev => [...prev, { 
        type: 'ai', 
        content: result.answer || result.error || 'Sorry, I could not answer that.'
      }]);
    } catch (error) {
      setChatHistory(prev => [...prev, { 
        type: 'ai', 
        content: 'Sorry, something went wrong. Please try again.'
      }]);
    }
    setLoading(false);
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="ai-loading">
          <div className="ai-spinner"></div>
          <p>🤖 AI is thinking...</p>
        </div>
      );
    }

    if (activeMode === 'chat') {
      return (
        <div className="ai-chat-container">
          <div className="chat-messages">
            {chatHistory.length === 0 ? (
              <div className="chat-empty">
                <p>👋 Ask me anything about this problem!</p>
                <p className="suggestions">Try asking:</p>
                <ul>
                  <li>"What data structure should I use?"</li>
                  <li>"Why is my loop not working?"</li>
                  <li>"How do I handle edge cases?"</li>
                  <li>"What's the time complexity of my approach?"</li>
                </ul>
              </div>
            ) : (
              chatHistory.map((msg, idx) => (
                <div key={idx} className={`chat-message ${msg.type}`}>
                  <div className="message-avatar">
                    {msg.type === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    {msg.type === 'ai' ? (
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    ) : (
                      <p>{msg.content}</p>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
          
          <form onSubmit={handleAskQuestion} className="chat-input-form">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask your doubt here..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !question.trim()}>
              Send
            </button>
          </form>
        </div>
      );
    }

    if (response) {
      const content = response.explanation || response.hint || response.approach || response.debug_help || response.error;
      return (
        <div className="ai-response">
          {response.success === false ? (
            <div className="ai-error">
              <p>❌ {content}</p>
            </div>
          ) : (
            <div className="ai-content">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )}
        </div>
      );
    }

    return (
      <div className="ai-welcome">
        <div className="welcome-icon">🤖</div>
        <h3>How can I help you?</h3>
        <p>Select an option from the sidebar to get started!</p>
      </div>
    );
  };

  return (
    <div className="ai-helper-overlay">
      <div className="ai-helper-modal">
        {/* Sidebar Navigation */}
        <div className="ai-helper-sidebar">
          <div className="sidebar-header">
            <h2><span>🤖</span> AI Tutor</h2>
          </div>
          
          <div className="sidebar-nav">
            <button 
              className={`nav-item ${activeMode === 'explain' ? 'active' : ''}`}
              onClick={handleExplain}
              disabled={loading}
            >
              <span className="nav-icon">📚</span> Explain Problem
            </button>
            
            <button 
              className={`nav-item ${activeMode === 'hint' ? 'active' : ''}`}
              onClick={handleHint}
              disabled={loading}
            >
              <span className="nav-icon">💡</span> Get Hint
            </button>
            
            <button 
              className={`nav-item ${activeMode === 'approach' ? 'active' : ''}`}
              onClick={handleApproach}
              disabled={loading}
            >
              <span className="nav-icon">🎯</span> Approach
            </button>
            
            <button 
              className={`nav-item ${activeMode === 'debug' ? 'active' : ''}`}
              onClick={handleDebug}
              disabled={loading}
            >
              <span className="nav-icon">🐛</span> Debug Code
            </button>
            
            <button 
              className={`nav-item ${activeMode === 'chat' ? 'active' : ''}`}
              onClick={() => { setActiveMode('chat'); setResponse(null); }}
              disabled={loading}
            >
              <span className="nav-icon">💬</span> Ask Doubt
            </button>
          </div>

          <div className="hint-level-box">
            <label>Hint Level</label>
            <select 
              value={hintLevel} 
              onChange={(e) => setHintLevel(Number(e.target.value))}
            >
              <option value={1}>1 - Gentle Nudge</option>
              <option value={2}>2 - Medium Help</option>
              <option value={3}>3 - Strong Hint</option>
            </select>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="ai-helper-main">
          <div className="main-header">
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          
          <div className="ai-helper-content">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIHelper;
