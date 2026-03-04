from datetime import date
from types import SimpleNamespace

from app.application.services import AlertService, MetricsService


def _build_cycle():
    pond = SimpleNamespace(farm=SimpleNamespace(climate_records=[]))
    cycle = SimpleNamespace(
        id=1,
        stocked_count=10000,
        seed_cost=100,
        start_date=date(2024, 1, 1),
        pond=pond,
        feedings=[
            SimpleNamespace(date=date(2024, 1, 1), feed_kg=100, feed_cost_usd=90, energy_cost_usd=8, chemical_cost_usd=3),
            SimpleNamespace(date=date(2024, 1, 2), feed_kg=120, feed_cost_usd=110, energy_cost_usd=9, chemical_cost_usd=3),
        ],
        mortalities=[SimpleNamespace(date=date(2024, 1, 1), dead_count=50)],
        water_parameters=[SimpleNamespace(date=date(2024, 1, 1), oxygen_mg_l=2.5)],
        samplings=[
            SimpleNamespace(date=date(2024, 1, 1), avg_weight_g=2),
            SimpleNamespace(date=date(2024, 1, 8), avg_weight_g=8),
        ],
    )
    pond.farm.climate_records = [SimpleNamespace(date=date(2024, 1, 1), temperature_c=34, rain_mm=50)]
    return cycle


def test_compute_metrics():
    cycle = _build_cycle()
    service = MetricsService(db=None)
    metrics = service.compute_metrics(cycle)
    assert metrics.feed_total_kg == 220
    assert metrics.fcr > 0
    assert 0 < metrics.survival_rate <= 1


def test_alert_generation():
    cycle = _build_cycle()
    alerts = AlertService(MetricsService(db=None)).generate_alerts(cycle)
    severities = [a.severity.value for a in alerts]
    assert "CRITICAL" in severities
