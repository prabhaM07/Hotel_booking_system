from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Form, HTTPException, Query,Request,Depends
from sqlalchemy.orm import Session
from streamlit import status
from app.models.bookings import Bookings
from app.schemas.ratings_reviews_schema import RatingsReviewsBase, RatingsReviewsResponse
from app.models.Enum import BookingStatusEnum
from app.models.rating_reviews import RatingsReviews
from app.utils import convertTOString
from app.core.dependency import get_db
from app.core.database_mongo import db
from app.crud.generic_crud import delete_record, delete_record_mongo, filter_record, get_record_by_id, get_record_mongo,insert_record_mongo,insert_record
from app.core.database_mongo import collection
from app.utils import convertTOString

router = APIRouter(prefix="/ratings_reviews", tags=["Ratings Reviews"])

@router.post("/add", response_model=RatingsReviewsResponse)
async def create_ratings_reviews(
    booking_id: int,
    ratings: RatingsReviewsBase,
    request: Request,
    db: Session = Depends(get_db)
):
    booking_instance = await get_record_by_id(id=booking_id, model=Bookings, db=db)
    
    if booking_instance.booking_status != BookingStatusEnum.COMPLETED.value:
        raise ValueError("The reviews can be enabled only after completing the stay")
    
    result = await insert_record_mongo(collection=collection, data=ratings.model_dump())
    
    dicts = {
        "booking_id": booking_instance.id,
        "room_id": booking_instance.room_id,
        "object_id": convertTOString(result["_id"])
    }
    
    ratings_reviews_instance = await insert_record(db=db, model=RatingsReviews, **dicts)
    
    return RatingsReviewsResponse.model_validate(ratings_reviews_instance)

@router.get("/{id}")
async def get_ratings_reviews(ratings_reviews_id : int, db: Session = Depends(get_db)):
    
    ratings_reviews_instance = await get_record_by_id(id = ratings_reviews_id,model = RatingsReviews,db = db)
    result = await get_record_mongo(id = ratings_reviews_instance.object_id, collection = collection)
    if not result:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return result


@router.delete("/delete")
async def delete_ratings_reviews(
    id: int,
    db: Session = Depends(get_db)
):
    ratings_reviews_instance = await get_record_by_id(
        id=id,
        model=RatingsReviews,
        db=db
    )

    if not ratings_reviews_instance:
        raise HTTPException(status_code=404, detail="Review not found in SQL database")

    print(f"Attempting to delete MongoDB record with object_id: {ratings_reviews_instance.object_id}")

    mongo_result = await delete_record_mongo(
        id=ratings_reviews_instance.object_id,
        collection=collection
    )

    if not mongo_result["deleted"]:
        error_msg = mongo_result.get("error", "MongoDB record not found")
        print(f"MongoDB deletion failed: {error_msg}")
        

        await delete_record(db=db, model=RatingsReviews, id=id)
        
        return {
            "message": "SQL record deleted, but MongoDB record was not found",
            "deleted_mongo": False,
            "deleted_sql": True,
            "warning": error_msg
        }

    await delete_record(db=db, model=RatingsReviews, id=id)

    return {
        "message": "Review deleted successfully",
        "deleted_mongo": True,
        "deleted_sql": True
    }