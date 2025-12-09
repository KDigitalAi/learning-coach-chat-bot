# Learning Coach Backend

AI-powered learning companion backend with Socratic teaching method.

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
   - Create `.env` file (see `ENV_SETUP.md` for details)
   - Fill in your `OPENAI_API_KEY`
   - Add Supabase credentials (`SUPABASE_URL` and `SUPABASE_KEY`)

3. **Set up Supabase database:**
   - Create a Supabase project at https://supabase.com
   - Run the SQL schema from `backend/database/schema.sql` in Supabase SQL Editor
   - Get your project URL and service_role key from Supabase dashboard

4. **Run the server:**
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /api/onboarding/consent
Update user consent for storing conversation history.

**Request:**
```json
{
  "consent": true,
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "generated-session-id",
  "consent": true,
  "message": "Consent updated successfully"
}
```

### POST /api/chat
Main chat endpoint with Dynamic Model Router.

**Request:**
```json
{
  "message": "What is photosynthesis?",
  "session_id": "optional-session-id"
}
```

**Response:** Server-Sent Events (SSE) stream
```
data: Hello! I'm glad you're curious about photosynthesis...
data: [DONE]
```

## Architecture

- **Router Model:** GPT-3.5-turbo (fast triage)
- **Speed Model:** GPT-3.5-turbo (simple Q&A)
- **Quality Model:** GPT-4o (Socratic teaching)
- **Database:** Supabase PostgreSQL (for persistent storage)
- **Learning Patterns:** Analyzes and stores user learning behavior for personalization

The system automatically routes messages based on:
- Heuristic detection (confused/confident states)
- Router model analysis
- Complexity assessment
- Conversation history and learning patterns


