from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.auth import require_admin
from app.db.session import get_db
from app.models.ops import Banner
from app.models.user import User

router = APIRouter(prefix="/admin/banners", tags=["admin-banners"])

class BannerIn(BaseModel):
    placement: str = "home_hero"
    title: str
    subtitle: str | None = None
    image_url: str
    link_url: str | None = None
    button_label: str | None = "SHOP NOW"
    sort_order: int = 0
    is_active: bool = True

class BannerPatch(BaseModel):
    placement: str | None = None
    title: str | None = None
    subtitle: str | None = None
    image_url: str | None = None
    link_url: str | None = None
    button_label: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None

def payload(b: Banner):
    return {"id": str(b.id), "placement": b.placement, "title": b.title, "subtitle": b.subtitle, "image_url": b.image_url, "link_url": b.link_url, "button_label": b.button_label, "sort_order": b.sort_order, "is_active": b.is_active}

@router.get("")
def list_admin_banners(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return [payload(b) for b in db.scalars(select(Banner).order_by(Banner.placement, Banner.sort_order)).all()]

@router.post("", status_code=status.HTTP_201_CREATED)
def create_banner(data: BannerIn, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    b = Banner(**data.model_dump())
    db.add(b); db.commit(); db.refresh(b)
    return payload(b)

@router.patch("/{banner_id}")
def update_banner(banner_id: UUID, data: BannerPatch, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    b = db.get(Banner, banner_id)
    if not b: raise HTTPException(404, "Banner not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(b, k, v)
    db.commit(); db.refresh(b)
    return payload(b)

@router.delete("/{banner_id}")
def delete_banner(banner_id: UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    b = db.get(Banner, banner_id)
    if b:
        db.delete(b); db.commit()
    return {"ok": True}
