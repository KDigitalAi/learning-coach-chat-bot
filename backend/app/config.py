from pydantic_settings import BaseSettings  # type: ignore
import os


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
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow reading from environment variables even if .env file doesn't exist
        # This is important for Vercel deployment where .env file is not present


def get_settings() -> Settings:
    """Get settings with helpful error messages for missing environment variables."""
    try:
        # Try to load settings - will read from environment variables or .env file
        return Settings()
    except Exception as e:
        env_file_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        env_file_path = os.path.abspath(env_file_path)
        
        # Check if we're in Vercel (environment variables should be set)
        is_vercel = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None
        
        if is_vercel:
            error_msg = (
                f"\n{'=' * 60}\n"
                f"Configuration Error: Missing required environment variables in Vercel\n"
                f"{'=' * 60}\n"
                f"Please ensure the following environment variables are set in Vercel Dashboard:\n"
                f"  - OPENAI_API_KEY\n"
                f"  - SUPABASE_URL\n"
                f"  - SUPABASE_KEY\n"
                f"\nGo to: Vercel Dashboard → Project Settings → Environment Variables\n"
                f"{'=' * 60}\n"
                f"Original error: {str(e)}\n"
            )
        else:
            error_msg = (
                f"\n{'=' * 60}\n"
                f"Configuration Error: Missing required environment variables\n"
                f"{'=' * 60}\n"
                f"Please ensure your .env file exists at: {env_file_path}\n"
                f"And contains the following required variables:\n"
                f"  - OPENAI_API_KEY\n"
                f"  - SUPABASE_URL\n"
                f"  - SUPABASE_KEY\n"
                f"\nSee backend/ENV_SETUP.md for setup instructions.\n"
                f"{'=' * 60}\n"
                f"Original error: {str(e)}\n"
            )
        raise ValueError(error_msg) from e


# Initialize settings - this will fail fast if environment variables are missing
# This is intentional to catch configuration errors early
settings = get_settings()
