from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

settings = get_settings()

client: AsyncIOMotorClient = AsyncIOMotorClient(
    settings.MONGO_URL,
    serverSelectionTimeoutMS=5000
)

db = client[settings.MONGO_DB]

chat_collection1 = db["chats"]
chat_collection2 = db["generalQuery"]
collection = db["ratings_reviews"]
collection_cm = db["content_management"]
