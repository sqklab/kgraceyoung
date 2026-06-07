from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.v1.health import router as health_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.reels import router as reels_router
from app.api.v1.auth import router as auth_router
from app.api.v1.commerce import router as commerce_router
from app.api.v1.assets import router as assets_router
from app.api.v1.shipping import router as shipping_router
from app.api.v1.payments import router as payments_router
from app.api.v1.banners import router as banners_router
from app.api.v1.admin.backoffice import router as backoffice_router

settings = get_settings()
app = FastAPI(title="Grace Young API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(commerce_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")
app.include_router(catalog_router, prefix="/api/v1")
app.include_router(reels_router, prefix="/api/v1")
app.include_router(shipping_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(banners_router, prefix="/api/v1")
app.include_router(backoffice_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"name": settings.project_name, "environment": settings.environment, "message": "K-Beauty Video Commerce API"}
