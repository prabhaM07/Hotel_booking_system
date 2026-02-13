from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, File, Form, Request,UploadFile, logger
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from streamlit import status
from app.auth.auth_utils import require_scope
from app.crud.generic_crud import commit_db, filter_record, get_record, insert_record, search
from app.crud.userQueryChat import del_user_history
from app.models.otps import OTPModel
from app.schemas.user_schema import UserBase, UserForgetPassword,UserResponse
from app.core.dependency import get_db
from app.crud import user
from app.auth.jwt_handler import verify_refresh_token
from app.models.user import Users
from app.models.user_profile import Profiles
from app.middleware.logging_middleware import get_recent_activities
from typing import Any, Dict, List, Optional
from app.schemas.user_profile_schema import UserProfileBase, Address
from datetime import date, datetime, timezone
import uuid
import os

STATIC_DIR = "app/static/profile_images"
os.makedirs(STATIC_DIR, exist_ok=True)


def safe_parse_dob(dob_str):
    if not dob_str:
        return None
    try:
          
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(dob_str, fmt).date()
            except ValueError:
                continue
        raise ValueError("DOB must be in YYYY-MM-DD or DD-MM-YYYY format")
    except ValueError as e:
        raise ValueError(str(e))


router = APIRouter(prefix="/user", tags=["Users"])

