from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends

from app.schemas.review import ReviewBase, ReviewRead, ReviewUpdate
from app.services.review_service import ReviewService
from app.api.deps import get_db
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/reviews", dependencies=[Depends(get_current_user)])


async def get_review_service(db=Depends(get_db)):
    """Dependency to inject database into ProductService."""
    return ReviewService(db)


@router.get("", response_model=List[ReviewRead])
async def list_reviews(
    service: ReviewService = Depends(get_review_service),
):
    return await service.list_reviews()


@router.get("/{product_id}", response_model=List[ReviewRead])
async def get_product_review(
    product_id: str,
    service: ReviewService = Depends(get_review_service),
):
    product_reviews = await service.get_product_review(product_id)
    if not product_reviews:
        raise HTTPException(status_code=404, detail="Review for this product not found")
    return product_reviews


@router.post("/{product_id}", response_model=ReviewRead, status_code=201)
async def create_review(
    product_id: str,
    review_data: ReviewBase,
    service: ReviewService = Depends(get_review_service),
    current_user=Depends(get_current_user),
):
    """Create a new review for a product. Reviewer ID and name are taken from authenticated user."""
    try:
        return await service.create_review(
            product_id=product_id,
            review_data=review_data,
            reviewer_id=current_user.id,
            reviewer_name=current_user.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: str,
    review_data: ReviewUpdate,
    service: ReviewService = Depends(get_review_service),
    current_user=Depends(get_current_user),
):
    """Update an existing review. Only the reviewer can update their own review."""
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = review_data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        updated_review = await service.update_review(
            review_id=review_id,
            review_data=update_data,
            reviewer_id=current_user.id,
        )

        if not updated_review:
            raise HTTPException(
                status_code=404,
                detail="Review not found or you don't have permission to update it"
            )

        return updated_review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    service: ReviewService = Depends(get_review_service),
    current_user=Depends(get_current_user),
):
    """Delete a review. Only the reviewer can delete their own review."""
    try:
        deleted = await service.delete_review(
            review_id=review_id,
            reviewer_id=current_user.id,
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Review not found or you don't have permission to delete it"
            )

        return {"message": "Review deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.get("/user/me", response_model=List[ReviewRead])
# async def get_my_reviews(
#     service: ReviewService = Depends(get_review_service),
#     current_user=Depends(get_current_user),
# ):
#     """Get all reviews created by the current authenticated user."""
#     return await service.get_user_reviews(current_user.id)
