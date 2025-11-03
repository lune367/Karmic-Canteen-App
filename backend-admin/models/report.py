from pydantic import BaseModel
from typing import List, Dict

class MealCount(BaseModel):
    menu_item_name: str
    count: int

class DailyReport(BaseModel):
    date: str
    meal_type: str
    meals: List[MealCount]
    total_count: int

class HistoricalData(BaseModel):
    date: str
    total_meals: int
    breakdown: Dict[str, int]