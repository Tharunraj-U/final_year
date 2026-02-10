# Deployment Guide

## Overview

This application is deployed using:
- **Backend**: Render.com (Python/Flask)
- **Frontend**: Render.com (Static Site) or Vercel
- **Database**: MongoDB Atlas (Cloud)
- **AI**: OpenAI API (GPT-4o-mini)

---

## MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a free cluster
3. Create a database user with password
4. Get the connection string (replace `<password>` with actual password)
5. Whitelist IP: 0.0.0.0/0 (for Render)

Connection String Format:
```
mongodb+srv://root:<password>@todo.mk9rmqh.mongodb.net/?appName=TODO
```

---

## Backend Deployment (Render.com)

### 1. Create a Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: codemaster-ai-backend
   - **Root Directory**: backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app --bind 0.0.0.0:$PORT`

### 2. Environment Variables

Set these in Render dashboard:

| Variable | Value |
|----------|-------|
| `MONGODB_URI` | `mongodb+srv://root:root@todo.mk9rmqh.mongodb.net/?appName=TODO` |
| `USE_OPENAI` | `true` |
| `OPENAI_API_KEY` | `your-openai-api-key` |
| `OPENAI_MODEL` | `gpt-4o-mini` |
| `GOOGLE_CLIENT_ID` | `your-google-client-id` |
| `GOOGLE_CLIENT_SECRET` | `your-google-client-secret` |
| `PYTHON_VERSION` | `3.11.0` |

---

## Frontend Deployment (Render.com)

### 1. Create a Static Site

1. Go to Render Dashboard
2. Click "New" → "Static Site"
3. Connect your GitHub repository
4. Configure:
   - **Name**: codemaster-ai-frontend
   - **Root Directory**: frontend
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build`

### 2. Environment Variables

| Variable | Value |
|----------|-------|
| `REACT_APP_API_URL` | `https://codemaster-ai-backend.onrender.com` |
| `REACT_APP_GOOGLE_CLIENT_ID` | `your-google-client-id` |

---

## Google OAuth Setup

### 1. Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Navigate to "APIs & Services" → "Credentials"
4. Create OAuth 2.0 Client ID

### 2. Configure OAuth Consent Screen

1. Set up OAuth consent screen (External)
2. Add app name, user support email, developer email
3. Add scopes: email, profile, openid

### 3. Create OAuth Client ID

1. Application type: Web application
2. Name: CodeMaster AI
3. Add Authorized JavaScript origins:
   ```
   http://localhost:3000
   https://codemaster-ai-frontend.onrender.com
   https://your-custom-domain.com
   ```
4. Add Authorized redirect URIs:
   ```
   http://localhost:3000
   https://codemaster-ai-frontend.onrender.com
   https://your-custom-domain.com
   ```

### 4. Copy Credentials

- Client ID → Use in frontend & backend
- Client Secret → Use in backend only

---

## Vercel Deployment (Alternative for Frontend)

### 1. Deploy to Vercel

```bash
cd frontend
npm install -g vercel
vercel
```

### 2. Environment Variables in Vercel

Add in Vercel Dashboard → Settings → Environment Variables:
- `REACT_APP_API_URL`: Your backend URL
- `REACT_APP_GOOGLE_CLIENT_ID`: Your Google Client ID

---

## Post-Deployment Checklist

- [ ] MongoDB connection working
- [ ] OpenAI API responding
- [ ] Google OAuth login working
- [ ] Frontend can reach backend API
- [ ] CORS configured correctly
- [ ] Environment variables set

---

## URLs After Deployment

- **Backend API**: `https://codemaster-ai-backend.onrender.com/api`
- **Frontend**: `https://codemaster-ai-frontend.onrender.com`

---

## Troubleshooting

### MongoDB Connection Issues
- Ensure IP whitelist includes 0.0.0.0/0
- Check password doesn't have special characters that need URL encoding
- Verify connection string format

### CORS Issues
- Backend should allow frontend origin
- Check CORS headers in Flask app

### Google OAuth Not Working
- Verify authorized origins include deployed URLs
- Check client ID matches in frontend and backend
