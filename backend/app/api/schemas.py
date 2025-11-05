from datetime import datetime

from pydantic import BaseModel, HttpUrl


class MonitorCreate(BaseModel):
    name: str
    url: HttpUrl
    interval_seconds: int = 60


class MonitorUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    interval_seconds: int | None = None
    is_active: bool | None = None


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
