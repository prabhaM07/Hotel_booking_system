from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, Form, Request
from sqlalchemy.orm import Session
from fastapi import status
from app.auth.auth_utils import require_scope
from app.schemas import floor_schema
from app.schemas.floor_schema import FloorBase
from app.models.floor import Floors
from app.models.user import Users
from app.core.dependency import get_db
from app.crud.generic_crud import filter_record, get_records, insert_record, search, update_record, delete_record, get_record

router = APIRouter(prefix="/floor", tags=["Floors"])

@router.post("/add", response_model=FloorBase)
@require_scope(["floor:write"])
async def add_floor(
    request: Request,
    floor_no: int = Form(...),
    db: Session = Depends(get_db)
):
    floor_data = FloorBase(floorNo=floor_no)

    new_floor = await insert_record(
        db=db,
        model=Floors,
        **floor_data.model_dump(),
    )
    return new_floor

@router.delete("/delete", response_model=Dict[str, str])
@require_scope(["floor:delete"])
async def delete_floor(
    request: Request,
    floor_no: int = Query(...),
    db: Session = Depends(get_db)
):
    record = await get_record(
        db=db,
        model=Floors,
        floor_no=floor_no
    )

    if not record:
        raise HTTPException(status_code=404, detail=f"Floor {floor_no} not found")

    await delete_record(
        db=db,
        model=Floors,
        id=record.id
    )

    return {"message": f"Floor {floor_no} deleted successfully"}


@router.get("/get", response_model=FloorBase)
@require_scope(["floor:read"])
async def get_floor(
    request: Request,
    floor_id: int = Query(...),
    db: Session = Depends(get_db)
):
    record = await get_record(
        db=db,
        model=Floors,
        id=floor_id
    )

    if not record:
        raise HTTPException(status_code=404, detail=f"Floor not found")

    return record

@router.get("/list", response_model=List[FloorBase])
@require_scope(["floor:read"])
async def list_floors(
    request: Request,
    db: Session = Depends(get_db)
):
    records = await get_records(
        db=db,
        model=Floors
    )

    if not records:
        raise HTTPException(status_code=404, detail=f"Floor not found")

    return records

@router.get("/search", response_model=List[FloorBase])
@require_scope(["floor:read"])
def search_floors(
    request: Request,
    q: str = Query(..., min_length=1),
    page: int = 1,
    per_page: int = 10, 
    db: Session = Depends(get_db)
):
    result = search(db=db, model=Floors, q=q, page=page, per_page=per_page)
    return [FloorBase.model_validate(floor) for floor in result]

@router.get("/filter", response_model=List[FloorBase])
@require_scope(["floor:write"])
async def filter_floors(
    request: Request,
    floor_no: Optional[int] = Query(None, description="Filter by floor number"),
    min_floor_no: Optional[int] = Query(None, description="Minimum floor number"),
    max_floor_no: Optional[int] = Query(None, description="Maximum floor number"),
    created_from: Optional[datetime] = Query(None, description="Filter from creation date"),
    created_to: Optional[datetime] = Query(None, description="Filter to creation date"),
    db: Session = Depends(get_db)
):
    dicts = {}

    if floor_no is not None:
        dicts["floor_no"] = ["==", floor_no]
    if min_floor_no is not None:
        dicts["floor_no"] = [">=", min_floor_no]
    if max_floor_no is not None:
        dicts["floor_no"] = ["<=", max_floor_no]

    if created_from:
        dicts["created_at"] = [">=", created_from]
    if created_to:
        dicts["created_at"] = ["<=", created_to]

    if not dicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one filter parameter."
        )
    result = await filter_record(db=db, model=Floors, **dicts)
    return result