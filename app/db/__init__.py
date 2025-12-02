"""Database connection using Motor (async MongoDB driver)."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import Settings

settings = Settings()

client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_to_db():
    """Initialize MongoDB connection on app startup."""
    global client, db
    client = AsyncIOMotorClient(
        settings.mongodb_uri,
        maxpoolsize=50,
        serverSelectionTimeoutMS=5000,
    )
    db = client[settings.database_name]
    try:
        await db.client.admin.command("ping")
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")


async def close_db_connection():
    """Close MongoDB connection on app shutdown."""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")
