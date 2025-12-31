from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from app.schemas.review import ReviewBase, ReviewRead


class ReviewService:
    """Review service with MongoDB backend."""

    collection_name = "reviews"
    product_collection_name = "products"

    def __init__(self, db):
        """Initialize service with database instance."""
        self.db = db

    async def list_reviews(self, reviewer_id: str) -> List[ReviewRead]:
        """Fetch all reviews from MongoDB."""
        reviews = []
        async for doc in self.db[self.collection_name].find():
            tr_doc = doc.copy()
            tr_doc["isEditable"] = doc["reviewer_id"] == reviewer_id
            reviews.append(self._doc_to_review_read(tr_doc))
        return reviews

    async def get_product_review(self, product_id: str, reviewer_id: str) -> List[ReviewRead]:
        """Fetch all review by product_id from MongoDB."""
        reviews = []
        async for doc in self.db[self.collection_name].find({"product_id": product_id}):
            tr_doc = doc.copy()
            tr_doc["isEditable"] = doc["reviewer_id"] == reviewer_id
            reviews.append(self._doc_to_review_read(tr_doc))
        return reviews

    async def create_review(
        self,
        product_id: str,
        review_data: ReviewBase,
        reviewer_id: str,
        reviewer_name: str = None,
    ) -> ReviewRead:
        """Create a new review for a product with product name and reviewer name."""
        # Get product name from products collection
        try:
            product_oid = ObjectId(product_id)
        except Exception:
            raise ValueError("Invalid product_id format")

        product_doc = await self.db[self.product_collection_name].find_one(
            {"_id": product_oid}
        )
        if not product_doc:
            raise ValueError("Product not found")

        product_name = product_doc.get("name", "Unknown Product")

        # Create review data
        now = datetime.now(timezone.utc)
        data = review_data.model_dump()
        data["product_id"] = product_id
        data["reviewer_id"] = reviewer_id
        data["product_name"] = product_name
        data["reviewer_name"] = reviewer_name or "Anonymous"
        data["createdAt"] = now
        data["updatedAt"] = now

        # Insert review
        result = await self.db[self.collection_name].insert_one(data)
        data["_id"] = result.inserted_id

        # Update product's average rating
        await self._update_product_average_rating(product_id)

        return self._doc_to_review_read(data)

    async def update_review(
        self,
        review_id: str,
        review_data: dict,
        reviewer_id: str,
    ) -> Optional[ReviewRead]:
        """Update an existing review. Only the reviewer can update their own review."""
        try:
            review_oid = ObjectId(review_id)
        except Exception:
            raise ValueError("Invalid review_id format")

        # Find the review and verify ownership
        review_doc = await self.db[self.collection_name].find_one({
            "_id": review_oid,
            "reviewer_id": reviewer_id
        })

        if not review_doc:
            return None

        # Update the review
        update_data = review_data.copy()
        update_data["updatedAt"] = datetime.now(timezone.utc)

        result = await self.db[self.collection_name].update_one(
            {"_id": review_oid},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            return None

        # Get updated review
        updated_doc = await self.db[self.collection_name].find_one({"_id": review_oid})

        # Update product's average rating
        product_id = review_doc.get("product_id")
        if product_id:
            await self._update_product_average_rating(product_id)

        return self._doc_to_review_read(updated_doc)

    async def delete_review(
        self,
        review_id: str,
        reviewer_id: str,
    ) -> bool:
        """Delete a review. Only the reviewer can delete their own review."""
        try:
            review_oid = ObjectId(review_id)
        except Exception:
            raise ValueError("Invalid review_id format")

        # Find the review and verify ownership
        review_doc = await self.db[self.collection_name].find_one({
            "_id": review_oid,
            "reviewer_id": reviewer_id
        })

        if not review_doc:
            return False

        # Delete the review
        result = await self.db[self.collection_name].delete_one({"_id": review_oid})

        if result.deleted_count == 0:
            return False

        # Update product's average rating
        product_id = review_doc.get("product_id")
        if product_id:
            await self._update_product_average_rating(product_id)

        return True

    async def _update_product_average_rating(self, product_id: str):
        """Update the average rating for a product based on all its reviews."""
        try:
            product_oid = ObjectId(product_id)
        except Exception:
            return

        # Calculate average rating from all reviews for this product
        pipeline = [
            {"$match": {"product_id": product_id, "rating": {"$ne": None}}},
            {"$group": {"_id": None, "average_rating": {"$avg": "$rating"}}},
        ]

        result = (
            await self.db[self.collection_name].aggregate(pipeline).to_list(length=1)
        )

        average_rating = None
        if result:
            avg = result[0].get("average_rating")
            if avg is not None:
                # Round to nearest integer
                average_rating = round(avg)

        # Update product with new average rating
        await self.db[self.product_collection_name].update_one(
            {"_id": product_oid},
            {
                "$set": {
                    "average_rating": average_rating,
                    "updatedAt": datetime.now(timezone.utc),
                }
            },
        )

    # async def get_user_reviews(self, reviewer_id: str) -> List[ReviewRead]:
    #     """Fetch all reviews by a specific user."""
    #     reviews = []
    #     async for doc in self.db[self.collection_name].find(
    #         {"reviewer_id": reviewer_id}
    #     ):
    #         reviews.append(self._doc_to_review_read(doc))
    #     return reviews

    @staticmethod
    def _doc_to_review_read(doc: dict) -> ReviewRead:
        """Convert MongoDB document to ReviewRead schema."""
        # ensure id field exists and is a str
        doc["id"] = str(doc["_id"]) if "_id" in doc else doc.get("id")
        return ReviewRead(**doc)
