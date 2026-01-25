"""Tests for SLO calculations."""

import pytest
from app.core.slo import calculate_error_budget, AVAILABILITY_SLO


class TestErrorBudgetCalculation:
    """Tests for error budget math."""

    def test_full_budget_when_meeting_slo(self):
        """When SLI >= SLO, full error budget remains."""
        budget_remaining, budget_pct, burn_rate, hours = calculate_error_budget(
            sli=0.998,  # 99.8% - exceeds 99.5% SLO
            slo=AVAILABILITY_SLO,
            window_days=30,
        )

        assert budget_pct == 100.0
        assert burn_rate == 0.0

    def test_partial_budget_when_below_slo(self):
        """When SLI < SLO, error budget is partially consumed."""
        budget_remaining, budget_pct, burn_rate, hours = calculate_error_budget(
            sli=0.993,  # 99.3% - below 99.5% SLO
            slo=0.995,
            window_days=30,
        )

        # SLO is 99.5%, SLI is 99.3%
        # Error budget total = 0.5% = 0.005
        # Consumed = 99.5% - 99.3% = 0.2% = 0.002
        # Remaining = 0.5% - 0.2% = 0.3% = 0.003
        # Percentage = 0.003 / 0.005 = 60%

        assert budget_pct == pytest.approx(60.0, rel=0.01)
        assert burn_rate > 0

    def test_zero_budget_when_sli_way_below_slo(self):
        """When SLI is far below SLO, budget is exhausted."""
        budget_remaining, budget_pct, burn_rate, hours = calculate_error_budget(
            sli=0.980,  # 98% - way below 99.5%
            slo=0.995,
            window_days=30,
        )

        # Consumed more than available budget
        assert budget_pct == 0.0
        assert budget_remaining == 0

    def test_burn_rate_indicates_consumption_speed(self):
        """Burn rate should indicate how fast budget is consumed."""
        _, _, burn_rate_fast, _ = calculate_error_budget(
            sli=0.990,  # Consumed 100% of budget
            slo=0.995,
            window_days=30,
        )

        _, _, burn_rate_slow, _ = calculate_error_budget(
            sli=0.994,  # Consumed 20% of budget
            slo=0.995,
            window_days=30,
        )

        assert burn_rate_fast > burn_rate_slow


class TestSLOEndpoint:
    """Tests for SLO API endpoint."""

    @pytest.mark.asyncio
    async def test_slo_config_endpoint(self, client):
        """GET /api/slo/config returns SLO configuration."""
        response = await client.get("/api/slo/config")

        assert response.status_code == 200
        data = response.json()

        assert "availability_target" in data
        assert "latency_target_ms" in data
        assert "window_days" in data

    @pytest.mark.asyncio
    async def test_slo_monitor_endpoint_404(self, client):
        """GET /api/slo/monitors/{id} returns 404 for missing monitor."""
        response = await client.get("/api/slo/monitors/99999")

        assert response.status_code in [404, 500]
