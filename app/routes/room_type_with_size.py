from datetime import datetime
from fastapi import APIRouter, Depends, Form, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.auth.auth_utils import require_scope
from app.core.dependency import get_db
from app.models.room_type import RoomTypeWithSizes
from app.models.bed_type import BedTypes
from app.models.features import Features
from app.models.roomType_bedType import RoomTypeBedTypes
from app.schemas.room_type_schema import (
    RoomTypeResponse,
    RoomTypeDetailResponse,
    RoomTypePaginatedResponse,
    RoomTypeDetailPaginatedResponse,
    RoomTypeFilterResponse,
    BulkOperationResponse,
    PaginationMeta,
    BedTypeInfo,
    FeatureInfo
)
from app.models.associations import room_type_features
from app.crud.generic_crud import (
    filter_record, get_records, insert_record, delete_record, 
    get_record, save_images, get_record_by_id, search, update_record, commit_db
)

router = APIRouter(prefix="/roomtype", tags=["Room Types"])


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


async def get_room_type_with_relations(db: Session, room_type_id: int) -> RoomTypeDetailResponse:
    room_type = await get_record(id=room_type_id, db=db, model=RoomTypeWithSizes)
    if not room_type:
        return None
    
    # Fetch bed types
    bed_type_relations = db.query(RoomTypeBedTypes).filter(
        RoomTypeBedTypes.room_type_id == room_type_id
    ).all()
    
    bed_types = []
    total_beds = 0
    for rel in bed_type_relations:
        bed_type = await get_record(id=rel.bed_type_id, db=db, model=BedTypes)
        if bed_type:
            bed_types.append(BedTypeInfo(
                id=bed_type.id,
                bed_type_name=bed_type.bed_type_name,
                num_of_beds=rel.num_of_beds
            ))
            total_beds += rel.num_of_beds
    
    feature_results = db.execute(
        room_type_features.select().where(room_type_features.c.room_type_id == room_type_id)
    ).fetchall()
    
    features = []
    for feature_rel in feature_results:
        feature = await get_record(id=feature_rel.feature_id, db=db, model=Features)
        if feature:
            features.append(FeatureInfo(
                id=feature.id,
                feature_name=feature.feature_name,
                description=getattr(feature, 'description', None)
            ))
    
    room_data = RoomTypeResponse.model_validate(room_type)
    return RoomTypeDetailResponse(
        **room_data.model_dump(),
        bed_types=bed_types,
        features=features,
        total_beds=total_beds
    )


