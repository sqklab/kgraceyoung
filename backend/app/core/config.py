from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # Load both backend/.env and repository-root .env.
    # Environment variables exported in the shell still take highest priority.
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    project_name: str = "Grace Young"
    environment: str = "local"
    api_origin: str = "http://localhost:8000"
    client_origin: str = "http://localhost:3000"
    admin_origin: str = "http://localhost:3001"
    allowed_origins: str = ""

    # Database / cache / queue
    database_url: str = "postgresql+psycopg://graceyoung:graceyoung@localhost:5432/graceyoung"
    redis_url: str = "redis://localhost:6379/0"
    queue_broker_url: str = "redis://localhost:6379/1"
    queue_result_backend: str = "redis://localhost:6379/2"

    # Object storage
    minio_endpoint: str = "localhost:9000"
    minio_public_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket_products: str = "grace-young-products"
    minio_bucket_reels: str = "grace-young-reels"
    minio_bucket_reviews: str = "grace-young-reviews"
    minio_secure: bool = False

    # Search
    meili_url: str = "http://localhost:7700"
    meili_master_key: str = "graceyoung_dev_master_key"

    # Mail / notification
    mail_host: str = "localhost"
    mail_port: int = 1025
    mail_from: str = "no-reply@graceyoung.local"
    mail_username: str = ""
    mail_password: str = ""

    # Auth
    jwt_secret_key: str = "CHANGE_ME_grace_young_local_dev_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    # Localization / commerce
    default_locale: str = "en"
    supported_locales: str = "en,fr,es,ko"
    default_currency: str = "USD"

    # Payment / shipping placeholders for later phases
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    easypost_api_key: str = ""
    shippo_api_key: str = ""

    @property
    def cors_origins(self) -> List[str]:
        configured = [x.strip() for x in self.allowed_origins.split(",") if x.strip()]
        defaults = [self.client_origin, self.admin_origin]
        seen = []
        for origin in configured + defaults:
            if origin and origin not in seen:
                seen.append(origin)
        return seen

    @property
    def supported_locale_list(self) -> List[str]:
        return [x.strip() for x in self.supported_locales.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
