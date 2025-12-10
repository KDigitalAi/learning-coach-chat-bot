# Frontend

Simple HTML/CSS/JavaScript frontend for Learning Coach.

## Files

- `index.html` - Main HTML structure
- `script.js` - Application logic and API communication
- `style.css` - Styling
- `assets/` - Static assets (images, etc.)

## Local Development

Open `index.html` directly in a browser, or use a local server:

```bash
# Python
python -m http.server 8001

# Node.js
npx serve .
```

The frontend expects the backend API at `http://localhost:8000` when running locally.

## API Configuration

The frontend automatically detects the environment:
- **Local**: Uses `http://localhost:8000` for API calls
- **Production**: Uses same origin (Vercel deployment)

## Features

- Real-time chat interface with Server-Sent Events (SSE)
- Onboarding flow for user personalization
- Conversation history management
- Responsive design for mobile and desktop

