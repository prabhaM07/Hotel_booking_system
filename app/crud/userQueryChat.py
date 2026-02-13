from datetime import datetime
from app.core.database_mongo import chat_collection1 
from app.utils import convertTOString
from dateutil import parser

def _to_int(x):
    try:
        return int(x)
    except:
        return x

async def save_message(sender_id, receiver_id, message, sender_role):
    sender_id = _to_int(sender_id)
    receiver_id = _to_int(receiver_id)

    doc = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": message,
        "sender_role": sender_role.lower(),
        "timestamp": datetime.now(),
        "seen": False
    }
    res = await chat_collection1.insert_one(doc)

    inserted_id = res.inserted_id
    doc["_id"] = convertTOString(inserted_id)
    doc["timestamp"] = doc["timestamp"].isoformat()
    return doc


async def get_all_user():
    
    participants = {}

    cursor = chat_collection1.find().sort("timestamp", -1)
    async for chat in cursor:
        sid = chat.get("sender_id")
        rid = chat.get("receiver_id")
        ts = chat.get("timestamp")
        for pid in (sid, rid):
            if pid is None:
                continue
            if isinstance(pid, int) and pid > 0:
                if pid not in participants:
                    participants[pid] = {
                        "user_id": pid,
                        "last_message": chat.get("message"),
                        "last_timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                        "last_sender_role": chat.get("sender_role"),
                        "unseen_count": 0,
                        "email": None  
                    }

    unseen_cursor = chat_collection1.find({"seen": False})
    async for chat in unseen_cursor:
        sid = chat.get("sender_id")
        rid = chat.get("receiver_id")
        if isinstance(sid, int) and sid > 0 and rid == 0:
            if sid in participants:
                participants[sid]["unseen_count"] += 1

    result = list(participants.values())
    result.sort(key=lambda r: r.get("last_timestamp") or "", reverse=True)
    
    return result


async def get_chat_history(user_id: int):
    user_id = _to_int(user_id)
    cursor = chat_collection1.find(
        {
            "$or": [
                {"sender_id": user_id},
                {"receiver_id": user_id}
            ]
        }
    ).sort("timestamp", 1)  

    chats = []
    async for chat in cursor:
        if "_id" in chat:
            chat["_id"] = convertTOString(chat["_id"])
        if "timestamp" in chat and hasattr(chat["timestamp"], "isoformat"):
            chat["timestamp"] = chat["timestamp"].isoformat()
        elif "timestamp" in chat:
            chat["timestamp"] = str(chat["timestamp"])
        chats.append(chat)
    return chats


async def del_user_history(user_id: int):
    user_id = _to_int(user_id)
    result = await chat_collection1.delete_many({
        "$or": [
            {"sender_id": user_id},
            {"receiver_id": user_id}
        ]
    })
    return {"deleted_count": result.deleted_count}


async def mark_seen_until(reader_id: int, peer_id: int, max_iso_ts: str):
    
    try:
        ts = parser.isoparse(max_iso_ts)
    except Exception:
        ts = max_iso_ts

    reader_id = _to_int(reader_id)
    peer_id = _to_int(peer_id)

    query = {
        "receiver_id": reader_id,
        "sender_id": peer_id,
        "timestamp": {"$lte": ts},
        "seen": False
    }
    
    cursor = chat_collection1.find(query)
    ids = []
    async for doc in cursor:
        if "_id" in doc:
            ids.append(convertTOString(doc["_id"]))

    if ids:
        await chat_collection1.update_many(query, {"$set": {"seen": True}})

    return {"ids": ids, "count": len(ids)}


async def get_unseen_count(user_id: int):

    user_id = _to_int(user_id)
    count = await chat_collection1.count_documents({
        "sender_id": user_id,
        "receiver_id": 0,  
        "seen": False
    })
    return count


async def get_conversation_participants():
   
    senders = await chat_collection1.distinct("sender_id")
    receivers = await chat_collection1.distinct("receiver_id")
    ids = set()
    for x in senders + receivers:
        if isinstance(x, int) and x > 0:
            ids.add(x)
    return sorted(list(ids))