@router.post("/register")
async def register_user(user_data: UserBase,background_tasks:BackgroundTasks,db: Session = Depends(get_db)):
    try:
        result = await user.send_otp(db = db,email = user_data.email,background_tasks=background_tasks,user_data = user_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

    return result

@router.post("/verify_email")
async def verify_email(
    otp: str = Form(...),
    db: Session = Depends(get_db)
):  
    
    instance = await get_record(db=db, model=OTPModel, otp = otp)
    
    if not instance:
        raise HTTPException(status_code=404, detail="OTP not found or already verified")

    if instance.otp != otp:
        raise HTTPException(status_code=400, detail="Incorrect OTP")

    if datetime.now(timezone.utc) > instance.expiry:
        
        raise HTTPException(status_code=400, detail="OTP expired")

    data = UserBase(
        firstName=instance.temp_user_data["first_name"],
        lastName=instance.temp_user_data["last_name"],
        phoneNo=instance.temp_user_data["phone_no"],
        email=instance.temp_user_data["email"],
        role=instance.temp_user_data["role"],
        password=instance.temp_user_data["password"],
    )

    new_user = user.create_user(db, data)


    new_user.verified = True
    
    db.delete(instance)
    
    await commit_db(db=db)
    
    role_name = new_user.role.role_name 

    return UserResponse(
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        email=new_user.email,
        phone_no=new_user.phone_no,
        role=role_name
    )


@router.post("/login")
async def login(
     user_email_or_password: str = Form(
        ..., 
        description="Enter your email or phone number",
        example="john.doe@example.com"
    ),
    password: str = Form(
        ..., 
        description="Enter your account password",
        example="John@123"
    ),
    db: Session = Depends(get_db)):
    try:
        return await user.login_by_phoneno_or_email(user_email_or_password,password, db)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    
    try:
        refresh_token = request.cookies.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=401, 
                detail="Refresh token not found. Please login again."
            )
        
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        new_tokens = user.refresh_access_token(db, user_id)
        
        response.set_cookie(
            key="access_token",
            value=new_tokens['access_token'],
            max_age=1800,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/"
        )
        
        return {
            "message": "Token refreshed successfully",
            "token_type": "bearer"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
def logout(request: Request,
    response: Response
):
    
    response.delete_cookie(
        key="access_token",
        path="/"
    )
    
    response.delete_cookie(
        key="refresh_token",
        path="/"
    )
    
    return {
        "message": "Logged out successfully",
        "detail": "Authentication cookies have been cleared"
    }


@router.put("/forget-password")
def forget_user_password(
    request: Request,
    user_data: UserForgetPassword,
    db: Session = Depends(get_db)
):
    current_user= request.state.user
    try:
        if user_data.email != current_user.email:
            raise HTTPException(status_code=403, detail="Cannot change another user's password")
        
        return user.change_password(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/me", response_model=UserResponse)
@require_scope(["user:read"])
def get_current_user_Info(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    role = user.get_role(db, current_user.role_id)

    return UserResponse(
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone_no=current_user.phone_no,
        role=role
    )


@router.get("/users", response_model=List[UserResponse])
@require_scope(["user:write"])
async def get_all_users(request: Request, db: Session = Depends(get_db)):
    users = user.list_users(db)
    
    return [
        UserResponse(
            first_name=u.first_name,
            last_name=u.last_name,
            email=u.email,
            phone_no=u.phone_no,
            role=user.get_role(db, u.role_id)
        )
        for u in users
    ]


@router.delete("/user/{user_id}")
@require_scope(["user:delete"])
async def delete_user_by_id(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db)
):
    result = user.delete_user(db, user_id)
    await del_user_history(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.put("/profile/{user_id}", response_model=UserProfileBase)
@require_scope(["user:update"])
async def update_user_profile(
    request: Request,
    DOB: Optional[str] = Form(None),
    street: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),
    remove_image: Optional[bool] = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    current_user = request.state.user


    profile = db.query(Profiles).filter(Profiles.user_id == current_user.id).first()
    image_url = profile.image_url if profile else None

    if remove_image and image_url:
        old_file_path = os.path.join(STATIC_DIR, os.path.basename(image_url))
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
        image_url = None

    if image:
        try:
            if not image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="File must be an image")
            if image_url:
                old_file_path = os.path.join(STATIC_DIR, os.path.basename(image_url))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            extension = image.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{extension}"
            file_path = os.path.join(STATIC_DIR, filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())
            image_url = f"/static/profile_images/{filename}"
        except Exception as e:
            logger.error(f"Image save error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image save failed: {str(e)}")

    address_data = None
    if any([street, city, state, country, pincode]):
        address_data = Address(
            street=street,
            city=city,
            state=state,
            country=country,
            pincode=pincode
        )

    profile_data = UserProfileBase(
        address=address_data,
        DOB=safe_parse_dob(DOB)
    )

    updated_profile = user.update_profile(db, user_id, profile_data, image_url=image_url)

    return UserProfileBase(
        DOB=updated_profile.DOB,
        address=user.tuple_to_address(updated_profile.address),
        image_url=image_url,
        updated_at=updated_profile.updated_at
    )


templates = Jinja2Templates(directory="app/templates")

@router.get("/view")
@require_scope(["user:read"])
async def view_profile_image(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.state.user.id
     
    profile = db.query(Profiles).filter(Profiles.user_id == user_id).first()

    if not profile or not profile.image_url:
        raise HTTPException(status_code=404, detail="Profile image not found")

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user_id": user_id,
            "image_path": profile.image_url
        }
    )
   

@router.get("/search", response_model=Dict[str, Any])
@require_scope(["user:write"])
def search_users(
    request: Request,
    q: str = Query(..., min_length=1),
    page: int = 1,
    per_page: int = 10, 
    db: Session = Depends(get_db)
):
    result = search(db=db, model=Users, q=q, page=page, per_page=per_page)
    
    if "data" in result and isinstance(result["data"], list):
        result["data"] = [
            UserResponse(
                first_name=u.first_name,
                last_name=u.last_name,
                email=u.email,
                phone_no=u.phone_no,
                role=user.get_role(db, u.role_id)
            ).model_dump()
            for u in result["data"]
        ]
    
    return result
 
 
@router.get("/filter")
@require_scope(["user:write"])
async def filter_users(
    role_id: Optional[int] = Query(None, description="Filter by role ID"),
    created_from: Optional[datetime] = Query(None, description="Filter users created on or after this datetime"),
    created_to: Optional[datetime] = Query(None, description="Filter users created on or before this datetime"),
    db: Session = Depends(get_db)
):
    dicts = {}

    # Build filters dynamically
    if role_id is not None:
        dicts["role_id"] = ["==", role_id]
    if created_from:
        dicts["created_at"] = [">=", created_from]
    if created_to:
        dicts["created_at"] = ["<=", created_to]

    if not dicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one filter parameter."
        )

    result = await filter_record(db=db, model=Users, **dicts)
    
    if isinstance(result, list):
        result = [
            UserResponse(
                first_name=u.first_name,
                last_name=u.last_name,
                email=u.email,
                phone_no=u.phone_no,
                role=user.get_role(db, u.role_id)
            ).dict()
            for u in result
        ]
    
    return result


@router.get("/recent-activity")
@require_scope(["user:write"])
async def get_recent_activity(
    request: Request,
    limit: int = 50,
    user_id: Optional[int] = None,
    exclude_self: bool = False,
    db: Session = Depends(get_db)
):
    activities = get_recent_activities(limit=limit * 2, user_id=user_id) 
    
    filtered_activities = []
    current_user = getattr(request.state, "user", None)
    current_user_id = current_user.id if current_user else None
    
    for activity in activities:
        filtered_activities.append(activity)
        
        if len(filtered_activities) >= limit:
            break
    
    return {
        "activities": filtered_activities, 
        "total": len(filtered_activities),
        "filters_applied": {
            "user_id": user_id,
            "exclude_self": exclude_self
        }
    }