from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ItemInDB(Item):
    id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Sample Item",
                "description": "A sample item",
                "price": 29.99,
                "created_at": "2024-01-01T00:00:00"
            }
        }