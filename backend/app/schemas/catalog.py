from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    slug: str
    name: str
    sort_order: int = 0

class CategoryCreate(CategoryBase):
    parent_id: UUID | None = None

class CategoryRead(CategoryBase):
    id: UUID
    parent_id: UUID | None = None
    class Config:
        from_attributes = True

class BrandBase(BaseModel):
    slug: str
    name: str
    country: str | None = "Korea"
    description: str | None = None
    is_active: bool = True

class BrandCreate(BrandBase):
    pass

class BrandRead(BrandBase):
    id: UUID
    class Config:
        from_attributes = True

class ProductImageRead(BaseModel):
    id: UUID
    url: str
    alt_text: str | None = None
    sort_order: int = 0
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    slug: str
    name: str
    short_description: str | None = None
    price: Decimal = Field(decimal_places=2)
    currency: str = "USD"
    status: str = "published"

class ProductCreate(ProductBase):
    brand_id: UUID | None = None
    category_ids: list[UUID] = []
    image_urls: list[str] = []

class ProductUpdate(BaseModel):
    name: str | None = None
    short_description: str | None = None
    price: Decimal | None = None
    currency: str | None = None
    status: str | None = None
    brand_id: UUID | None = None
    category_ids: list[UUID] | None = None
    image_urls: list[str] | None = None

class ProductRead(ProductBase):
    id: UUID
    brand: BrandRead | None = None
    categories: list[CategoryRead] = []
    images: list[ProductImageRead] = []
    class Config:
        from_attributes = True
