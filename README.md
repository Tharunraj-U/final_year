# 🧠 CodeMaster AI - Final Year Project

An AI-powered coding learning assistant with LeetCode-style problem solving and GPT-powered recommendations.

## ✨ Features

- 📝 **200+ Coding Problems** - Array, String, LinkedList, Tree, Graph, and more
- 🤖 **AI-Powered Analysis** - Get personalized feedback on your code using GPT
- 📊 **Dashboard & Statistics** - Track your progress with animated stats
- 🔥 **Streak System** - Stay motivated with daily practice streaks
- 🏆 **Achievements** - Unlock badges as you progress
- 🏅 **Leaderboard** - Compete with other users
- 🌙 **Dark Mode** - Easy on the eyes
- 🔐 **Google OAuth** - Sign in with Google
- 📧 **Weekly Reports** - Get progress reports via email

## 🚀 Quick Start

### Windows
Simply double-click `run.bat` to start both backend and frontend servers.

### Manual Setup

#### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv ../.venv

# Activate virtual environment
..\.venv\Scripts\activate  # Windows
source ../.venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example and fill in your keys)
cp .env.example .env

# Run the server
python -m app.main
```

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env file (copy from .env.example and fill in your keys)
cp .env.example .env

# Run the development server
npm start
```

## 📁 Project Structure

```
final-year-project/
├── backend/
│   ├── app/
│   │   ├── main.py           # Flask API
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   │   ├── ai_service.py      # OpenAI integration
│   │   │   ├── data_store.py      # JSON data storage
│   │   │   ├── email_service.py   # Email reports
│   │   │   └── google_oauth.py    # Google OAuth
│   │   └── utils/            # Utilities
│   ├── data/                 # JSON data files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API services
│   │   └── App.js           # Main App
│   └── package.json
├── run.bat                   # Windows startup script
└── README.md
```

## 🔧 Configuration

### Backend (.env)
```env
OPENAI_API_KEY=your_key
EMAIL_USER=your_email
EMAIL_PASS=your_app_password
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_secret
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_GOOGLE_CLIENT_ID=your_client_id
```

## 👥 Demo Users

| Username | Password |
|----------|----------|
| student_tharun | 123 |
| student_vijay | 123 |
| student_irfan | 123 |
| student_jai | 123 |

## 🛠️ Tech Stack

- **Backend**: Python, Flask, OpenAI API
- **Frontend**: React, Monaco Editor, Axios
- **Authentication**: Google OAuth, JWT
- **Database**: JSON file storage

## 📝 License

This project is part of a final year academic project.

## 👨‍💻 Author

Tharun Raj U
