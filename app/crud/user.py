import re
from smtplib import SMTPException
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.models.otps import OTPModel
from app.models.user import Users
from app.models.role import Roles
from app.models.user_profile import Profiles
from app.core.config import conf
from app.schemas.user_schema import (
    UserBase, UserForgetPassword
)
from app.models.token_store import TokenStore
from app.schemas.user_profile_schema import Address, UserProfileBase
from app.auth.hashing import (
    verify_password, 
    get_password_hash
)
from app.auth.jwt_handler import(
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token
)
from app.crud.generic_crud import insert_record
from fastapi import BackgroundTasks, UploadFile
from datetime import datetime, timezone
from io import BytesIO
from fastapi import BackgroundTasks, HTTPException
from fastapi_mail import FastMail, MessageSchema
from typing import Optional, Union, Dict
from passlib.context import CryptContext
from app.utils import get_role
import secrets
import string


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user_data: UserBase):
    existing_user = db.query(Users).filter(
        (Users.email == user_data.email) | (Users.phone_no == user_data.phone_no)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise ValueError("Email already registered")
        if existing_user.phone_no == user_data.phone_no:
            raise ValueError("Phone number already registered")
    
    role = db.query(Roles).filter(Roles.role_name == user_data.role).first()
    if not role:
        raise ValueError(f"Role '{user_data.role}' not found in database")
    
    hashed_password = pwd_context.hash(user_data.password)
    if(user_data.role == "user"):
        new_user = Users(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone_no=user_data.phone_no,
            password=hashed_password,
            role_id=role.id 
        )
    else:
        new_user = Users(
            id = 0,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone_no=user_data.phone_no,
            password=hashed_password,
            role_id=role.id 
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def get_user_by_email(db: Session, email: str):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        raise ValueError("User not found with this email.")
    return user


def get_user_by_phoneno(db: Session, phone_no: int):
    user = db.query(Users).filter(Users.phone_no == phone_no).first()
    if not user:
        raise ValueError("User not found with this phone number.")
    return user


def list_users(db: Session):
    return db.query(Users).all()


def delete_user(db: Session, user_id: str):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return user

def change_password(db: Session,user_data: UserForgetPassword):
    prev_pass = user_data.prev_password
    cur_pass = user_data.cur_password
    prev_hashed_password = get_password_hash(prev_pass)
    cur_hashed_password = get_password_hash(cur_pass)
    if not verify_password(cur_pass,prev_hashed_password):
        Users.password = cur_hashed_password
    db.commit()
    return user_data


def generate_tokens(db:Session , user_data: Users) -> Dict[str, str]:
    """Generate access and refresh tokens for a user."""
    role = db.query(Roles).filter(Roles.id == user_data.role_id).first()
    role_name = role.role_name
    token_data = {
        "sub": str(user_data.id),
        "email": user_data.email,
        "phone_no": user_data.phone_no,
        "role": role_name,
        "role_id" : user_data.role_id
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user_data.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
        
    }
    

async def login_by_phoneno_or_email(user_: str, password: str, db: Session) -> Dict:
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    PHONE_REGEX = r"^[6-9]\d{9}$"

    if re.match(EMAIL_REGEX, user_):
        existing_user = db.query(Users).filter(Users.email == user_).first()
    elif re.match(PHONE_REGEX, user_):
        existing_user = db.query(Users).filter(Users.phone_no == user_).first()
    else:
        raise ValueError("Invalid user detail format")

    if existing_user is None:
        raise ValueError("Invalid user detail")

    if not verify_password(password, existing_user.password):
        raise ValueError("Invalid password")

    tokens = generate_tokens(db, existing_user)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    at = verify_access_token(access_token)
    rt = verify_refresh_token(refresh_token)

    access_token_expiry_dt = datetime.fromtimestamp(at.get("exp"), tz=timezone.utc)
    refresh_token_expiry_dt = datetime.fromtimestamp(rt.get("exp"), tz=timezone.utc)

    dicts = {
        "user_id": existing_user.id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_expiry": access_token_expiry_dt,
        "refresh_token_expiry": refresh_token_expiry_dt
    }

    token_store_instance = await insert_record(db=db, model=TokenStore, **dicts)

    role = get_role(db, existing_user.role_id)
    response = JSONResponse({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": existing_user.id,
        "role": role if role else None
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=1800,  
        httponly=True,
        secure=False,
        samesite="lax",
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=604800,  
        httponly=True,
        secure=False,
        samesite="lax",
        path="/"
    )

    return response



def refresh_access_token(db: Session, user_id: str) -> Dict[str, str]:
    """Generate new access token using refresh token."""
    user = db.query(Users).filter(Users.id == user_id).first()
    role = get_role(db,user.role_id)

    if not user:
        raise ValueError("User not found")
    
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "phone_no": user.phone_no,
        "role": role
    }
    
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def tuple_to_address(address_tuple):
    if not address_tuple:
        return None
    return Address(
        street=address_tuple[0],
        city=address_tuple[1],
        state=address_tuple[2],
        country=address_tuple[3],
        pincode=address_tuple[4]
    )

def update_profile(
    db: Session, 
    user_id: str, 
    user_profile_data: UserProfileBase, 
    image: Optional[Union[UploadFile, BytesIO]] = None,
    image_url: Optional[str] = None 
):
    profile = db.query(Profiles).filter(Profiles.user_id == user_id).first()

    if not profile:
        profile = Profiles(user_id=user_id, updated_at=datetime.utcnow())
        db.add(profile)

    if user_profile_data.DOB:
        profile.DOB = user_profile_data.DOB

    if user_profile_data.address:
        profile.address = (
            user_profile_data.address.street or "",
            user_profile_data.address.city or "",
            user_profile_data.address.state or "",
            user_profile_data.address.country or "",
            user_profile_data.address.pincode or ""
        )

    if image_url:
        profile.image_url = image_url  
    elif image:  
        content = image.file.read() if hasattr(image, 'file') else image.read()
        profile.image = content

    profile.updated_at = datetime.now()
    db.commit()
    db.refresh(profile)
    return profile



def generate_otp(length=6):
    """Generate a numeric OTP of given length (default 6 digits)."""
    digits = string.digits 
    otp = ''.join(secrets.choice(digits) for _ in range(length))
    return otp


async def send_otp(
    db: Session,
    email: EmailStr,
    background_tasks: BackgroundTasks,
    user_data : UserBase,
):
    otp = generate_otp()

    message = MessageSchema(
        subject="Your OTP Code",
        recipients=[email],
        body=f"Your OTP code is: {otp}",
        subtype="plain"
    )

    fm = FastMail(conf)

    try:
        background_tasks.add_task(fm.send_message, message)
        
    except SMTPException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

    await insert_record(db=db, model=OTPModel, email=email,otp=otp,temp_user_data = user_data.model_dump())
    print("OTP : "+otp)
    
    return {"status": "OTP sent successfully"}

