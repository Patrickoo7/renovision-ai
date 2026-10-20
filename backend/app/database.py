from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URL, DB_NAME

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

materials_collection = db["materials"]
projects_collection = db["projects"]

def get_db():
    return db
