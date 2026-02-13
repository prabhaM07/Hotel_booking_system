from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.auth.auth_utils import require_scope
from app.models.Enum import RoomStatusEnum
from app.models.rooms import Rooms
from app.models.user import Users
from app.models.room_status_history import RoomStatusHistory
from app.schemas.rooms_schema import (
    RoomsBase, 
    RoomResponse, 
    RoomListResponse, 
    RoomDetailResponse,
    RoomDeleteResponse,
    RoomSearchResponse
)
from app.core.dependency import get_db
from app.crud.generic_crud import (
    get_records, 
    insert_record, 
    update_record, 
    get_record, 
    get_record_by_id, 
    delete_record, 
    filter_record, 
    search
)
from app.schemas.status_history_schema import RoomStatusHistoryBase
from app.crud.rooms import whole_filter

router = APIRouter(prefix="/room", tags=["Rooms"])

@router.post("/add", response_model=RoomDetailResponse)
@require_scope(["room:write"])
async def add_room(
    request: Request,
    room_type_id: int = Form(...),
    floor_id: int = Form(...),
    room_no: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        room_base = RoomsBase(
            room_type_id=room_type_id,
            floor_id=floor_id,
            room_no=room_no,
            status=RoomStatusEnum.available,
        )
        room_data = await insert_record(db=db, model=Rooms, **room_base.model_dump())
        
        return RoomDetailResponse(
            success=True,
            room=RoomResponse.model_validate(room_data)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update", response_model=RoomDetailResponse)
@require_scope(["room:write"])
async def update_room(
    request: Request,
    room_id: int = Form(...),
    room_type_id: Optional[int] = Form(None),
    floor_id: Optional[int] = Form(None),
    room_no: Optional[int] = Form(None),
    status: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    existing_room = await get_record_by_id(model=Rooms, db=db, id=room_id)
    if not existing_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    update_data = {}
    old_status = existing_room.status
    
    if status and status != "string":
        try:
            new_status = RoomStatusEnum(status.lower())
            update_data["status"] = new_status
            
            if new_status != old_status:
                history_entry = RoomStatusHistoryBase(
                    room_id=room_id,
                    old_status=old_status,
                    new_status=new_status
                )
                await insert_record(db=db, model=RoomStatusHistory, **history_entry.model_dump())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid room status: {status}")
    
    if floor_id and floor_id > 0:
        update_data["floor_id"] = floor_id
    if room_type_id and room_type_id > 0:
        update_data["room_type_id"] = room_type_id
    if room_no and room_no > 0:
        update_data["room_no"] = room_no
    
    room_data = await update_record(id=room_id, db=db, model=Rooms, **update_data)
    
    return RoomDetailResponse(
        success=True,
        room=RoomResponse.model_validate(room_data)
    )


@router.delete("/delete", response_model=RoomDeleteResponse)
@require_scope(["room:delete"])
async def delete_room(
    request: Request,
    room_id: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        deleted_data = await delete_record(db=db, model=Rooms, id=room_id)
        
        return RoomDeleteResponse(
            success=True,
            message="Room deleted successfully",
            deleted_room_id=room_id
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Room not found or deletion failed: {str(e)}")


@router.get("/filter", response_model=RoomListResponse)
@require_scope(["room:write"])
async def filter_room(
    request: Request,
    room_no: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    created_from: Optional[datetime] = Query(None),
    created_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    if status:
        valid_values = [e.value for e in RoomStatusEnum]
        if status not in valid_values:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of {valid_values}."
            )

    dicts = {}
    if room_no:
        dicts["room_no"] = ["==", room_no]
    if status:
        dicts["status"] = ["==", status]
    if created_from:
        dicts["created_at"] = [">=", created_from]
    if created_to:
        dicts["created_at"] = ["<=", created_to]
    
    result = await filter_record(db=db, model=Rooms, **dicts)
    
    # Convert to response format
    rooms_list = [RoomResponse.model_validate(room) for room in result]
    
    return RoomListResponse(
        success=True,
        count=len(rooms_list),
        rooms=rooms_list
    )


@router.get("/search", response_model=RoomSearchResponse)
@require_scope(["room:read"])
def search_rooms(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    try:
        result = search(db=db, model=Rooms, q=q, page=page, per_page=per_page)
        
        if isinstance(result, dict):
            rooms_list = [RoomResponse.model_validate(room) for room in result.get("items", [])]
            total = result.get("total", 0)
            total_pages = result.get("total_pages", 0)
        else:
            rooms_list = [RoomResponse.model_validate(room) for room in result]
            total = len(rooms_list)
            total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        
        return RoomSearchResponse(
            success=True,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            rooms=rooms_list
        )
    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error searching rooms: {str(e)}"
        )


@router.get("/whole/filter", response_model=RoomListResponse)
@require_scope(["room:read"])
async def filter_advanced(
    request: Request,
    room_price: Optional[int] = Query(None),
    floor_no: Optional[int] = Query(None),
    min_room_size: Optional[int] = Query(None, description="Minimum size in BHK"),
    max_room_size: Optional[int] = Query(None, description="Maximum size in BHK"),
    no_of_child: Optional[int] = Query(None),
    no_of_adult: Optional[int] = Query(None),
    room_type_name: Optional[str] = Query(None),
    ratings: Optional[int] = Query(None),
    feature_ids: Optional[List[int]] = Query(None),
    bed_type_ids: Optional[List[int]] = Query(None),
    check_in: Optional[date] = Query(None),
    check_out: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    result = await whole_filter(
        db=db,
        room_price=room_price,
        min_room_size=min_room_size,
        max_room_size=max_room_size,
        floor_no=floor_no,
        room_type_name=room_type_name,
        ratings=ratings,
        feature_ids=feature_ids,
        bed_type_ids=bed_type_ids,
        check_in=check_in,
        check_out=check_out,
        no_of_child=no_of_child,
        no_of_adult=no_of_adult
    )
    
    rooms_list = [RoomResponse.model_validate(room) for room in result]
    
    return RoomListResponse(
        success=True,
        count=len(rooms_list),
        rooms=rooms_list
    )


@router.get("/{room_id}", response_model=RoomDetailResponse)
@require_scope(["room:read"])
async def get_room_by_id(
    request: Request,
    room_id: int,
    db: Session = Depends(get_db)
):
    room = await get_record_by_id(model=Rooms, db=db, id=room_id)
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return RoomDetailResponse(
        success=True,
        room=RoomResponse.model_validate(room)
    )


@router.get("/", response_model=RoomListResponse)
@require_scope(["room:read"])
async def get_all_rooms(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all rooms with pagination"""
    try:
        # Direct query for better control
        total_count = db.query(Rooms).count()
        rooms = db.query(Rooms).offset(skip).limit(limit).all()
        
        rooms_list = [RoomResponse.model_validate(room) for room in rooms]
        
        return RoomListResponse(
            success=True,
            count=len(rooms_list),
            rooms=rooms_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rooms: {str(e)}")