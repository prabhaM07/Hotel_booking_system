from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class FeatureSchema(BaseModel):
    feature_name: str = Field(..., min_length=2, max_length=100, description="Name of the feature")
    image : str 
    
    class Config:
        from_attributes = True

class FeatureResponse(BaseModel):
    id: int
    feature_name: str
    image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True