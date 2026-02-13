from datetime import datetime
from fastapi import APIRouter, Depends, Form, Query, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.auth.auth_utils import require_scope
from app.crud.generic_crud import filter_record, get_records, search 
from app.core.dependency import get_db
from app.models.bed_type import BedTypes
from app.schemas.bed_type_schema import (
    BedTypeSchema, 
    BedTypeResponse, 
    BedTypePaginatedResponse,
    PaginationMeta,
    BedTypeFilterResponse,
    BedTypeWithRoomsResponse,
    BulkOperationResponse
)
from app.crud.generic_crud import insert_record, delete_record, get_record_by_id, get_record, update_record

router = APIRouter(prefix="/bedtype", tags=["Bed Types"])


def create_pagination_meta(page: int, per_page: int, total_items: int) -> PaginationMeta:
    total_pages = (total_items + per_page - 1) // per_page
    return PaginationMeta(
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.post("/add", response_model=BedTypeResponse, status_code=status.HTTP_201_CREATED)
@require_scope(["bedtype:write"])
async def add_bed_type(
    request: Request,
    bed_type_name: str = Form(...),
    db: Session = Depends(get_db)
):
    bed_data = BedTypeSchema(bed_type_name=bed_type_name)

    new_bed_type = await insert_record(
        db=db,
        model=BedTypes,
        **bed_data.model_dump(),
    )
    return new_bed_type


@router.delete("/delete", response_model=BulkOperationResponse)
@require_scope(["bedtype:delete"])
async def delete_bed_type(
    request: Request,
    bed_type_name: str = Query(...),
    db: Session = Depends(get_db)
):
    record = await get_record(
        db=db,
        model=BedTypes,
        bed_type_name=bed_type_name
    )

    if not record:
        raise HTTPException(status_code=404, detail="Bed type not found")

    await delete_record(
        db=db,
        model=BedTypes,
        id=record.id
    )

    return BulkOperationResponse(
        success=True,
        message=f"Bed type '{bed_type_name}' deleted successfully",
        affected_count=1,
        errors=[]
    )


@router.get("/get", response_model=BedTypeResponse)
@require_scope(["bedtype:read"])
async def get_bed_type(
    request: Request,
    bed_type_id: int = Query(..., description="ID of the bed type"),
    db: Session = Depends(get_db)
):
    """Get a single bed type by ID"""
    record = await get_record(id=bed_type_id, db=db, model=BedTypes)
    if not record:
        raise HTTPException(status_code=404, detail="Bed type not found")
    return record


@router.get("/list", response_model=BedTypePaginatedResponse)
@require_scope(["bedtype:read"])
async def list_bed_types(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get all bed types with pagination"""
    total_items = db.query(func.count(BedTypes.id)).scalar()
    
    offset = (page - 1) * per_page
    records = db.query(BedTypes).offset(offset).limit(per_page).all()
    
    meta = create_pagination_meta(page, per_page, total_items)
    
    return BedTypePaginatedResponse(
        data=[BedTypeResponse.model_validate(record) for record in records],
        meta=meta
    )


@router.get("/search", response_model=BedTypePaginatedResponse)
@require_scope(["bedtype:read"])
async def search_bed_types(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"), 
    db: Session = Depends(get_db)
):
    """Search bed types with pagination"""
    result = search(db=db, model=BedTypes, q=q, page=page, per_page=per_page)
    
    if isinstance(result, dict):
        data = result.get("data", [])
        meta = PaginationMeta(
            page=result.get("page", page),
            per_page=result.get("per_page", per_page),
            total_items=result.get("total", 0),
            total_pages=result.get("pages", 0),
            has_next=result.get("page", page) < result.get("pages", 0),
            has_prev=result.get("page", page) > 1
        )
    else:
        data = result
        total_items = len(result)
        offset = (page - 1) * per_page
        paginated_data = result[offset:offset + per_page]
        
        data = paginated_data
        meta = create_pagination_meta(page, per_page, total_items)
    
    return BedTypePaginatedResponse(
        data=[BedTypeResponse.model_validate(record) for record in data],
        meta=meta
    )


@router.get("/filter", response_model=BedTypeFilterResponse)
@require_scope(["bedtype:read"])
async def filter_bedtypes(
    request: Request,
    created_from: Optional[datetime] = Query(None, description="Filter records created after this date"),
    created_to: Optional[datetime] = Query(None, description="Filter records created before this date"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Filter bed types with pagination and statistics"""
    dicts = {}

    if created_from:
        dicts["created_at"] = [">=", created_from]
    if created_to:
        dicts["created_at"] = ["<=", created_to]

    if not dicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one filter parameter."
        )

    result = await filter_record(db=db, model=BedTypes, **dicts)
    
    if isinstance(result, list):
        total_items = len(result)
        offset = (page - 1) * per_page
        paginated_data = result[offset:offset + per_page]
    else:
        paginated_data = result.get("data", [])
        total_items = result.get("total", len(paginated_data))
    
    meta = create_pagination_meta(page, per_page, total_items)
    
    statistics = {
        "filtered_count": total_items,
        "date_range": f"{created_from or 'start'} to {created_to or 'end'}"
    }
    
    return BedTypeFilterResponse(
        data=[BedTypeResponse.model_validate(record) for record in paginated_data],
        meta=meta,
        statistics=statistics
    )

@router.delete("/bulk-delete", response_model=BulkOperationResponse)
@require_scope(["bedtype:delete"])
async def bulk_delete_bed_types(
    request: Request,
    bed_type_ids: list[int] = Query(..., description="List of bed type IDs to delete"),
    db: Session = Depends(get_db)
):
    """Delete multiple bed types at once"""
    deleted_count = 0
    errors = []
    
    for bed_id in bed_type_ids:
        try:
            await delete_record(db=db, model=BedTypes, id=bed_id)
            deleted_count += 1
        except Exception as e:
            errors.append(f"Failed to delete ID {bed_id}: {str(e)}")
    
    return BulkOperationResponse(
        success=len(errors) == 0,
        message=f"Deleted {deleted_count} bed types",
        affected_count=deleted_count,
        errors=errors
    )