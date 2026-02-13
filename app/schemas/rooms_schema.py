# app/schemas/rooms_schema.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.Enum import RoomStatusEnum

class RoomsBase(BaseModel):
    
    room_type_id: int = Field(
        ...,
        alias="roomTypeId",
        description="Foreign key reference to room_type_with_size table.",
        example=1
    )
    floor_id: int = Field(
        ...,
        alias="floorId",
        description="Foreign key reference to Floor table.",
        example=3
    )
    
    room_no: int = Field(
        ...,
        alias="roomNo",
        description="Room number (1-9999, must be unique).",
        example=101
    )
    
    status: Optional[RoomStatusEnum] = Field(
        default=RoomStatusEnum.AVAILABLE.value,
        description="Current room status"
    )

    @field_validator("room_type_id")
    def validate_room_type_id(cls, v):
        if v <= 0:
            raise ValueError("Room type ID must be a positive integer.")
        return v

    @field_validator("floor_id")
    def validate_floor_id(cls, v):
        if v < 0:
            raise ValueError("Floor ID must be a positive integer.")
        return v
    
    @field_validator("room_no")
    def validate_room_no(cls, v):
        if v < 1 or v > 9999:
            raise ValueError("Room number must be between 1 and 9999.")
        return v

    class Config:
        populate_by_name = True
        use_enum_values = True


class RoomResponse(BaseModel):
    
    id: int = Field(..., description="Unique room identifier")
    room_type_id: int = Field(..., alias="roomTypeId")
    floor_id: int = Field(..., alias="floorId")
    room_no: int = Field(..., alias="roomNo")
    status: str = Field(..., description="Current room status")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "roomTypeId": 2,
                "floorId": 3,
                "roomNo": 101,
                "status": "available",
                "createdAt": "2025-01-15T10:30:00",
                "updatedAt": "2025-01-15T10:30:00"
            }
        }


class RoomListResponse(BaseModel):
    
    success: bool = Field(default=True)
    count: int = Field(..., description="Number of rooms returned")
    rooms: List[RoomResponse] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "count": 2,
                "rooms": [
                    {
                        "id": 1,
                        "roomTypeId": 2,
                        "floorId": 3,
                        "roomNo": 101,
                        "status": "available",
                        "createdAt": "2025-01-15T10:30:00",
                        "updatedAt": "2025-01-15T10:30:00"
                    }
                ]
            }
        }


class RoomDetailResponse(BaseModel):
    
    success: bool = Field(default=True)
    room: RoomResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "room": {
                    "id": 1,
                    "roomTypeId": 2,
                    "floorId": 3,
                    "roomNo": 101,
                    "status": "available",
                    "createdAt": "2025-01-15T10:30:00"
                }
            }
        }


class RoomUpdateRequest(BaseModel):
    
    room_id: int = Field(..., alias="roomId")
    room_type_id: Optional[int] = Field(None, alias="roomTypeId")
    floor_id: Optional[int] = Field(None, alias="floorId")
    room_no: Optional[int] = Field(None, alias="roomNo")
    status: Optional[str] = None
    
    class Config:
        populate_by_name = True


class RoomDeleteResponse(BaseModel):
    
    success: bool = Field(default=True)
    message: str = Field(..., description="Deletion confirmation message")
    deleted_room_id: int = Field(..., alias="deletedRoomId")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Room deleted successfully",
                "deletedRoomId": 1
            }
        }


class RoomSearchResponse(BaseModel):
    
    success: bool = Field(default=True)
    total: int = Field(..., description="Total matching records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., alias="perPage", description="Records per page")
    total_pages: int = Field(..., alias="totalPages")
    rooms: List[RoomResponse] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "success": True,
                "total": 25,
                "page": 1,
                "perPage": 10,
                "totalPages": 3,
                "rooms": []
            }
        }


class RoomFilterRequest(BaseModel):
    
    room_no: Optional[int] = Field(None, alias="roomNo")
    status: Optional[str] = None
    created_from: Optional[datetime] = Field(None, alias="createdFrom")
    created_to: Optional[datetime] = Field(None, alias="createdTo")
    
    class Config:
        populate_by_name = True


class RoomAvailabilityResponse(BaseModel):
    
    success: bool = Field(default=True)
    available: bool = Field(..., description="Whether room is available")
    room_id: int = Field(..., alias="roomId")
    status: str
    message: Optional[str] = None
    
    class Config:
        populate_by_name = True