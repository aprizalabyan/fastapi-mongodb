from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from app.schemas.product import ProductBase, ProductRead


class ProductService:
    """Product service with MongoDB backend."""

    collection_name = "products"

    def __init__(self, db):
        """Initialize service with database instance."""
        self.db = db

    async def list_products(
        self, name: Optional[str] = None, category: Optional[str] = None
    ) -> List[ProductRead]:
        """Fetch all products from MongoDB with dynamic filters."""
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        if category:
            query["category"] = {"$regex": category, "$options": "i"}

        products = []
        async for doc in self.db[self.collection_name].find(query):
            products.append(self._doc_to_product_read(doc))
        return products

    async def add_product(self, payload: ProductBase) -> ProductRead:
        """Insert new product into MongoDB and add timestamps."""
        now = datetime.now(timezone.utc)
        data = payload.model_dump()

        data["createdAt"] = now
        data["updatedAt"] = now
        result = await self.db[self.collection_name].insert_one(data)
        data["_id"] = result.inserted_id
        return self._doc_to_product_read(data)

    async def get_product(self, product_id: str) -> Optional[ProductRead]:
        """Fetch single product by ID from MongoDB."""
        try:
            oid = ObjectId(product_id)
        except Exception:
            return None

        doc = await self.db[self.collection_name].find_one({"_id": oid})
        if doc:
            return self._doc_to_product_read(doc)
        return None

    async def delete_product(self, product_id: str) -> bool:
        """Delete a product by ID. Returns True if deleted."""
        try:
            oid = ObjectId(product_id)
        except Exception:
            return False

        result = await self.db[self.collection_name].delete_one({"_id": oid})
        return result.deleted_count == 1

    async def update_product(
        self, product_id: str, payload: ProductBase
    ) -> Optional[ProductRead]:
        """Update a product by ID. Returns updated product or None if not found."""
        try:
            oid = ObjectId(product_id)
        except Exception:
            return None

        # Only update fields that are provided (not None)
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            # If no fields provided, just return the user as-is
            return await self.get_product(product_id)

        # Add updatedAt timestamp
        update_data["updatedAt"] = datetime.now(timezone.utc)

        result = await self.db[self.collection_name].find_one_and_update(
            {"_id": oid}, {"$set": update_data}, return_document=True
        )
        if result:
            return self._doc_to_product_read(result)
        return None

    @staticmethod
    def _doc_to_product_read(doc: dict) -> ProductRead:
        """Convert MongoDB document to ProductRead schema."""
        # ensure id field exists and is a str
        doc["id"] = str(doc["_id"]) if "_id" in doc else doc.get("id")
        return ProductRead(**doc)
