# Learning Coach - AI Learning Companion

An AI-powered learning companion that uses the Socratic method to help learners truly understand concepts, not just memorize them.

## 🎯 Features

- **Socratic Teaching Method**: Encourages deep understanding through thoughtful questions
- **Dynamic Model Router**: Intelligently routes between fast (GPT-3.5) and quality (GPT-4o) models
- **Real-time Streaming**: Server-Sent Events for instant, streaming responses
- **Session-based History**: Remembers conversation context (with user consent)
- **Smart Heuristics**: Detects confusion/confidence states to adapt teaching style

## 📁 Project Structure

```
LearningCoach/
├── backend/          # FastAPI backend application
│   ├── app/          # Main application package
│   ├── database/     # Database schemas & migrations
│   ├── data/         # Local data storage (ChromaDB)
│   └── requirements.txt
├── frontend/         # Frontend HTML/CSS/JS files
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── assets/       # Static assets (images, etc.)
├── api/              # Vercel serverless function handler
│   └── index.py
├── docs/             # Project documentation
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── LOCAL_DEVELOPMENT.md
│   ├── VERCEL_DEPLOYMENT.md
│   └── QUICK_START.md
├── vercel.json       # Vercel configuration
└── README.md         # This file
```

## 🏗️ Architecture

### Backend (FastAPI)
- **Router Model**: GPT-3.5-turbo (fast triage)
- **Speed Model**: GPT-3.5-turbo (simple Q&A)
- **Quality Model**: GPT-4o (Socratic teaching)
- **Storage**: Supabase PostgreSQL (persistent storage)
- **Learning Patterns**: Analyzes and stores user learning behavior
- **Framework**: LangChain for AI interactions

### Frontend
- Simple HTML/CSS/JavaScript interface
- SSE client for streaming responses
- Onboarding/consent flow
- Responsive design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account (free tier available)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file (see `backend/ENV_SETUP.md`):
```env
OPENAI_API_KEY=your_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
SESSION_SECRET_KEY=your_secret_key
```

4. Set up Supabase database:
   - Create project at https://supabase.com
   - Run SQL schema from `backend/database/schema.sql` in Supabase SQL Editor

5. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

The frontend is a static site. For local development:

1. Open `frontend/index.html` directly in a browser, or
2. Use a simple HTTP server:
```bash
cd frontend
python -m http.server 8001
```

The frontend expects the backend API at `http://localhost:8000` when running locally.

### Deployment

See `docs/VERCEL_DEPLOYMENT.md` for Vercel deployment instructions.

## 📚 API Endpoints

### POST `/api/onboarding/consent`
Update user consent for storing conversation history.

### POST `/api/chat`
Main chat endpoint with Dynamic Model Router.
- Accepts: `{"message": "...", "session_id": "..."}`
- Returns: Server-Sent Events stream

### GET `/health`
Health check endpoint.

## 🎓 How It Works

1. **User sends a message**
2. **Heuristic Check**: Python function detects confusion/confidence
3. **Router Model**: Determines if message needs fast or quality response
4. **Specialist Model**: 
   - **Speed**: Direct, concise answers
   - **Quality**: Socratic questions to foster understanding
5. **Response Streaming**: Tokens stream back in real-time

## 🔧 Configuration

All configuration is done via environment variables. See `backend/ENV_SETUP.md` for details.

## 📝 Documentation

- **Backend**: `backend/README.md`
- **Environment Setup**: `backend/ENV_SETUP.md`
- **Deployment**: `docs/VERCEL_DEPLOYMENT.md`
- **Local Development**: `docs/LOCAL_DEVELOPMENT.md`
- **Quick Start**: `docs/QUICK_START.md`

## 📝 License

MIT
