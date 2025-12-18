from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    
mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB"""
    mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
    print(f"📊 Connected to MongoDB at {settings.mongodb_url}")

async def close_mongo_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("📊 MongoDB connection closed")

async def get_database():
    """Get database instance"""
    if mongodb.client is None:
        raise RuntimeError("MongoDB client is not initialized. Call connect_to_mongo() first.")
    return mongodb.client[settings.mongodb_db_name]