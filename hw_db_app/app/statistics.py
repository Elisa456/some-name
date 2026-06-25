from pydantic import BaseModel
from typing import Dict, List, Optional

class MonthlyStatistics(BaseModel):
    month: int
    year: int
    count: int

class TotalStatisticsResponse(BaseModel):
    total: int
    by_status: Dict[str, int]

class MonthlyStatisticsResponse(BaseModel):
    items: list[MonthlyStatistics]