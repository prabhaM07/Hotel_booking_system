from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from streamlit import status
from app.auth.auth_utils import require_scope
from app.schemas.addon_schema import AddonSchema
from app.models.addon import Addons
from app.models.user import Users
from app.core.dependency import get_db
from app.crud.generic_crud import (
    insert_record,
    search,
    update_record,
    delete_record,
    save_image,
    get_record,
)
import os
from app.crud.generic_crud import filter_record 

router = APIRouter(prefix="/addon", tags=["Addons"])

@router.post("/add", response_model=AddonSchema)
@require_scope(["addon:write"])
async def add_addon(
    request : Request,
    addon_name: str = Form(...),
    base_price: int = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    sub_static_dir = "addon_images"
    image_url = await save_image(image, sub_static_dir) if image else None

    addon_data = AddonSchema(
        addon_name=addon_name,
        base_price=base_price,
        image=image_url,
    )
    new_addon = await insert_record(
        db=db,
        model=Addons,
        **addon_data.model_dump(),
    )

    return new_addon


@router.post("/update/image", response_model=AddonSchema)
@require_scope(["addon:write"])
async def update_addon_image(
    request : Request,
    addon_id: int = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    instance = await get_record(model=Addons, db=db, id=addon_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Addon not found")

    if image:
        existing_image = instance.image
        if existing_image:
            image_path = os.path.join("app", existing_image)
            if os.path.exists(image_path):
                os.remove(image_path)

        sub_static_dir = "addon_images"
        image_url = await save_image(image, sub_static_dir)

        updated_addon = await update_record(
            id=addon_id,
            model=Addons,
            db=db,
            image=image_url,
        )
        return updated_addon

    return instance


@router.post("/update/details", response_model=AddonSchema)
@require_scope(["addon:write"])
async def update_addon_details(
    request : Request,
    addon_id: int = Form(...),
    addon_name: Optional[str] = Form(None),
    base_price: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    instance = await get_record(model=Addons, db=db, id=addon_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Addon not found")

    updated_data = {}
    if addon_name:
        updated_data["addon_name"] = addon_name
    if base_price is not None:
        updated_data["base_price"] = base_price

    updated_addon = await update_record(
        id=addon_id,
        model=Addons,
        db=db,
        **updated_data,
    )

    return updated_addon


@router.delete("/delete")
@require_scope(["addon:delete"])
async def delete_addon(
    request : Request,
    addon_id: int = Form(...),
    db: Session = Depends(get_db)
):
    deleted_addon = await delete_record(
        id=addon_id,
        model=Addons,
        db=db,
    )
    return {"message": f"Addon with ID {addon_id} deleted successfully"}


@router.get("/get", response_model=AddonSchema)
@require_scope(["addon:read"])
async def get_addon(
    request : Request,
    addon_id: int = Query(...),
    db: Session = Depends(get_db)
):
    addon = await get_record(model=Addons, db=db,id = addon_id)
    if not addon:
        raise HTTPException(status_code=404, detail="Addon not found")
    return addon

@router.get("/search")
@require_scope(["addon:read"])
def search_rooms(
    request : Request,
    q: str = Query(..., min_length=1),
    page: int = 1,
    per_page: int = 10, 
    db: Session = Depends(get_db)
):
    result = search(db=db, model=Addons, q=q, page=page, per_page=per_page)
    return result


@router.get("/filter")
@require_scope(["addon:read"])
async def filter_addons(
    request : Request,
    base_price_min: Optional[int] = Query(None, description="Minimum base price"),
    base_price_max: Optional[int] = Query(None, description="Maximum base price"),
    created_from: Optional[datetime] = Query(None, description="Filter from creation date"),
    created_to: Optional[datetime] = Query(None, description="Filter to creation date"),
    db: Session = Depends(get_db)
):
    
    dicts = {}
    
    if base_price_min:
        dicts["base_price"] = [">=", base_price_min]
    if base_price_max:
        dicts["base_price"] = ["<=", base_price_max]
    if created_from:
        dicts["created_at"] = [">=", created_from]
    if created_to:
        dicts["created_at"] = ["<=", created_to]

    if not dicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one filter parameter."
        )

    result = await filter_record(db=db, model=Addons, **dicts)
    return result