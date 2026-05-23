from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import SessionLocal
from app.core.config import get_settings

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    settings = get_settings()
    return {"status": "ok", "service": "grace-young-api", "environment": settings.environment}

@router.get("/health/db")
def db_health():
    with SessionLocal() as db:
        db.execute(text("select 1"))
    return {"status": "ok", "database": "reachable"}

@router.get("/health/config")
def config_health():
    """Safe configuration snapshot for local debugging. No secrets are returned."""
    settings = get_settings()
    return {
        "project_name": settings.project_name,
        "environment": settings.environment,
        "api_origin": settings.api_origin,
        "client_origin": settings.client_origin,
        "admin_origin": settings.admin_origin,
        "cors_origins": settings.cors_origins,
        "database_url_configured": bool(settings.database_url),
        "redis_url_configured": bool(settings.redis_url),
        "minio_endpoint": settings.minio_endpoint,
        "minio_public_endpoint": settings.minio_public_endpoint,
        "minio_bucket_products": settings.minio_bucket_products,
        "meili_url": settings.meili_url,
        "default_locale": settings.default_locale,
        "supported_locales": settings.supported_locale_list,
        "default_currency": settings.default_currency,
        "stripe_configured": bool(settings.stripe_secret_key),
        "paypal_configured": bool(settings.paypal_client_id),
        "easypost_configured": bool(settings.easypost_api_key),
        "shippo_configured": bool(settings.shippo_api_key),
    }
