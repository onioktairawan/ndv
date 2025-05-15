from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["telegram_bot"]

async def get_session(user_id: int):
    session = await db.sessions.find_one({"user_id": user_id})
    return session

async def save_session(user_id: int, session_data: dict):
    await db.sessions.update_one(
        {"user_id": user_id},
        {"$set": {"session_data": session_data, "last_active":  __import__('datetime').datetime.utcnow()}},
        upsert=True,
    )

async def delete_session(user_id: int):
    await db.sessions.delete_one({"user_id": user_id})

async def update_last_active(user_id: int):
    await db.sessions.update_one(
        {"user_id": user_id},
        {"$set": {"last_active": __import__('datetime').datetime.utcnow()}},
    )

async def get_active_sessions_expired(expire_seconds: int):
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(seconds=expire_seconds)
    sessions = db.sessions.find({"last_active": {"$lt": cutoff}})
    return [s async for s in sessions]
