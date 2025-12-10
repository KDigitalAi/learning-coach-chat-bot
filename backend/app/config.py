from pydantic_settings import BaseSettings  # type: ignore
import os
from typing import Optional
from pathlib import Path

# Try to load .env file from multiple locations
try:
    from dotenv import load_dotenv  # type: ignore
    
    # Check for .env in backend directory first, then parent directory
    backend_env = Path(__file__).parent.parent / ".env"
    root_env = Path(__file__).parent.parent.parent / ".env"
    
    if backend_env.exists():
        load_dotenv(backend_env)
        print(f"✅ Loaded .env from: {backend_env}")
    elif root_env.exists():
        load_dotenv(root_env)
        print(f"✅ Loaded .env from: {root_env}")
    else:
        # Try default locations
        load_dotenv()  # This will try .env in current directory
except ImportError:
    # python-dotenv not installed, pydantic_settings will handle it
    pass


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str

    # Supabase
    supabase_url: str
    supabase_key: str  # Service role key for backend

    # Session
    session_secret_key: str = "change-this-secret-key"

    # OpenAI Models
    router_model: str = "gpt-3.5-turbo"
    speed_model: str = "gpt-3.5-turbo"
    quality_model: str = "gpt-4o"

    class Config:
        # Check for .env in multiple locations:
        # 1. backend/.env (preferred)
        # 2. ../.env (project root)
        env_file = [".env", "../.env"]
        case_sensitive = False
        # Also read from environment variables (for Vercel)
        env_file_encoding = 'utf-8'


def get_settings() -> Settings:
    """Get settings with helpful error messages for missing environment variables.
    
    Works in both local (.env file) and Vercel (environment variables) environments.
    Priority: Environment variables (Vercel) > .env file (local)
    """
    # First, try to get from environment variables directly (Vercel)
    # This handles both uppercase (OPENAI_API_KEY) and lowercase (openai_api_key)
    openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("openai_api_key")
    supabase_url = os.getenv("SUPABASE_URL") or os.getenv("supabase_url")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("supabase_key")
    
    # If all environment variables are available, use them directly
    if openai_key and supabase_url and supabase_key:
        try:
            return Settings(
                openai_api_key=openai_key,
                supabase_url=supabase_url,
                supabase_key=supabase_key
            )
        except Exception as e:
            # Fall through to error handling below
            pass
    
    # Try pydantic_settings (reads from .env file and environment)
    # The .env file should already be loaded by dotenv at the top of this file
    try:
        return Settings()
    except Exception as e:
        # Check which variables are missing
        missing_vars = []
        if not openai_key:
            missing_vars.append("OPENAI_API_KEY")
        if not supabase_url:
            missing_vars.append("SUPABASE_URL")
        if not supabase_key:
            missing_vars.append("SUPABASE_KEY")
        
        # Check which .env file exists for error message
        backend_env_path = Path(__file__).parent.parent / ".env"
        root_env_path = Path(__file__).parent.parent.parent / ".env"
        
        env_file_path = None
        if backend_env_path.exists():
            env_file_path = str(backend_env_path)
        elif root_env_path.exists():
            env_file_path = str(root_env_path)
        else:
            env_file_path = str(backend_env_path)  # Default to backend/.env

        error_msg = (
            f"\n{'=' * 60}\n"
            f"Configuration Error: Missing required environment variables\n"
            f"{'=' * 60}\n"
            f"Missing variables: {', '.join(missing_vars)}\n\n"
            f"For local development:\n"
            f"  - Create a .env file at: {env_file_path}\n"
            f"  - Or place it at: {root_env}\n"
            f"  - Add these lines:\n"
            f"    OPENAI_API_KEY=your_openai_api_key_here\n"
            f"    SUPABASE_URL=https://your-project.supabase.co\n"
            f"    SUPABASE_KEY=your_service_role_key_here\n\n"
            f"For Vercel deployment:\n"
            f"  - Go to Vercel Dashboard > Your Project > Settings > Environment Variables\n"
            f"  - Add these variables:\n"
            f"    - OPENAI_API_KEY (your OpenAI API key)\n"
            f"    - SUPABASE_URL (your Supabase project URL)\n"
            f"    - SUPABASE_KEY (your Supabase service role key)\n"
            f"  - Redeploy after adding variables\n\n"
            f"See backend/ENV_SETUP.md for setup instructions.\n"
            f"{'=' * 60}\n"
            f"Original error: {str(e)}\n"
        )
        raise ValueError(error_msg) from e


settings = get_settings()
