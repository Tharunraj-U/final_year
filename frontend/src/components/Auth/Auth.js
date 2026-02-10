import React, { useState, useEffect } from 'react';
import { login, register, googleAuth } from '../../services/api';
import './Auth.css';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

const Auth = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [googleLoaded, setGoogleLoaded] = useState(false);
  
  const [loginData, setLoginData] = useState({
    username: '',
    password: ''
  });
  
  const [registerData, setRegisterData] = useState({
    username: '',
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  // Load Google Sign-In script
  useEffect(() => {
    const loadGoogleScript = () => {
      // Check if Google script already loaded
      if (window.google?.accounts) {
        initializeGoogle();
        return;
      }
      
      // Check if script already exists
      if (document.querySelector('script[src*="accounts.google.com/gsi/client"]')) {
        // Script exists but not loaded yet, wait for it
        const checkGoogle = setInterval(() => {
          if (window.google?.accounts) {
            clearInterval(checkGoogle);
            initializeGoogle();
          }
        }, 100);
        return;
      }
      
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => {
        // Wait a bit for Google to fully initialize
        setTimeout(initializeGoogle, 100);
      };
      script.onerror = () => {
        console.error('Failed to load Google Sign-In script');
      };
      document.body.appendChild(script);
    };

    const initializeGoogle = () => {
      if (window.google?.accounts && GOOGLE_CLIENT_ID) {
        try {
          window.google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleCallback,
            auto_select: false,
            cancel_on_tap_outside: true,
          });
          setGoogleLoaded(true);
          console.log('Google Sign-In initialized successfully');
        } catch (err) {
          console.error('Failed to initialize Google Sign-In:', err);
        }
      } else if (!GOOGLE_CLIENT_ID) {
        console.warn('Google Client ID not configured');
      }
    };

    loadGoogleScript();
  }, []);

  const handleGoogleCallback = async (response) => {
    setLoading(true);
    setError(null);
    try {
      const result = await googleAuth(response.credential);
      if (result.success) {
        onLoginSuccess(result.user);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Google sign-in failed. Please try again.');
    }
    setLoading(false);
  };

  const handleGoogleSignIn = () => {
    if (window.google && googleLoaded) {
      window.google.accounts.id.prompt();
    } else {
      setError('Google Sign-In is not available. Please try again later.');
    }
  };

  const handleLoginChange = (e) => {
    setLoginData({ ...loginData, [e.target.name]: e.target.value });
    setError(null);
  };

  const handleRegisterChange = (e) => {
    setRegisterData({ ...registerData, [e.target.name]: e.target.value });
    setError(null);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await login(loginData.username, loginData.password);
      if (result.success) {
        onLoginSuccess(result.user);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    }
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (registerData.password !== registerData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const result = await register(
        registerData.username,
        registerData.name,
        registerData.email,
        registerData.password
      );
      if (result.success) {
        onLoginSuccess(result.user);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    }
    setLoading(false);
  };

  const quickLoginUsers = [
    { username: 'student_tharun', name: 'Tharun', emoji: '👨‍💻' },
    { username: 'student_vijay', name: 'Vijay', emoji: '👨‍🔬' },
    { username: 'student_irfan', name: 'Irfan', emoji: '👨‍🎓' },
    { username: 'student_jai', name: 'Jai', emoji: '🧑‍💻' },
  ];

  const handleQuickLogin = async (username) => {
    setLoading(true);
    setError(null);
    try {
      const result = await login(username, '123');
      if (result.success) {
        onLoginSuccess(result.user);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed.');
    }
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <span className="logo-icon">🧠</span>
            <h1>CodeMaster AI</h1>
          </div>
          <p className="auth-subtitle">AI-Powered Learning Assistant</p>
        </div>

        <div className="auth-tabs">
          <button
            className={`auth-tab ${isLogin ? 'active' : ''}`}
            onClick={() => { setIsLogin(true); setError(null); }}
          >
            Login
          </button>
          <button
            className={`auth-tab ${!isLogin ? 'active' : ''}`}
            onClick={() => { setIsLogin(false); setError(null); }}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="auth-error">
            ❌ {error}
          </div>
        )}

        {isLogin ? (
          <form onSubmit={handleLogin} className="auth-form">
            <div className="form-group">
              <label>Username or Email</label>
              <input
                type="text"
                name="username"
                value={loginData.username}
                onChange={handleLoginChange}
                placeholder="Enter your username"
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                name="password"
                value={loginData.password}
                onChange={handleLoginChange}
                placeholder="Enter your password"
                required
              />
            </div>
            <button type="submit" className="auth-submit" disabled={loading}>
              {loading ? '⏳ Logging in...' : '🚀 Login'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="auth-form">
            <div className="form-row">
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  name="username"
                  value={registerData.username}
                  onChange={handleRegisterChange}
                  placeholder="Choose a username"
                  required
                />
              </div>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  name="name"
                  value={registerData.name}
                  onChange={handleRegisterChange}
                  placeholder="Your full name"
                  required
                />
              </div>
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={registerData.email}
                onChange={handleRegisterChange}
                placeholder="your@email.com"
                required
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  name="password"
                  value={registerData.password}
                  onChange={handleRegisterChange}
                  placeholder="Create password"
                  required
                />
              </div>
              <div className="form-group">
                <label>Confirm Password</label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={registerData.confirmPassword}
                  onChange={handleRegisterChange}
                  placeholder="Confirm password"
                  required
                />
              </div>
            </div>
            <button type="submit" className="auth-submit" disabled={loading}>
              {loading ? '⏳ Creating account...' : '✨ Create Account'}
            </button>
          </form>
        )}

        <div className="quick-login-section">
          <div className="quick-login-divider">
            <span>or continue with</span>
          </div>
          
          {/* Google Sign-In Button */}
          <button 
            className="google-signin-btn"
            onClick={handleGoogleSignIn}
            disabled={loading || !googleLoaded}
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            <span>Sign in with Google</span>
          </button>

          <div className="quick-login-divider">
            <span>or quick login as demo user</span>
          </div>
          <div className="quick-login-users">
            {quickLoginUsers.map(user => (
              <button
                key={user.username}
                className="quick-login-btn"
                onClick={() => handleQuickLogin(user.username)}
                disabled={loading}
              >
                <span className="user-emoji">{user.emoji}</span>
                <span className="user-name">{user.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;
