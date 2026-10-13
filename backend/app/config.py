from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "GrowthAI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/growthai"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Authentication
    AUTH_SECRET: str = Field(default="CHANGE_ME_IN_PRODUCTION")
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Rate limiting
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # AI / vLLM
    AI_PROVIDER: str = "vllm"
    VLLM_BASE_URL: str = "http://localhost:8000/v1"
    VLLM_API_KEY: str = ""
    VLLM_MODEL: str = ""

    # PayPal
    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_CLIENT_SECRET: str = ""
    PAYPAL_WEBHOOK_ID: str = ""
    PAYPAL_BASE_URL: str = "https://api-m.sandbox.paypal.com"

    # Google OAuth / Calendar
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    # WhatsApp
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_API_VERSION: str = ""
    WHATSAPP_APP_SECRET: str = ""

    # Email / SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    EMAIL_FROM_NAME: str = "GrowthAI"

    # Voice
    VOICE_API_KEY: str = ""
    VOICE_ACCOUNT_SID: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.APP_ENV.strip().lower() in {"production", "prod"}:
            secret = self.AUTH_SECRET.strip()

            if secret == "CHANGE_ME_IN_PRODUCTION" or len(secret) < 32:
                raise ValueError(
                    "Production requires a strong AUTH_SECRET of at least 32 characters."
                )

            if self.APP_DEBUG:
                raise ValueError("APP_DEBUG must be false in production.")

            default_database_url = (
                "postgresql+asyncpg://postgres:postgres@localhost:5432/growthai"
            )
            if not self.DATABASE_URL.strip() or (
                self.DATABASE_URL.strip() == default_database_url
            ):
                raise ValueError(
                    "Production requires an explicit DATABASE_URL; "
                    "the development database default cannot be used."
                )

            origins = self.cors_origins_list
            if not origins or any(
                origin.strip().lower().startswith(
                    (
                        "http://localhost",
                        "https://localhost",
                        "http://127.0.0.1",
                        "https://127.0.0.1",
                        "http://0.0.0.0",
                        "https://0.0.0.0",
                    )
                )
                for origin in origins
            ):
                raise ValueError(
                    "Production CORS_ORIGINS must contain real frontend origins, "
                    "not localhost addresses."
                )

        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
