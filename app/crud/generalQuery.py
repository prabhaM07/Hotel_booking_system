from datetime import datetime
from fastapi import HTTPException,Request
from sqlalchemy.orm import Session
from bson import ObjectId
from app.utils import convertTOString,formatDatetime
from app.core.database_mongo import chat_collection2
from app.schemas.general_query_schema import GeneralQueryResponseSchema,UserQuerySchema
from app.models.user import Users


async def create_query(query: UserQuerySchema, request: Request, db: Session):
    try:
        user = request.state.user if hasattr(request.state, "user") else None
        data = query.model_dump()

        if user is not None:
            user = db.query(Users).filter(Users.id == user.id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            data["email"] = user.email
            data["phone_no"] = user.phone_no

        data["created_at"] = datetime.now()
        data.setdefault("response", None)
        data.setdefault("response_at", None)

        result = await chat_collection2.insert_one(data)

        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create query")

        inserted_doc = await chat_collection2.find_one({"_id": result.inserted_id})

        if not inserted_doc:
            raise HTTPException(status_code=500, detail="Inserted document not found")

        inserted_doc["id"] = convertTOString(inserted_doc["_id"])
        inserted_doc["created_at"] = formatDatetime(inserted_doc["created_at"])

        return inserted_doc

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


 
    
async def get_all_queries():
    cursor = chat_collection2.find().sort("created_at", 1)
    queries = []
    async for doc in cursor:
        doc["created_at"] = formatDatetime(doc["created_at"])
        doc["response_at"] = formatDatetime(doc["response_at"])
        doc["id"] = convertTOString(doc["_id"])
        queries.append(doc)
        
    return queries


async def respond_query(query_id: str, response: GeneralQueryResponseSchema):
    if not ObjectId.is_valid(query_id):
        raise HTTPException(status_code=400, detail="Invalid query ID")

    update_data = {
        "response": response.response,
        "response_at": datetime.now()
    }

    result = await chat_collection2.update_one(
        {"_id": ObjectId(query_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Query not found")

    updated_doc = await chat_collection2.find_one({"_id": ObjectId(query_id)})
    updated_doc["id"] = convertTOString(updated_doc["_id"])
    updated_doc["created_at"] = formatDatetime(updated_doc["created_at"])
    updated_doc["response_at"] = formatDatetime(updated_doc["response_at"])
    return updated_doc
   