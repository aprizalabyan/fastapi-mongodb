from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends

from app.schemas.product import ProductBase, ProductRead
from app.services.product_service import ProductService
from app.api.deps import get_db
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/products", dependencies=[Depends(get_current_user)])


async def get_product_service(db=Depends(get_db)):
    """Dependency to inject database into ProductService."""
    return ProductService(db)


@router.get("", response_model=List[ProductRead])
async def list_products(
    name: Optional[str] = None,
    category: Optional[str] = None,
    service: ProductService = Depends(get_product_service),
):
    return await service.list_products(name, category)


@router.post("", response_model=ProductRead, status_code=201)
async def add_product(
    payload: ProductBase,
    service: ProductService = Depends(get_product_service),
):
    return await service.add_product(payload)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service),
):
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: str,
    payload: ProductBase,
    service: ProductService = Depends(get_product_service),
):
    product = await service.update_product(product_id, payload)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    service: ProductService = Depends(get_product_service),
):
    deleted = await service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Review deleted successfully"}
