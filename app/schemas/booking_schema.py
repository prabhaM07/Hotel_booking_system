from datetime import date
from pydantic import BaseModel, Field, field_validator
from app.models.Enum import BookingStatusEnum

class BookingBase(BaseModel):
    room_id: int = Field(..., gt=0, description="Foreign key to Room table")
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date (must be after check-in)")
    booking_status: BookingStatusEnum = Field(default=BookingStatusEnum.CONFIRMED.value)


class BookingResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    total_amount : int
    check_in: date
    check_out: date
    booking_status : BookingStatusEnum
    
    class Config:
        from_attributes = True