@router.post("/add", response_model=RoomTypeDetailResponse, status_code=status.HTTP_201_CREATED)
@require_scope(["roomtype:write"])
async def add_room_type(
    request: Request,
    room_name: str = Form(...),
    room_size: int = Form(...),
    base_price_per_night: int = Form(...),
    no_of_adult: int = Form(...),
    no_of_child: int = Form(...),
    feature_ids: Optional[List[str]] = Form(None),
    bed_type_id_with_count: Optional[List[str]] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    
    image_urls = []
    if images:
        sub_static_dir = "room_type_images"
        image_urls = await save_images(images, sub_static_dir)
    
    room_type_data = RoomTypeResponse(
        room_name=room_name,
        room_size=room_size,
        base_price=base_price_per_night,
        no_of_adult=no_of_adult,
        no_of_child=no_of_child,
    )
    
    data = await insert_record(
        model=RoomTypeWithSizes,
        db=db,
        **room_type_data.model_dump(exclude={'id', 'created_at', 'updated_at'}),
        images=image_urls
    )
    
    if bed_type_id_with_count:
        room_type_bed_type = []
        for btwc in bed_type_id_with_count:
            bed_type_id, count = btwc.split(":")
            count = int(count)
            
            bed_type_instance = await get_record(db=db, model=BedTypes, id=int(bed_type_id))
            if not bed_type_instance:
                raise HTTPException(status_code=404, detail=f"Bed type with ID {bed_type_id} not found")
            
            room_type_bed_type.append({
                "bed_type_id": bed_type_instance.id,
                "num_of_beds": count,
                "room_type_id": data.id
            })
        
        for item in room_type_bed_type:
            await insert_record(db=db, model=RoomTypeBedTypes, **item)
    
    if feature_ids:
        feature_ids = feature_ids[0].split(',') if isinstance(feature_ids[0], str) else feature_ids
        
        for feature_id in feature_ids:
            feature_instance = await get_record(db=db, model=Features, id=int(feature_id))
            if not feature_instance:
                raise HTTPException(status_code=404, detail=f"Feature with ID {feature_id} not found")
            
            db.execute(room_type_features.insert().values(
                room_type_id=data.id,
                feature_id=feature_instance.id
            ))
    
    commit_db(db=db)
    
    return await get_room_type_with_relations(db, data.id)


@router.put("/update/{room_type_id}", response_model=RoomTypeDetailResponse)
@require_scope(["roomtype:write"])
async def update_room_type(
    request: Request,
    room_type_id: int,
    room_name: Optional[str] = Form(None),
    room_size: Optional[int] = Form(None),
    base_price_per_night: Optional[int] = Form(None),
    no_of_adult: Optional[int] = Form(None),
    no_of_child: Optional[int] = Form(None),
    features: Optional[List[str]] = Form(None),
    bed_types_with_count: Optional[List[str]] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """Update existing room type and its related associations"""
    
    # Fetch existing record
    room_type = await get_record_by_id(model=RoomTypeWithSizes, db=db, id=room_type_id)
    if not room_type:
        raise HTTPException(status_code=404, detail="Room type not found")

    # Collect updatable fields
    update_data = {}
    if room_name:
        update_data["room_name"] = room_name
    if room_size:
        update_data["room_size"] = room_size
    if base_price_per_night:
        update_data["base_price"] = base_price_per_night
    if no_of_adult:
        update_data["no_of_adult"] = no_of_adult
    if no_of_child:
        update_data["no_of_child"] = no_of_child

    if images:
        sub_static_dir = "room_type_images"
        image_urls = await save_images(images, sub_static_dir)
        update_data["images"] = image_urls

    if features and features != ['string']:
        features = features[0].split(',') if isinstance(features[0], str) else features
        
        db.execute(room_type_features.delete().where(
            room_type_features.c.room_type_id == room_type_id
        ))
        db.commit()
        
        for feature in features:
            feature_instance = await get_record(db=db, model=Features, id=int(feature))
            if not feature_instance:
                raise HTTPException(status_code=404, detail=f"Feature {feature} not found")
            
            db.execute(room_type_features.insert().values(
                room_type_id=room_type_id,
                feature_id=feature_instance.id
            ))
        
        db.commit()

    if bed_types_with_count and bed_types_with_count != ['string']:
        db.query(RoomTypeBedTypes).filter(
            RoomTypeBedTypes.room_type_id == room_type_id
        ).delete()
        db.commit()
        
        for btwc in bed_types_with_count:
            bed_type_name, count = btwc.split(":")
            count = int(count)
            
            bed_type = await get_record(db=db, model=BedTypes, bed_type_name=bed_type_name)
            if not bed_type:
                raise HTTPException(status_code=404, detail=f"Bed type '{bed_type_name}' not found")
            
            await insert_record(db=db, model=RoomTypeBedTypes, **{
                "bed_type_id": bed_type.id,
                "num_of_beds": count,
                "room_type_id": room_type_id
            })

    if update_data:
        await update_record(model=RoomTypeWithSizes, db=db, id=room_type_id, **update_data)

    db.commit()
    
    return await get_room_type_with_relations(db, room_type_id)


@router.delete("/delete/{room_type_id}", response_model=BulkOperationResponse)
@require_scope(["roomtype:delete"])
async def delete_room_type(
    request: Request,
    room_type_id: int,
    db: Session = Depends(get_db)
):
    """Delete a room type and its associations"""
    room_type = await get_record(id=room_type_id, db=db, model=RoomTypeWithSizes)
    if not room_type:
        raise HTTPException(status_code=404, detail="Room type not found")
    
    await delete_record(id=room_type_id, db=db, model=RoomTypeWithSizes)
    
    return BulkOperationResponse(
        success=True,
        message=f"Room type '{room_type.room_name}' deleted successfully",
        affected_count=1,
        errors=[]
    )


@router.get("/get/{room_type_id}", response_model=RoomTypeDetailResponse)
@require_scope(["roomtype:read"])
async def get_room_type(
    request: Request,
    room_type_id: int,
    db: Session = Depends(get_db)
):
    result = await get_room_type_with_relations(db, room_type_id)
    if not result:
        raise HTTPException(status_code=404, detail="Room type not found")
    return result


@router.get("/list", response_model=RoomTypeDetailPaginatedResponse)
@require_scope(["roomtype:read"])
async def list_room_types(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    include_relations: bool = Query(True, description="Include bed types and features"),
    db: Session = Depends(get_db)
):
    
    total_items = db.query(func.count(RoomTypeWithSizes.id)).scalar()
    
    offset = (page - 1) * per_page
    records = db.query(RoomTypeWithSizes).offset(offset).limit(per_page).all()
    
    if include_relations:
        data = []
        for record in records:
            detail = await get_room_type_with_relations(db, record.id)
            data.append(detail)
    else:
        data = [RoomTypeResponse.model_validate(record) for record in records]
    
    meta = create_pagination_meta(page, per_page, total_items)
    
    return RoomTypeDetailPaginatedResponse(data=data, meta=meta)


@router.get("/search", response_model=RoomTypePaginatedResponse)
@require_scope(["roomtype:read"])
async def search_room_types(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    result = search(db=db, model=RoomTypeWithSizes, q=q, page=page, per_page=per_page)
    
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
    
    return RoomTypePaginatedResponse(
        data=[RoomTypeResponse.model_validate(record) for record in data],
        meta=meta
    )

@router.get("/filter", response_model=RoomTypeFilterResponse)
@require_scope(["roomtype:read"])
async def filter_room_types(
    request: Request,
    min_room_size: Optional[int] = Query(None, description="Minimum size in BHK"),
    max_room_size: Optional[int] = Query(None, description="Maximum size in BHK"),
    min_base_price: Optional[int] = Query(None, description="Minimum base price"),
    max_base_price: Optional[int] = Query(None, description="Maximum base price"),
    min_adults: Optional[int] = Query(None, description="Minimum number of adults"),
    max_adults: Optional[int] = Query(None, description="Maximum number of adults"),
    min_children: Optional[int] = Query(None, description="Minimum number of children"),
    max_children: Optional[int] = Query(None, description="Maximum number of children"),
    created_from: Optional[datetime] = Query(None, description="Created after this date"),
    created_to: Optional[datetime] = Query(None, description="Created before this date"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Filter room types with pagination and statistics"""
    dicts = {}

    if min_room_size:
        dicts["room_size"] = [">=", min_room_size]
    if max_room_size:
        dicts["room_size"] = ["<=", max_room_size]
    if min_base_price is not None:
        dicts["base_price"] = [">=", min_base_price]
    if max_base_price is not None:
        dicts["base_price"] = ["<=", max_base_price]
    if min_adults is not None:
        dicts["no_of_adult"] = [">=", min_adults]
    if max_adults is not None:
        dicts["no_of_adult"] = ["<=", max_adults]
    if min_children is not None:
        dicts["no_of_child"] = [">=", min_children]
    if max_children is not None:
        dicts["no_of_child"] = ["<=", max_children]
    if created_from:
        dicts["created_at"] = [">=", created_from]
    if created_to:
        dicts["created_at"] = ["<=", created_to]

    if not dicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one filter parameter."
        )

    result = await filter_record(db=db, model=RoomTypeWithSizes, **dicts)
    
    if isinstance(result, list):
        total_items = len(result)
        offset = (page - 1) * per_page
        paginated_data = result[offset:offset + per_page]
    else:
        paginated_data = result.get("data", [])
        total_items = result.get("total", len(paginated_data))
    
    detailed_data = []
    for record in paginated_data:
        detail = await get_room_type_with_relations(db, record.id)
        detailed_data.append(detail)
    
    if paginated_data:
        prices = [r.base_price for r in paginated_data]
        statistics = {
            "filtered_count": total_items,
            "avg_price": sum(prices) // len(prices),
            "min_price": min(prices),
            "max_price": max(prices),
            "price_range": f"{min(prices)}-{max(prices)}"
        }
    else:
        statistics = {"filtered_count": 0}
    
    meta = create_pagination_meta(page, per_page, total_items)
    
    return RoomTypeFilterResponse(
        data=detailed_data,
        meta=meta,
        statistics=statistics
    )


@router.delete("/bulk-delete", response_model=BulkOperationResponse)
@require_scope(["roomtype:delete"])
async def bulk_delete_room_types(
    request: Request,
    room_type_ids: List[int] = Query(..., description="List of room type IDs to delete"),
    db: Session = Depends(get_db)
):
    deleted_count = 0
    errors = []
    
    for room_id in room_type_ids:
        try:
            await delete_record(db=db, model=RoomTypeWithSizes, id=room_id)
            deleted_count += 1
        except Exception as e:
            errors.append(f"Failed to delete ID {room_id}: {str(e)}")
    
    return BulkOperationResponse(
        success=len(errors) == 0,
        message=f"Deleted {deleted_count} room types",
        affected_count=deleted_count,
        errors=errors
    )