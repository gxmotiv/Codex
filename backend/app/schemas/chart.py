from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChartRequest(BaseModel):
    name: str = Field(default="Untitled chart")
    birth_datetime: datetime
    latitude: float
    longitude: float
    timezone: str = "UTC"
    question: str = "General KP reading"


class ChartResponse(BaseModel):
    chart: dict[str, Any]
    prediction: dict[str, Any]
