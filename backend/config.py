from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/utility_wise"

    # CORS - comma separated list of allowed origins, e.g. "https://yoursite.com,http://localhost:5500"
    allowed_origins: str = "*"

    # Admin key required to view submitted enquiries via GET /api/enquiries
    admin_api_key: str = "change-me"

    # Basic anti-spam: minimum seconds between submissions from the same IP
    rate_limit_seconds: int = 30


settings = Settings()
