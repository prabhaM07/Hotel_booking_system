from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Generic, TypeVar
import re


class BedTypeSchema(BaseModel):
    id: Optional[int] = Field(None, description="Primary key (auto-generated)")
    bed_type_name: str = Field(
        ..., 
        min_length=2, 
        max_length=50, 
        description="Type of bed, e.g. Single, Double, King, Queen"
    )
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("bed_type_name")
    @classmethod
    def validate_bed_type_name(cls, v: str) -> str:
       
        if not re.match(r"^[A-Za-z\s]+$", v.strip()):
            raise ValueError("Bed type name must contain only letters and spaces.")
        return v.strip()

    class Config:
        from_attributes = True  
        arbitrary_types_allowed = True


class BedTypeResponse(BedTypeSchema):
    id: int  
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bed_type_name": "King Size",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


T = TypeVar('T')


class PaginationMeta(BaseModel):
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "per_page": 10,
                "total_items": 45,
                "total_pages": 5,
                "has_next": True,
                "has_prev": False
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T] = Field(..., description="List of items for current page")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

    class Config:
        arbitrary_types_allowed = True


class BedTypePaginatedResponse(BaseModel):
    data: List[BedTypeResponse] = Field(..., description="List of bed types")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": 1,
                        "bed_type_name": "Single",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    },
                    {
                        "id": 2,
                        "bed_type_name": "Double",
                        "created_at": "2024-01-02T00:00:00",
                        "updated_at": "2024-01-02T00:00:00"
                    }
                ],
                "meta": {
                    "page": 1,
                    "per_page": 10,
                    "total_items": 25,
                    "total_pages": 3,
                    "has_next": True,
                    "has_prev": False
                }
            }
        }


class BedTypeWithRoomsResponse(BedTypeResponse):
    room_count: Optional[int] = Field(0, description="Number of rooms with this bed type")
    rooms: Optional[List[dict]] = Field(default_factory=list, description="Associated rooms")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bed_type_name": "King Size",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "room_count": 5,
                "rooms": [
                    {"id": 101, "room_number": "A101", "floor": 1},
                    {"id": 102, "room_number": "A102", "floor": 1}
                ]
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
                "message": "Bulk operation completed successfully",
                "affected_count": 15,
                "errors": []
            }
        }


class BedTypeFilterResponse(BaseModel):
    data: List[BedTypeResponse] = Field(..., description="Filtered bed types")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    statistics: Optional[dict] = Field(None, description="Additional statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "meta": {
                    "page": 1,
                    "per_page": 10,
                    "total_items": 5,
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False
                },
                "statistics": {
                    "date_range": "2024-01-01 to 2024-12-31",
                    "most_common_type": "King Size"
                }
            }
        }


        