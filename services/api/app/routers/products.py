import uuid

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.core.errors import ApiError
from app.db.models import Product
from app.routers.deps import C
from app.schemas import ProductDetail, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(c: C, q: str | None = Query(None, max_length=100), category_id: uuid.UUID | None = None,
                  verification: str | None = Query(None, pattern="^(VERIFIED|COMMUNITY_SUBMITTED|UNVERIFIED)$"),
                  limit: int = Query(20, ge=1, le=100)) -> list[Product]:
    stmt = select(Product)
    if q:
        stmt = stmt.where(func.lower(Product.name).like(f"%{q.lower()}%"))
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    if verification:
        stmt = stmt.where(Product.verification_status == verification)
    return list(c.db.scalars(stmt.order_by(Product.name).limit(limit)))


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: uuid.UUID, c: C) -> Product:
    p = c.db.get(Product, product_id)
    if p is None:
        raise ApiError(404, "NOT_FOUND", "Product not found")
    return p
