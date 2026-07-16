from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # ==========================
    # AI Configuration (Groq)
    # ==========================
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # ==========================
    # Application
    # ==========================
    app_env: str = "development"
    upload_dir: str = "./data/uploads"
    db_path: str = "./data/rupeeradar.db"
    max_upload_size_mb: int = 50

    # ==========================
    # Server
    # ==========================
    backend_port: int = 8000

    # Local frontend
    frontend_url: str = "http://localhost:5173"

    # Production frontend (Vercel)
    frontend_url_prod: str = ""

    # ==========================
    # Load .env
    # ==========================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()