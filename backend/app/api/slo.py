from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.db import get_db
from app.core.slo import get_slo_report, SLO_WINDOW_DAYS, AVAILABILITY_SLO, LATENCY_SLO_MS
from app.models.monitor import Monitor


router = APIRouter(prefix="/slo", tags=["SLO"])


class SLOStatusResponse(BaseModel):
    name: str
    target: float
    current: float
    is_met: bool
    error_budget_pct: float
    burn_rate: float
    time_remaining_hours: float | None

    class Config:
        from_attributes = True


class SLOReportResponse(BaseModel):
    monitor_id: int
    monitor_name: str
    window_days: int
    total_checks: int
    availability: SLOStatusResponse
    latency: SLOStatusResponse

    class Config:
        from_attributes = True


class SLOConfigResponse(BaseModel):
    availability_target: float
    availability_target_pct: str
    latency_target_ms: int
    latency_percentile: str
    window_days: int


@router.get("/config", response_model=SLOConfigResponse)
async def get_slo_config():

    return SLOConfigResponse(
        availability_target=AVAILABILITY_SLO,
        availability_target_pct=f"{AVAILABILITY_SLO * 100}%",
        latency_target_ms=LATENCY_SLO_MS,
        latency_percentile="p95",
        window_days=SLO_WINDOW_DAYS,
    )


@router.get("/monitors/{monitor_id}", response_model=SLOReportResponse)
async def get_monitor_slo(
    monitor_id: int,
    db: AsyncSession = Depends(get_db),
):

    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    report = await get_slo_report(db, monitor_id, monitor.name)

    return SLOReportResponse.model_validate(report, from_attributes=True)
