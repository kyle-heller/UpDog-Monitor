"""
SLO API endpoints.

Exposes SLO/error budget data for monitors.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.db import get_db
from app.core.slo import get_slo_report, SLO_WINDOW_DAYS, AVAILABILITY_SLO, LATENCY_SLO_MS
from app.models.monitor import Monitor


router = APIRouter(prefix="/slo", tags=["SLO"])


# ===================
# Response Models
# ===================

class SLOStatusResponse(BaseModel):
    """Single SLO status."""
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
    """Complete SLO report for a monitor."""
    monitor_id: int
    monitor_name: str
    window_days: int
    total_checks: int
    availability: SLOStatusResponse
    latency: SLOStatusResponse

    class Config:
        from_attributes = True


class SLOConfigResponse(BaseModel):
    """Current SLO configuration."""
    availability_target: float
    availability_target_pct: str
    latency_target_ms: int
    latency_percentile: str
    window_days: int


# ===================
# Endpoints
# ===================

@router.get("/config", response_model=SLOConfigResponse)
async def get_slo_config():
    """
    Get current SLO configuration.

    Returns the targets used for SLO calculations.
    """
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
    """
    Get SLO report for a specific monitor.

    Returns:
    - Current SLI values (availability %, latency %)
    - Whether SLOs are being met
    - Error budget remaining (%)
    - Burn rate (1.0 = on track, >1 = consuming too fast)
    - Estimated time until budget exhausted
    """
    # Verify monitor exists
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    report = await get_slo_report(db, monitor_id, monitor.name)

    return SLOReportResponse(
        monitor_id=report.monitor_id,
        monitor_name=report.monitor_name,
        window_days=report.window_days,
        total_checks=report.total_checks,
        availability=SLOStatusResponse(
            name=report.availability.name,
            target=report.availability.target,
            current=report.availability.current,
            is_met=report.availability.is_met,
            error_budget_pct=report.availability.error_budget_pct,
            burn_rate=report.availability.burn_rate,
            time_remaining_hours=report.availability.time_remaining_hours,
        ),
        latency=SLOStatusResponse(
            name=report.latency.name,
            target=report.latency.target,
            current=report.latency.current,
            is_met=report.latency.is_met,
            error_budget_pct=report.latency.error_budget_pct,
            burn_rate=report.latency.burn_rate,
            time_remaining_hours=report.latency.time_remaining_hours,
        ),
    )
