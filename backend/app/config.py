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
        case_sensitive = False


def get_settings() -> Settings:
    """Get settings with helpful error messages for missing environment variables."""
    try:
        return Settings()
    except Exception as e:
        env_file_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        env_file_path = os.path.abspath(env_file_path)

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


settings = get_settings()
