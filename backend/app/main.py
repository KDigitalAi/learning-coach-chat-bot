from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, onboarding
import os


app = FastAPI(
    title="Learning Coach API",
    description="AI-powered learning companion with Socratic teaching method",
    version="1.0.0"
)

# Get allowed origins from environment or default to allow all
# In production, set ALLOWED_ORIGINS in Vercel environment variables
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(onboarding.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "message": "Learning Coach API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


