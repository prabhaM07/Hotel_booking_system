from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
import re


class RoomTypeResponse(BaseModel):
    id: Optional[int] = Field(None, description="Primary key (auto-generated)")
    room_name: str = Field(
        ...,
        alias="roomName",
        description="Name of the room type (2-100 chars, alphanumeric with spaces allowed).",
        example="Deluxe Suite"
    )
    room_size: int = Field(..., description="In BHK")
    base_price: int = Field(
        ...,
        alias="basePrice",
        description="Base price per night in currency units (must be positive).",
        example=5000
    )
    no_of_adult: int = Field(
        ...,
        alias="noOfAdult",
        description="Maximum number of adults allowed (1-10).",
        example=2
    )
    no_of_child: int = Field(
        ...,
        alias="noOfChild",
        description="Maximum number of children allowed (0-10).",
        example=2
    )
    images: Optional[List[str]] = Field(default_factory=list, description="List of image URLs")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @field_validator("room_name")
    @classmethod
    def validate_room_name(cls, v):
        v = v.strip()
        if not (2 <= len(v) <= 100):
            raise ValueError("Room name must be between 2 and 100 characters long.")
        if not re.fullmatch(r"[A-Za-z0-9\s]+", v):
            raise ValueError("Room name must contain only alphanumeric characters and spaces.")
        return v

    @field_validator("base_price")
    @classmethod
    def validate_base_price(cls, v):
        if v <= 0:
            raise ValueError("Base price must be a positive integer.")
        if v > 1000000:
            raise ValueError("Base price cannot exceed 1,000,000.")
        return v

    @field_validator("no_of_adult")
    @classmethod
    def validate_no_of_adult(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Number of adults must be between 1 and 10.")
        return v

    @field_validator("no_of_child")
    @classmethod
    def validate_no_of_child(cls, v):
        if v < 0 or v > 10:
            raise ValueError("Number of children must be between 0 and 10.")
        return v

    class Config:
        populate_by_name = True
        from_attributes = True


class BedTypeInfo(BaseModel):
    id: int
    bed_type_name: str
    num_of_beds: int

    class Config:
        from_attributes = True


class FeatureInfo(BaseModel):
    id: int
    feature_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoomTypeDetailResponse(RoomTypeResponse):
    bed_types: List[BedTypeInfo] = Field(default_factory=list, description="Associated bed types")
    features: List[FeatureInfo] = Field(default_factory=list, description="Room features")
    total_beds: Optional[int] = Field(0, description="Total number of beds across all types")

    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "room_name": "Deluxe Suite",
                "room_size": 3,
                "base_price": 5000,
                "no_of_adult": 2,
                "no_of_child": 1,
                "images": ["url1.jpg", "url2.jpg"],
                "bed_types": [
                    {"id": 1, "bed_type_name": "King", "num_of_beds": 1},
                    {"id": 2, "bed_type_name": "Single", "num_of_beds": 1}
                ],
                "features": [
                    {"id": 1, "feature_name": "WiFi", "description": "High-speed internet"},
                    {"id": 2, "feature_name": "TV", "description": "Smart TV"}
                ],
                "total_beds": 2
            }
        }


class PaginationMeta(BaseModel):
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class RoomTypePaginatedResponse(BaseModel):
    data: List[RoomTypeResponse] = Field(..., description="List of room types")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": 1,
                        "room_name": "Deluxe Suite",
                        "room_size": 3,
                        "base_price": 5000,
                        "no_of_adult": 2,
                        "no_of_child": 1,
                        "images": []
                    }
                ],
                "meta": {
                    "page": 1,
                    "per_page": 10,
                    "total_items": 50,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False
                }
            }
        }


class RoomTypeDetailPaginatedResponse(BaseModel):
    data: List[RoomTypeDetailResponse] = Field(..., description="List of detailed room types")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class RoomTypeFilterResponse(BaseModel):
    data: List[RoomTypeDetailResponse] = Field(..., description="Filtered room types")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    statistics: Optional[dict] = Field(None, description="Filter statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "meta": {
                    "page": 1,
                    "per_page": 10,
                    "total_items": 15,
                    "total_pages": 2,
                    "has_next": True,
                    "has_prev": False
                },
                "statistics": {
                    "avg_price": 4500,
                    "min_price": 2000,
                    "max_price": 8000,
                    "price_range": "2000-8000"
                }
            }
        }


class BulkOperationResponse(BaseModel):
    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Operation message")
    affected_count: int = Field(0, description="Number of records affected")
    errors: Optional[List[str]] = Field(default_factory=list, description="Any errors encountered")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "affected_count": 5,
                "errors": []
            }
        }


class RoomAvailabilityResponse(BaseModel):
    room_type_id: int
    room_name: str
    available: bool
    available_count: int = Field(0, description="Number of available rooms")
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "room_type_id": 1,
                "room_name": "Deluxe Suite",
                "available": True,
                "available_count": 3,
                "message": "3 rooms available for your dates"
            }
        }