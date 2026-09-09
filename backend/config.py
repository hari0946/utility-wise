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

    # Gmail API notification - sends from the account you authorize (see gmail_auth.py),
    # to this address, whenever a form is submitted. Leave gmail_notify_to empty to disable.
    # These come from a one-time local OAuth flow (gmail_auth.py) - no local files needed
    # at runtime, so this works the same locally and on a cloud deploy.
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_refresh_token: str = ""
    gmail_notify_to: str = ""
    gmail_notify_name: str = ""


settings = Settings()
