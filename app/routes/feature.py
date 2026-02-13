from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Request, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.auth_utils import require_scope
from app.schemas.features_schema import FeatureSchema, FeatureResponse
from app.models.features import Features
from app.models.user import Users
from app.core.dependency import get_db
from app.crud.generic_crud import (
    get_records,
    insert_record,
    search,
    update_record,
    delete_record,
    save_image,
    get_record,
    filter_record
)
import os

router = APIRouter(prefix="/feature", tags=["Features"])

MAX_IMAGE_SIZE_MB = 2 

@router.post("/add", response_model=FeatureResponse)
@require_scope(["feature:write"])
async def add_feature(
    request: Request,
    feature_name: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file is required."
        )

    contents = await image.read()
    size_mb = len(contents) / (1024 * 1024)

    if size_mb > MAX_IMAGE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image size exceeds {MAX_IMAGE_SIZE_MB} MB limit."
        )
        
    sub_static_dir = "feature_images"
    image_url = await save_image(image, sub_static_dir) if image else None
    feature_data = FeatureSchema(
        feature_name=feature_name,
        image=image_url,
    )
    new_feature = await insert_record(
        db=db,
        model=Features,
        **feature_data.model_dump(),
    )
    
    return new_feature


@router.post("/update/image", response_model=FeatureResponse)
@require_scope(["feature:write"])
async def update_feature_image(
    request: Request,
    feature_id: int = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    instance = await get_record(model=Features, db=db, id=feature_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Feature not found")

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file is required."
        )
    existing_image = instance.image
    if existing_image:
        image_path = os.path.join("app", existing_image)
        if os.path.exists(image_path):
            os.remove(image_path)

    sub_static_dir = "feature_images"
    image_url = await save_image(image, sub_static_dir)

    updated_feature = await update_record(
        id=feature_id,
        model=Features,
        db=db,
        image=image_url,
    )
    
    return updated_feature


@router.delete("/delete", response_model=Dict[str, str])
@require_scope(["feature:delete"])
async def delete_feature(
    request: Request,
    feature_id: int = Form(...),
    db: Session = Depends(get_db)
):
    deleted_feature = await delete_record(
        id=feature_id,
        model=Features,
        db=db,
    )
    return {"message": f"Feature with ID {feature_id} deleted successfully"}


@router.get("/get", response_model=FeatureResponse)
@require_scope(["feature:read"])
async def get_feature(
    request: Request,
    feature_id: int = Query(...),
    db: Session = Depends(get_db)
):
    feature = await get_record(id=feature_id, model=Features, db=db)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature


@router.get("/list", response_model=List[FeatureResponse])
@require_scope(["feature:read"])
async def list_feature(
    request: Request,
    db: Session = Depends(get_db)
):
    features = await get_records(model=Features, db=db)
    if not features:
        raise HTTPException(status_code=404, detail="Feature not found")
    return features


@router.get("/search", response_model=List[FeatureSchema])
@require_scope(["feature:read"])
def search_features(
    request: Request,
    q: str = Query(..., min_length=1),
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    result = search(db=db, model=Features, q=q, page=page, per_page=per_page)
    return [FeatureSchema.model_validate(f) for f in result]

    

@router.get("/filter", response_model=List[FeatureResponse])
@require_scope(["feature:write"])
async def filter_features(
    request: Request,
    created_from: Optional[datetime] = Query(None, description="Filter from creation date"),
    created_to: Optional[datetime] = Query(None, description="Filter to creation date"),
    db: Session = Depends(get_db)
):
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

    result = await filter_record(db=db, model=Features, **dicts)
    return result