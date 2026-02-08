import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Demo users for demonstration purposes
const DEMO_USERS = {
  'student_tharun': { name: 'Tharun', emoji: '👨‍💻' },
  'student_irfan': { name: 'Irfan', emoji: '👨‍🎓' },
  'student_jai': { name: 'Jai', emoji: '🧑‍💻' },
  'student_vijay': { name: 'Vijay', emoji: '👨‍🔬' },
};

// Get all demo users
export function getDemoUsers() {
  return DEMO_USERS;
}

// Get user ID from localStorage or generate one
export function getUserId() {
  const user = localStorage.getItem('currentUser');
  if (user) {
    try {
      return JSON.parse(user).user_id;
    } catch {
      return null;
    }
  }
  return null;
}

// Set user ID (for switching demo users)
export function setUserId(userId) {
  localStorage.setItem('userId', userId);
  return userId;
}

// Get current user from localStorage
export function getCurrentUser() {
  const user = localStorage.getItem('currentUser');
  if (user) {
    try {
      return JSON.parse(user);
    } catch {
      return null;
    }
  }
  return null;
}

// Save current user to localStorage
export function saveCurrentUser(user) {
  localStorage.setItem('currentUser', JSON.stringify(user));
}

// Clear current user from localStorage
export function clearCurrentUser() {
  localStorage.removeItem('currentUser');
  localStorage.removeItem('userId');
}

// Get current user display info
export function getCurrentUserInfo() {
  const user = getCurrentUser();
  if (user) {
    return {
      userId: user.user_id,
      name: user.name || user.user_id,
      emoji: DEMO_USERS[user.user_id]?.emoji || '👤'
    };
  }
  return null;
}

// Authentication - Login
export const login = async (username, password) => {
  const response = await api.post('/auth/login', { username, password });
  if (response.data.success) {
    saveCurrentUser(response.data.user);
  }
  return response.data;
};

// Authentication - Register
export const register = async (username, name, email, password) => {
  const response = await api.post('/auth/register', { username, name, email, password });
  if (response.data.success) {
    saveCurrentUser(response.data.user);
  }
  return response.data;
};

// Google OAuth Authentication
export const googleAuth = async (credential) => {
  const response = await api.post('/auth/google', { credential });
  if (response.data.success) {
    saveCurrentUser(response.data.user);
  }
  return response.data;
};

// Logout
export const logout = () => {
  clearCurrentUser();
};

// Check if user is logged in
export const isAuthenticated = () => {
  return getCurrentUser() !== null;
};

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Get all problems
export const getProblems = async (topic = null, difficulty = null) => {
  const params = new URLSearchParams();
  if (topic) params.append('topic', topic);
  if (difficulty) params.append('difficulty', difficulty);
  params.append('user_id', getUserId());
  
  const response = await api.get(`/problems?${params.toString()}`);
  return response.data;
};

// Get single problem
export const getProblem = async (problemId) => {
  const response = await api.get(`/problems/${problemId}?user_id=${getUserId()}`);
  return response.data;
};

// Get all topics
export const getTopics = async () => {
  const response = await api.get('/topics');
  return response.data;
};

// Run code (test without submitting)
export const runCode = async (problemId, code, language = 'python') => {
  const response = await api.post('/run', {
    problem_id: problemId,
    code: code,
    language: language,
  });
  return response.data;
};

// Submit code for evaluation and AI feedback
export const submitCode = async (problemId, code, timeTaken = 0, language = 'python') => {
  const response = await api.post('/submit', {
    user_id: getUserId(),
    problem_id: problemId,
    code: code,
    time_taken_minutes: timeTaken,
    language: language,
  });
  return response.data;
};

// Get AI recommendations
export const getRecommendations = async () => {
  const response = await api.get(`/recommendations?user_id=${getUserId()}`);
  return response.data;
};

// Get user stats
export const getUserStats = async () => {
  const response = await api.get(`/user/${getUserId()}/stats`);
  return response.data;
};

// Get submission history
export const getSubmissionHistory = async (limit = 50) => {
  const response = await api.get(`/user/${getUserId()}/history?limit=${limit}`);
  return response.data;
};

// Clear user data
export const clearUserData = async () => {
  const response = await api.delete(`/user/${getUserId()}`);
  return response.data;
};

// Add custom problem
export const addCustomProblem = async (problemData) => {
  const response = await api.post('/problems/custom', {
    ...problemData,
    user_id: getUserId()
  });
  return response.data;
};

// Get leaderboard
export const getLeaderboard = async (timeframe = 'all') => {
  try {
    const response = await api.get(`/leaderboard?timeframe=${timeframe}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching leaderboard:', error);
    // Return demo data if API fails
    return [
      { rank: 1, username: 'student_tharun', problems_solved: 42, total_score: 3850, avatar: '🦁' },
      { rank: 2, username: 'student_vijay', problems_solved: 38, total_score: 3420, avatar: '🐯' },
      { rank: 3, username: 'student_irfan', problems_solved: 35, total_score: 3180, avatar: '🐻' },
      { rank: 4, username: 'student_jai', problems_solved: 30, total_score: 2750, avatar: '🦊' },
    ];
  }
};

// Get user achievements stats
export const getUserAchievementStats = async () => {
  try {
    const response = await api.get(`/user/${getUserId()}/achievements`);
    return response.data;
  } catch (error) {
    console.error('Error fetching achievement stats:', error);
    // Return demo stats if API fails
    const stats = await getUserStats();
    return {
      problems_solved: stats.problems_solved || 0,
      streak: stats.streak || 0,
      has_perfect_score: stats.has_perfect_score || false,
      fastest_solve: stats.fastest_solve || 999,
      topics_count: stats.topics_count || 0,
      hard_solved: stats.hard_solved || 0
    };
  }
};

// Get user streak info
export const getUserStreak = async () => {
  try {
    const response = await api.get(`/user/${getUserId()}/streak`);
    return response.data;
  } catch (error) {
    console.error('Error fetching streak:', error);
    return { streak: 0, last_practice: null };
  }
};

// Get detailed stats for dashboard
export const getDetailedStats = async () => {
  try {
    const response = await api.get(`/user/${getUserId()}/detailed-stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching detailed stats:', error);
    // Return demo stats
    return {
      problems_solved: 15,
      total_submissions: 28,
      accuracy: 75,
      avg_score: 82,
      easy_solved: 8,
      medium_solved: 5,
      hard_solved: 2,
      streak: 3
    };
  }
};

// Send weekly report to user
export const sendWeeklyReport = async () => {
  const response = await api.post('/reports/send-weekly', { user_id: getUserId() });
  return response.data;
};

// Preview weekly report
export const previewWeeklyReport = async () => {
  const response = await api.get(`/reports/preview/${getUserId()}`);
  return response.data;
};

export default api;
