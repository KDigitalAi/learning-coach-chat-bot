# Learning Coach - AI Learning Companion

An AI-powered learning companion that uses the Socratic method to help learners truly understand concepts, not just memorize them.

## 🎯 Features

- **Socratic Teaching Method**: Encourages deep understanding through thoughtful questions
- **Dynamic Model Router**: Intelligently routes between fast (GPT-3.5) and quality (GPT-4o) models
- **Real-time Streaming**: Server-Sent Events for instant, streaming responses
- **Session-based History**: Remembers conversation context (with user consent)
- **Smart Heuristics**: Detects confusion/confidence states to adapt teaching style

## 🏗️ Architecture

### Backend (FastAPI)
- **Router Model**: GPT-3.5-turbo (fast triage)
- **Speed Model**: GPT-3.5-turbo (simple Q&A)
- **Quality Model**: GPT-4o (Socratic teaching)
- **Storage**: Supabase PostgreSQL (persistent storage)
- **Learning Patterns**: Analyzes and stores user learning behavior
- **Framework**: LangChain for AI interactions

### Frontend (React)
- Modern chat interface
- SSE client for streaming
- Onboarding/consent flow
- Responsive design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
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

4. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

4. Open the URL shown in the terminal (typically `http://localhost:5173`) in your browser

### Deployment (Vercel)

- This repository includes a `vercel.json` that builds the Vite frontend from `frontend/` and serves the SPA via `index.html` rewrites.
- Set the env var `VITE_API_BASE_URL` in Vercel to the publicly reachable backend URL (e.g. `https://your-backend-host`). Leave it blank locally to use the Vite dev proxy.
- Vercel build uses `npm ci && npm run build` inside `frontend` and publishes `frontend/dist`.

## 📚 API Endpoints

### POST `/api/onboarding/consent`
Update user consent for storing conversation history.

### POST `/api/chat`
Main chat endpoint with Dynamic Model Router.
- Accepts: `{"message": "...", "session_id": "..."}`
- Returns: Server-Sent Events stream

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

## 📝 License

MIT


