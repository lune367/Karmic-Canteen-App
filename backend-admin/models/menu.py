from pydantic import BaseModel
from typing import Optional

class MenuItemCreate(BaseModel):
    name: str
    category: str  # veg, non-veg, etc.
    meal_type: str  # breakfast, lunch, evening_snack
    date: str  # YYYY-MM-DD format

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    meal_type: Optional[str] = None
    date: Optional[str] = None
    is_available: Optional[bool] = None

class MenuItemResponse(BaseModel):
    id: int
    name: str
    category: str
    meal_type: str
    date: str
    is_available: bool