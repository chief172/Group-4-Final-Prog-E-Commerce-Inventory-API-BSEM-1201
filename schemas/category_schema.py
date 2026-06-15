"""
Category Schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., max_length=500)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True