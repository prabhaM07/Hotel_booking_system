import os
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, File, Form, HTTPException, Body, Request, UploadFile
from datetime import datetime
from pydantic import EmailStr
from app.auth.auth_utils import require_scope
from app.core.database_mongo import collection_cm
from app.crud.generic_crud import save_image, save_images
from app.crud.terms_conditions_assist import store_terms_to_pinecone,ask_question
from app.schemas.content_management_schema import TermsAndConditions

router = APIRouter(prefix="/content_management", tags=["Content Management"])


@router.put("/terms_conditions/update")
@require_scope(["scope:write"])
async def update_terms_conditions(request : Request , data: TermsAndConditions = Body(...)):
    """
    Update or insert Terms and Conditions in MongoDB content management collection.
    """
    try:
        data_dict = data.model_dump()
        data_dict["last_updated"] = datetime.now()

        existing_doc = await collection_cm.find_one({"terms_and_conditions": {"$exists": True}})
       
        if existing_doc:
            result = await collection_cm.update_one(
                {"_id": existing_doc["_id"]},
                {"$set": {"terms_and_conditions": data_dict, "updated_at": datetime.utcnow()}}
            )
            await store_terms_to_pinecone()
        

            return {"message": "Terms and Conditions updated successfully."}

        else:
            new_doc = {
                "terms_and_conditions": data_dict,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            insert_result = await collection_cm.insert_one(new_doc)
            await store_terms_to_pinecone()
            
            return {
                "message": "Terms and Conditions created successfully.",
                "id": str(insert_result.inserted_id)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/terms_conditions")
@require_scope(["scope:read"])
async def get_terms_conditions(request : Request):
    """
    Retrieve the latest Terms and Conditions document from MongoDB.
    """
    try:
        existing_doc = await collection_cm.find_one({"terms_and_conditions": {"$exists": True}})

        if not existing_doc or "terms_and_conditions" not in existing_doc:
            raise HTTPException(status_code=404, detail="Terms and Conditions not found")

        return existing_doc["terms_and_conditions"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ask_terms")
@require_scope(["scope:read"])
async def ask_terms(question: str, request: Request):
    
    
    response = ask_question(question=question)
    
    return {"answer": response}


@router.post("/carousel/add")
@require_scope(["scope:write"])
async def add_carousel_image(
    request : Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    order: int = Form(...),
    is_active: bool = Form(True),
    images: Optional[List[UploadFile]] = File(None),
):
    try:
        sub_static_dir = "carousel_images"
        image_urls = []
        
        image_urls = await save_images(images, sub_static_dir)

        new_doc = {
            "title": title,
            "description": description,
            "images": image_urls,
            "order": order,
            "is_active": is_active,
        }

        insert_result = await collection_cm.insert_one(new_doc)

        return {
            "message": "Carousel image added successfully",
            "id": str(insert_result.inserted_id),
            "data": new_doc
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.get("/carousel/")
@require_scope(["scope:read"])
async def get_all_carousel_images(request : Request):
    try:
        docs = await collection_cm.find().to_list(None)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return {"count": len(docs), "data": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.patch("/carousel/update/{carousel_id}")
@require_scope(["scope:write"])
async def update_carousel_image(
    request : Request,
    carousel_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    order: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
):
    try:
        existing = await collection_cm.find_one({"_id": ObjectId(carousel_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Carousel image not found")

        updated_fields = {}
        if title is not None:
            updated_fields["title"] = title
        if description is not None:
            updated_fields["description"] = description
        if order is not None:
            updated_fields["order"] = order
        if is_active is not None:
            updated_fields["is_active"] = is_active

        if images:
            sub_static_dir = "carousel_images"
            existing_images = existing.get("images", [])
            for existing_image in existing_images:
                if existing_image:
                    image_path = os.path.join("app", existing_image)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    
            new_image_urls = await save_images(images, sub_static_dir)
            updated_fields["images"] = new_image_urls

        if not updated_fields:
            raise HTTPException(status_code=400, detail="No fields provided to update")

        await collection_cm.update_one(
            {"_id": ObjectId(carousel_id)}, {"$set": updated_fields}
        )

        updated_doc = await collection_cm.find_one({"_id": ObjectId(carousel_id)})
        updated_doc["_id"] = str(updated_doc["_id"])

        return {"message": "Carousel updated successfully", "data": updated_doc}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/carousel/delete/{carousel_id}")
@require_scope(["scope:delete"])
async def delete_carousel_image(request : Request,carousel_id: str):
    try:
        existing = await collection_cm.find_one({"_id": ObjectId(carousel_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Carousel image not found")

        existing_images = existing.get("images", [])
        for existing_image in existing_images:
            if existing_image:
                image_path = os.path.join("app", existing_image)
                if os.path.exists(image_path):
                    os.remove(image_path)
                        
        await collection_cm.delete_one({"_id": ObjectId(carousel_id)})

        return {"message": "Carousel image deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/management/add")
@require_scope(["scope:write"])
async def add_management_member(
    request : Request,
    name: str = Form(...),
    position: str = Form(...),
    order: int = Form(...),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
):
    try:
        sub_static_dir = "management_team_images"
        image_url = await save_image(image, sub_static_dir) if image else None

        new_doc = {
            "name": name,
            "position": position,
            "image": image_url,
            "order": order,
            "is_active": is_active,
        }

        insert_result = await collection_cm.insert_one(new_doc)

        return {
            "message": "Management team member added successfully",
            "id": str(insert_result.inserted_id),
            "data": new_doc,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/management/")
@require_scope(["scope:read"])
async def get_all_management_members(request : Request):
    try:
        docs = await collection_cm.find().to_list(None)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return {"count": len(docs), "data": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/management/update/{member_id}")
@require_scope(["scope:write"])
async def update_management_member(
    request : Request,
    member_id: str,
    name: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    order: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    try:
        existing = await collection_cm.find_one({"_id": ObjectId(member_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Management team member not found")

        updated_fields = {}
        if name is not None:
            updated_fields["name"] = name
        if position is not None:
            updated_fields["position"] = position
        if order is not None:
            updated_fields["order"] = order
        if is_active is not None:
            updated_fields["is_active"] = is_active

        if image:
            sub_static_dir = "management_team_images"
            
            existing_image = existing.get("image", [])
            if existing_image:
                image_path = os.path.join("app", existing_image)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    
            new_image_url = await save_image(image, sub_static_dir)
            updated_fields["images"] = new_image_url

        if not updated_fields:
            raise HTTPException(status_code=400, detail="No fields provided to update")

        await collection_cm.update_one(
            {"_id": ObjectId(member_id)}, {"$set": updated_fields}
        )

        updated_doc = await collection_cm.find_one({"_id": ObjectId(member_id)})
        updated_doc["_id"] = str(updated_doc["_id"])

        return {"message": "Management team member updated successfully", "data": updated_doc}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/management/delete/{member_id}")
@require_scope(["scope:delete"])
async def delete_management_member(request : Request,member_id: str):
    try:
        existing = await collection_cm.find_one({"_id": ObjectId(member_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Management team member not found")

        existing_image = existing.get("image", [])
        if existing_image:
            image_path = os.path.join("app", existing_image)
            if os.path.exists(image_path):
                os.remove(image_path)
                
        await collection_cm.delete_one({"_id": ObjectId(member_id)})

        return {"message": "Management team member deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/contact/add")
@require_scope(["scope:write"])
async def add_contact_details(
    request : Request,
    email: EmailStr = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: Optional[str] = Form(None),
    country: str = Form(...),
    LinkedIn: Optional[str] = Form(None),
    twitter: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
):
    try:
        new_doc = {
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "country": country,
            "LinkedIn": LinkedIn,
            "twitter": twitter,
            "zip_code": zip_code,
        }

        insert_result = await collection_cm.insert_one(new_doc)

        return {
            "message": "Contact details added successfully",
            "id": str(insert_result.inserted_id),
            "data": new_doc,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contact/")
@require_scope(["scope:read"])
async def get_all_contact_details(request : Request):
    try:
        docs = await collection_cm.find().to_list(None)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return {"count": len(docs), "data": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/contact/update/{contact_id}")
@require_scope(["scope:write"])
async def update_contact_details(
    request : Request,
    contact_id: str,
    email: Optional[EmailStr] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    LinkedIn: Optional[str] = Form(None),
    twitter: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
):
    try:
        existing = await collection_cm.find_one({"_id": ObjectId(contact_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Contact details not found")

        updated_fields = {}
        if email is not None:
            updated_fields["email"] = email
        if phone is not None:
            updated_fields["phone"] = phone
        if address is not None:
            updated_fields["address"] = address
        if city is not None:
            updated_fields["city"] = city
        if state is not None:
            updated_fields["state"] = state
        if country is not None:
            updated_fields["country"] = country
        if LinkedIn is not None:
            updated_fields["LinkedIn"] = LinkedIn
        if twitter is not None:
            updated_fields["twitter"] = twitter
        if zip_code is not None:
            updated_fields["zip_code"] = zip_code

        if not updated_fields:
            raise HTTPException(status_code=400, detail="No fields provided to update")

        await collection_cm.update_one(
            {"_id": ObjectId(contact_id)}, {"$set": updated_fields}
        )

        updated_doc = await collection_cm.find_one({"_id": ObjectId(contact_id)})
        updated_doc["_id"] = str(updated_doc["_id"])

        return {"message": "Contact details updated successfully", "data": updated_doc}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/contact/delete/{contact_id}")
@require_scope(["scope:delete"])
async def delete_contact_details(request : Request,contact_id: str):
    try:
        existing = await collection_cm.find_one({"_id": ObjectId(contact_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Contact details not found")

        await collection_cm.delete_one({"_id": ObjectId(contact_id)})

        return {"message": "Contact details deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.post("/founder/add")
@require_scope(["scope:write"])
async def add_founder_info(
    request : Request,
    name: str = Form(...),
    title: str = Form(...),
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    try:
        sub_static_dir = "founder_images"
        image_url = await save_image(image, sub_static_dir) if image else None

        new_doc = {
            "name": name,
            "title": title,
            "message": message,
            "image": image,
        }

        insert_result = await collection_cm.insert_one(new_doc)

        return {
            "message": "Founder info added successfully",
            "id": str(insert_result.inserted_id),
            "data": new_doc,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/founder/")
@require_scope(["scope:read"])
async def get_all_founders(request : Request):
    try:
        docs = await collection_cm.find().to_list(None)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return {"count": len(docs), "data": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/founder/update/{founder_id}")
@require_scope(["scope:write"])
async def update_founder_info(
    request : Request,
    founder_id: str,
    name: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    try:
        existing = await collection_cm.find_one({"_id": ObjectId(founder_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Founder info not found")

        updated_fields = {}
        if name is not None:
            updated_fields["name"] = name
        if title is not None:
            updated_fields["title"] = title
        if message is not None:
            updated_fields["message"] = message

        if image:
            sub_static_dir = "founder_images"
            existing_image = existing.get("image", [])
            if existing_image:
                image_path = os.path.join("app", existing_image)
                if os.path.exists(image_path):
                    os.remove(image_path)
            new_image_url = await save_image(image, sub_static_dir)
            updated_fields["image_url"] = new_image_url

        if not updated_fields:
            raise HTTPException(status_code=400, detail="No fields provided to update")

        await collection_cm.update_one(
            {"_id": ObjectId(founder_id)}, {"$set": updated_fields}
        )

        updated_doc = await collection_cm.find_one({"_id": ObjectId(founder_id)})
        updated_doc["_id"] = str(updated_doc["_id"])

        return {"message": "Founder info updated successfully", "data": updated_doc}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/founder/delete/{founder_id}")
@require_scope(["scope:delete"])
async def delete_founder_info(request : Request,founder_id: str):
    try:
        existing = await collection_cm.find_one({"_id": ObjectId(founder_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Founder info not found")

        existing_image = existing.get("image", [])
        if existing_image:
            image_path = os.path.join("app", existing_image)
            if os.path.exists(image_path):
                os.remove(image_path)
                
        await collection_cm.delete_one({"_id": ObjectId(founder_id)})

        return {"message": "Founder info deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.post("/content-management/")
@require_scope(["scope:write"])
async def create_or_update_content_management(
    request : Request,
    website_name: str = Form(...),
    about: str = Form(...),
    map_path: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
):
    """
    Create or update the website content (only one document allowed).
    """
    try:
        sub_static_dir = "content_logo"
        logo_url = await save_image(logo, sub_static_dir) if logo else None

        existing_doc = await collection_cm.find_one({"type": "content_management"})

        if existing_doc:
            update_fields = {
                "website_name": website_name,
                "about": about,
                "map_path": map_path,
            }

            if logo_url:
                existing_url = existing_doc.get("logo_url", [])
                if existing_url:
                    image_path = os.path.join("app", existing_url)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        
                update_fields["logo_url"] = logo_url

            await collection_cm.update_one(
                {"_id": existing_doc["_id"]},
                {"$set": update_fields}
            )

            updated_doc = await collection_cm.find_one({"_id": existing_doc["_id"]})
            updated_doc["_id"] = str(updated_doc["_id"])
            return {"message": "Content updated successfully", "data": updated_doc}

        else:
            new_doc = {
                "type": "content_management",
                "website_name": website_name,
                "about": about,
                "map_path": map_path,
                "logo_url": logo_url,
            }
            insert_result = await collection_cm.insert_one(new_doc)
            new_doc["_id"] = str(insert_result.inserted_id)
            return {"message": "Content added successfully", "data": new_doc}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content-management/")
@require_scope(["scope:read"])
async def get_content_management(request : Request):
    """
    Retrieve the current website content configuration.
    """
    try:
        doc = await collection_cm.find_one({"type": "content_management"})
        if not doc:
            raise HTTPException(status_code=404, detail="Content not found")

        doc["_id"] = str(doc["_id"])
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/content-management/")
@require_scope(["scope:delete"])
async def delete_content_management(request : Request):
    """
    Delete the current website content (and logo file).
    """
    try:
        existing_doc = await collection_cm.find_one({"type": "content_management"})
        if not existing_doc:
            raise HTTPException(status_code=404, detail="Content not found")

        existing_url = existing_doc.get("logo_url", [])
        if existing_url:
            image_path = os.path.join("app", existing_url)
            if os.path.exists(image_path):
                os.remove(image_path)
                
        await collection_cm.delete_one({"_id": existing_doc["_id"]})

        return {"message": "Content management data deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))