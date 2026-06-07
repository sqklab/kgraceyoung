from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.ops import Banner

router = APIRouter(prefix="/banners", tags=["banners"])

@router.get("")
def list_banners(placement: str = "home_hero", db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Banner)
        .where(Banner.placement == placement, Banner.is_active == True)  # noqa: E712
        .order_by(Banner.sort_order, Banner.created_at.desc())
    ).all()
    return [{
        "id": str(b.id), "placement": b.placement, "title": b.title, "subtitle": b.subtitle,
        "image_url": b.image_url, "link_url": b.link_url, "button_label": b.button_label,
        "sort_order": b.sort_order,
    } for b in rows]
