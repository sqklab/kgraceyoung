from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.db.session import get_db
from app.models.catalog import Brand, Category, Product, ProductImage
from app.schemas.catalog import BrandCreate, BrandRead, CategoryCreate, CategoryRead, ProductCreate, ProductRead, ProductUpdate
from app.services.storage import upload_file
from app.api.v1.auth import require_admin
from app.models.user import User
from pathlib import Path
import tempfile

router = APIRouter(prefix="/admin/catalog", tags=["admin-catalog"])

@router.post("/categories", response_model=CategoryRead)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = Category(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.scalars(select(Category).order_by(Category.sort_order, Category.name)).all()

@router.post("/brands", response_model=BrandRead)
def create_brand(payload: BrandCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = Brand(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/brands", response_model=list[BrandRead])
def list_brands(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.scalars(select(Brand).order_by(Brand.name)).all()

@router.post("/products", response_model=ProductRead)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    data = payload.model_dump(exclude={"category_ids", "image_urls"})
    item = Product(**data)
    if payload.category_ids:
        cats = db.scalars(select(Category).where(Category.id.in_(payload.category_ids))).all()
        item.categories = cats
    for idx, url in enumerate(payload.image_urls):
        item.images.append(ProductImage(url=url, alt_text=payload.name, sort_order=idx))
    db.add(item); db.commit(); db.refresh(item)
    return db.scalar(select(Product).options(selectinload(Product.brand), selectinload(Product.categories), selectinload(Product.images)).where(Product.id == item.id))

@router.get("/products", response_model=list[ProductRead])
def list_products(limit: int = 50, offset: int = 0, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    stmt = (select(Product)
            .options(selectinload(Product.brand), selectinload(Product.categories), selectinload(Product.images))
            .order_by(Product.created_at.desc())
            .offset(offset).limit(limit))
    return db.scalars(stmt).all()

@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.scalar(select(Product).options(selectinload(Product.brand), selectinload(Product.categories), selectinload(Product.images)).where(Product.id == product_id))
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    return item

@router.patch("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: UUID, payload: ProductUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.get(Product, product_id)
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    data = payload.model_dump(exclude_unset=True, exclude={"category_ids", "image_urls"})
    for k, v in data.items():
        setattr(item, k, v)
    if payload.category_ids is not None:
        item.categories = db.scalars(select(Category).where(Category.id.in_(payload.category_ids))).all() if payload.category_ids else []
    if payload.image_urls is not None:
        item.images = [ProductImage(url=url, alt_text=item.name, sort_order=i) for i, url in enumerate(payload.image_urls)]
    db.commit()
    return db.scalar(select(Product).options(selectinload(Product.brand), selectinload(Product.categories), selectinload(Product.images)).where(Product.id == product_id))

@router.delete("/products/{product_id}")
def delete_product(product_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.get(Product, product_id)
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(item); db.commit()
    return {"deleted": str(product_id)}

@router.post("/images/upload")
async def upload_product_image(file: UploadFile = File(...), admin: User = Depends(require_admin)):
    suffix = Path(file.filename or "upload.png").suffix or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    key = f"admin-uploads/{tmp_path.stem}{suffix}"
    url = upload_file(tmp_path, key, content_type=file.content_type or "application/octet-stream")
    tmp_path.unlink(missing_ok=True)
    return {"url": url}
