"""
SLO (Service Level Objective) calculations for UpDog Monitor.

Key concepts:
- SLI (Service Level Indicator): The metric you measure (e.g., "99.2% of checks succeeded")
- SLO (Service Level Objective): The target you commit to (e.g., "99.5% availability")
- Error Budget: The allowed failure rate (100% - SLO = 0.5% = ~3.6 hours/month)
- Burn Rate: How fast you're consuming error budget (1.0 = on track, 2.0 = 2x too fast)

Example:
    SLO: 99.5% availability over 30 days
    Error budget: 0.5% = 0.005 * 30 days * 24 hours = 3.6 hours of allowed downtime
    If you've had 1.8 hours of downtime, you've used 50% of your error budget
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.result import CheckResult


# ===================
# SLO Configuration
# ===================
# These would typically come from config, but hardcoded for simplicity

AVAILABILITY_SLO = 0.995  # 99.5% of checks must succeed
LATENCY_SLO_MS = 500      # 95% of checks must complete within 500ms
LATENCY_PERCENTILE = 0.95 # p95 latency target
SLO_WINDOW_DAYS = 30      # Rolling 30-day window


@dataclass
class SLOStatus:
    """Result of SLO calculation for a single objective."""
    name: str
    target: float           # The SLO target (e.g., 0.995)
    current: float          # Current SLI value (e.g., 0.992)
    is_met: bool            # Is SLI >= target?
    error_budget_total: float      # Total allowed failures (e.g., 0.005)
    error_budget_remaining: float  # How much budget left (e.g., 0.002)
    error_budget_pct: float        # Percentage remaining (e.g., 40.0)
    burn_rate: float        # Rate of budget consumption (1.0 = on track)
    time_remaining_hours: float | None  # Hours until budget exhausted at current rate


@dataclass
class SLOReport:
    """Complete SLO report for a monitor."""
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
    """
    Calculate availability SLI for a monitor.

    Returns: (availability_ratio, successful_checks, total_checks)
    """
    since = datetime.now(timezone.utc) - timedelta(days=window_days)

    # Count total checks in window
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

    # Count successful checks
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
    """
    Calculate latency SLI for a monitor (% of checks under target).

    Returns: (ratio_under_target, fast_checks, total_checks_with_latency)
    """
    since = datetime.now(timezone.utc) - timedelta(days=window_days)

    # Count checks with latency data (excludes failed checks with no response time)
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

    # Count checks under latency target
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
    """
    Calculate error budget metrics.

    Returns: (budget_remaining_ratio, budget_pct, burn_rate, hours_until_exhausted)

    Error budget = allowed failure rate = 1 - SLO
    Budget consumed = SLO - SLI (if SLI < SLO)
    Burn rate = (budget consumed so far) / (expected budget consumed by now)
    """
    error_budget_total = 1 - slo  # e.g., 0.005 for 99.5% SLO

    if sli >= slo:
        # Meeting SLO - full budget remaining
        return error_budget_total, 100.0, 0.0, None

    # Budget consumed = how much we've failed beyond what's allowed
    budget_consumed = slo - sli  # e.g., if SLI=99.2%, consumed = 0.003
    budget_remaining = error_budget_total - budget_consumed

    if budget_remaining < 0:
        budget_remaining = 0

    budget_pct = (budget_remaining / error_budget_total) * 100 if error_budget_total > 0 else 0

    # Burn rate: if we're halfway through the window and used half the budget, rate = 1.0
    # This is simplified - real burn rate considers time elapsed in window
    # For now: burn_rate = (budget_consumed / error_budget_total) normalized
    # burn_rate > 1 means consuming faster than sustainable
    burn_rate = budget_consumed / error_budget_total if error_budget_total > 0 else 0

    # Hours until exhausted (if continuing at current rate)
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
    """
    Generate complete SLO report for a monitor.
    """
    # Calculate availability SLI
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

    # Calculate latency SLI
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
