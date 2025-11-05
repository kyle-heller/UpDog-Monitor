# [Pydantic] - Request/response validation schemas
from datetime import datetime

from pydantic import BaseModel, HttpUrl


# What clients send when creating a monitor
class MonitorCreate(BaseModel):
    name: str
    url: HttpUrl
    interval_seconds: int = 60


# What clients send when updating a monitor
class MonitorUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    interval_seconds: int | None = None
    is_active: bool | None = None


# What we send back to clients
class MonitorResponse(BaseModel):
    id: int
    name: str
    url: str
    interval_seconds: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
