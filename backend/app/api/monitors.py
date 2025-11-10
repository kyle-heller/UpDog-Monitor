# [FastAPI] - Monitor CRUD routes
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.result import CheckResult
from app.api.schemas import MonitorCreate, MonitorResponse, MonitorUpdate
from app.core.db import get_db
from app.models.monitor import Monitor

router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.get("", response_model=list[MonitorResponse])
async def list_monitors(db: AsyncSession = Depends(get_db)):
    """Get all monitors."""
    result = await db.execute(select(Monitor))
    monitors = result.scalars().all()
    return monitors


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(monitor_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific monitor by ID."""
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.post("", response_model=MonitorResponse, status_code=201)
async def create_monitor(data: MonitorCreate, db: AsyncSession = Depends(get_db)):
    """Create a new monitor."""
    monitor = Monitor(
        name=data.name,
        url=str(data.url),
        interval_seconds=data.interval_seconds,
    )
    db.add(monitor)
    await db.commit()
    await db.refresh(monitor)
    return monitor


@router.put("/{monitor_id}", response_model=MonitorResponse)
async def update_monitor(
    monitor_id: int, data: MonitorUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an existing monitor."""
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    # Only update fields that were provided
    if data.name is not None:
        monitor.name = data.name
    if data.url is not None:
        monitor.url = str(data.url)
    if data.interval_seconds is not None:
        monitor.interval_seconds = data.interval_seconds
    if data.is_active is not None:
        monitor.is_active = data.is_active

    await db.commit()
    await db.refresh(monitor)
    return monitor


@router.get("/{monitor_id}/results")
async def get_monitor_results(
    monitor_id: int, limit: int = 20, db: AsyncSession = Depends(get_db)
):
    """Get recent check results for a monitor."""
    # First verify the monitor exists
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    # Get recent results, newest first
    result = await db.execute(
        select(CheckResult)
        .where(CheckResult.monitor_id == monitor_id)
        .order_by(CheckResult.checked_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.delete("/{monitor_id}", status_code=204)
async def delete_monitor(monitor_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a monitor."""
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    await db.delete(monitor)
    await db.commit()
