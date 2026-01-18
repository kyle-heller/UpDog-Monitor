from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.result import CheckResult


AVAILABILITY_SLO = 0.995  # 99.5% of checks must succeed
LATENCY_SLO_MS = 500      # 95% of checks must complete within 500ms
LATENCY_PERCENTILE = 0.95 # p95 latency target
SLO_WINDOW_DAYS = 30      # Rolling 30-day window


@dataclass
class SLOStatus:
    name: str
    target: float
    current: float
    is_met: bool
    error_budget_total: float
    error_budget_remaining: float
    error_budget_pct: float
    burn_rate: float  # 1.0 = consuming at expected rate
    time_remaining_hours: float | None


@dataclass
class SLOReport:
    monitor_id: int
    monitor_name: str
    window_days: int
    total_checks: int
    availability: SLOStatus
    latency: SLOStatus


async def calculate_availability_slo(
    db: AsyncSession,
    monitor_id: int,
    window_days: int = SLO_WINDOW_DAYS,
) -> tuple[float, int, int]:
    """Returns (availability_ratio, successful_checks, total_checks)."""
    since = datetime.now(timezone.utc) - timedelta(days=window_days)

    total_result = await db.execute(
        select(func.count(CheckResult.id))
        .where(and_(
            CheckResult.monitor_id == monitor_id,
            CheckResult.checked_at >= since,
        ))
    )
    total_checks = total_result.scalar() or 0

    if total_checks == 0:
        return 1.0, 0, 0  # No data = assume OK

    success_result = await db.execute(
        select(func.count(CheckResult.id))
        .where(and_(
            CheckResult.monitor_id == monitor_id,
            CheckResult.checked_at >= since,
            CheckResult.is_up == True,
        ))
    )
    successful_checks = success_result.scalar() or 0

    availability = successful_checks / total_checks
    return availability, successful_checks, total_checks


async def calculate_latency_slo(
    db: AsyncSession,
    monitor_id: int,
    window_days: int = SLO_WINDOW_DAYS,
    target_ms: int = LATENCY_SLO_MS,
) -> tuple[float, int, int]:
    """Returns (ratio_under_target, fast_checks, total_checks_with_latency)."""
    since = datetime.now(timezone.utc) - timedelta(days=window_days)

    total_result = await db.execute(
        select(func.count(CheckResult.id))
        .where(and_(
            CheckResult.monitor_id == monitor_id,
            CheckResult.checked_at >= since,
            CheckResult.response_time_ms.isnot(None),
        ))
    )
    total_checks = total_result.scalar() or 0

    if total_checks == 0:
        return 1.0, 0, 0  # No data = assume OK

    fast_result = await db.execute(
        select(func.count(CheckResult.id))
        .where(and_(
            CheckResult.monitor_id == monitor_id,
            CheckResult.checked_at >= since,
            CheckResult.response_time_ms.isnot(None),
            CheckResult.response_time_ms <= target_ms,
        ))
    )
    fast_checks = fast_result.scalar() or 0

    ratio = fast_checks / total_checks
    return ratio, fast_checks, total_checks


def calculate_error_budget(
    sli: float,
    slo: float,
    window_days: int,
) -> tuple[float, float, float, float | None]:
    """Returns (budget_remaining, budget_pct, burn_rate, hours_until_exhausted)."""
    error_budget_total = 1 - slo

    if sli >= slo:
        # Meeting SLO - full budget remaining
        return error_budget_total, 100.0, 0.0, None

    budget_consumed = slo - sli
    budget_remaining = error_budget_total - budget_consumed

    if budget_remaining < 0:
        budget_remaining = 0

    budget_pct = (budget_remaining / error_budget_total) * 100 if error_budget_total > 0 else 0

    # burn_rate > 1 = consuming budget too fast
    burn_rate = budget_consumed / error_budget_total if error_budget_total > 0 else 0

    if burn_rate > 0 and error_budget_total > 0:
        window_hours = window_days * 24
        remaining_hours = (budget_remaining / error_budget_total) * window_hours
        hours_until_exhausted = remaining_hours / burn_rate
    else:
        hours_until_exhausted = None

    return budget_remaining, budget_pct, burn_rate, hours_until_exhausted


async def get_slo_report(
    db: AsyncSession,
    monitor_id: int,
    monitor_name: str,
) -> SLOReport:

    avail_sli, avail_success, avail_total = await calculate_availability_slo(
        db, monitor_id, SLO_WINDOW_DAYS
    )
    avail_budget_rem, avail_budget_pct, avail_burn, avail_hours = calculate_error_budget(
        avail_sli, AVAILABILITY_SLO, SLO_WINDOW_DAYS
    )

    availability = SLOStatus(
        name="Availability",
        target=AVAILABILITY_SLO,
        current=avail_sli,
        is_met=avail_sli >= AVAILABILITY_SLO,
        error_budget_total=1 - AVAILABILITY_SLO,
        error_budget_remaining=avail_budget_rem,
        error_budget_pct=avail_budget_pct,
        burn_rate=avail_burn,
        time_remaining_hours=avail_hours,
    )

    latency_sli, latency_fast, latency_total = await calculate_latency_slo(
        db, monitor_id, SLO_WINDOW_DAYS, LATENCY_SLO_MS
    )
    latency_budget_rem, latency_budget_pct, latency_burn, latency_hours = calculate_error_budget(
        latency_sli, LATENCY_PERCENTILE, SLO_WINDOW_DAYS
    )

    latency = SLOStatus(
        name=f"Latency (p{int(LATENCY_PERCENTILE*100)} < {LATENCY_SLO_MS}ms)",
        target=LATENCY_PERCENTILE,
        current=latency_sli,
        is_met=latency_sli >= LATENCY_PERCENTILE,
        error_budget_total=1 - LATENCY_PERCENTILE,
        error_budget_remaining=latency_budget_rem,
        error_budget_pct=latency_budget_pct,
        burn_rate=latency_burn,
        time_remaining_hours=latency_hours,
    )

    return SLOReport(
        monitor_id=monitor_id,
        monitor_name=monitor_name,
        window_days=SLO_WINDOW_DAYS,
        total_checks=avail_total,
        availability=availability,
        latency=latency,
    )
