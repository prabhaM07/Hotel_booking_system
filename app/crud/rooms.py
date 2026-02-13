
from datetime import date, timedelta
from typing import Type
from fastapi import HTTPException
from requests import Session
from app.models.Enum import BookingStatusEnum
from app.models.bookings import Bookings
from app.models.rooms import Rooms
from app.models.room_type import RoomTypeWithSizes
from app.models.bookings import Bookings
from app.models import Rooms, RoomTypeWithSizes, Features, RoomTypeBedTypes, BedTypes, RatingsReviews, Floors,associations
from sqlalchemy import and_
from app.core.database_mongo import collection

def check_availability(model: Type, db: Session,**kwargs):
    room_id = kwargs.get('room_id')
    check_in = kwargs.get('check_in')
    check_out = kwargs.get('check_out')
    
    if not (room_id and check_in and check_out):
        raise ValueError("room_id, check_in, and check_out are required")
    
    overlap_booking = db.query(model).filter(
        model.room_id == room_id,
        model.check_in < check_out,
        model.check_out > check_in,
        model.booking_status == BookingStatusEnum.CONFIRMED.value
    ).first()

    return overlap_booking is None
    
async def available_date_of_room(room_id : int,model: Type, db: Session):
    
    today = date.today()
    future_limit = today + timedelta(days=90) 
    

    room_booked_insances = db.query(model).filter(model.room_id == room_id , model.check_out >= today).all()
    
    if not room_booked_insances:
        raise HTTPException(status_code=404, detail="Room not found")

    all_dates = set()
    current_date = today

    while current_date <= future_limit:
        all_dates.add(current_date)
        current_date += timedelta(days=1)

    booked_dates = set()
    for rb in room_booked_insances:
        current_date = max(rb.check_in, today)
        while current_date < rb.check_out: 
            booked_dates.add(current_date)
            current_date += timedelta(days=1)
   
    available_dates = sorted(list(all_dates - booked_dates))

    if not available_dates:
        raise HTTPException(status_code=404, detail="No available dates found for this room")

    return {
        "room_id": room_id,
        "from": str(today),
        "to": str(future_limit),
        "available_dates": [str(d) for d in available_dates]
    }
      

def available_rooms(db: Session, check_in: date, check_out: date, no_of_child: int, no_of_adult: int):
    try:
        if check_in >= check_out:
            raise HTTPException(status_code=400, detail="Invalid date range")

        booked_room = (
            db.query(Bookings)
            .join(Rooms, Bookings.room_id == Rooms.id)
            .join(RoomTypeWithSizes, Rooms.room_type_id == RoomTypeWithSizes.id)
            .filter(
                Bookings.check_in < check_out,
                Bookings.check_out > check_in,
                RoomTypeWithSizes.no_of_adult >= no_of_adult,
                RoomTypeWithSizes.no_of_child >= no_of_child
            )
            .distinct()
            .all()
        )

        booked_room_ids = [r.room_id for r in booked_room]

        available_rooms_list = db.query(Rooms).filter(Rooms.id.notin_(booked_room_ids)).all()

        return {
            "available_rooms": [room.id for room in available_rooms_list],
            "count": len(available_rooms_list)
        }


    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    
async def whole_filter(
    db: Session,
    room_price=None,
    min_room_size = None,
    max_room_size = None,
    floor_no=None,
    room_type_name=None,
    ratings=None,
    feature_ids=None,
    bed_type_ids=None,
    check_in=None,
    check_out=None,
    no_of_child=None,
    no_of_adult=None
):
    query = db.query(Rooms).join(RoomTypeWithSizes, Rooms.room_type_id == RoomTypeWithSizes.id)\
                           .join(Floors, Rooms.floor_id == Floors.id)\
                           .outerjoin(RatingsReviews, RatingsReviews.room_id == Rooms.id)\
                           .outerjoin(associations.room_type_features, RoomTypeWithSizes.id == associations.room_type_features.c.room_type_id)\
                           .outerjoin(Features, associations.room_type_features.c.feature_id == Features.id)\
                           .outerjoin(RoomTypeBedTypes, RoomTypeWithSizes.id == RoomTypeBedTypes.room_type_id)\
                           .outerjoin(BedTypes, RoomTypeBedTypes.bed_type_id == BedTypes.id)

    filters = []

    if min_room_size:
        filters.append(RoomTypeWithSizes.room_size >= min_room_size)
    if max_room_size:
        filters.append(RoomTypeWithSizes.room_size <= max_room_size)
    if room_price:
        filters.append(RoomTypeWithSizes.base_price <= room_price)
    if floor_no:
        filters.append(Floors.floor_no == floor_no)
    if room_type_name:
        filters.append(RoomTypeWithSizes.room_name.ilike(f"%{room_type_name}%"))
    if ratings:

        matching_ratings = await collection.find({"rating": {"$gte": ratings}}).to_list(length=None)
        matching_object_ids = [r["_id"] for r in matching_ratings]

        ratings_review_ids = db.query(RatingsReviews.room_id).filter(
            RatingsReviews.odject_id.in_(matching_object_ids)
        ).subquery()

        filters.append(Rooms.id.in_(ratings_review_ids))

    if feature_ids:
        filters.append(Features.id.in_(feature_ids))
    if bed_type_ids:
        filters.append(BedTypes.id.in_(bed_type_ids))
    if no_of_adult:
        filters.append(RoomTypeWithSizes.no_of_adult >= no_of_adult)
    if no_of_child:
        filters.append(RoomTypeWithSizes.no_of_child >= no_of_child)

    if filters:
        query = query.filter(and_(*filters))

    if check_in and check_out:
        booked_subquery = (
            db.query(Bookings.room_id)
            .filter(
                Bookings.check_in < check_out,
                Bookings.check_out > check_in
            )
            .subquery()
        )
        query = query.filter(~Rooms.id.in_(booked_subquery))

    query = query.distinct()

    result = query.all()
    return result
