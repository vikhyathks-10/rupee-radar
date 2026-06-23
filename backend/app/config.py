from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Groq AI Configuration (OpenAI-compatible API)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Application
    app_env: str = "development"
    upload_dir: str = "./data/uploads"
    db_path: str = "./data/rupeeradar.db"
    max_upload_size_mb: int = 50

    # Server
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
