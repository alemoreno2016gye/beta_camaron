from collections import defaultdict
from datetime import timedelta

from sqlalchemy.orm import Session

from app.domain.entities import Alert, AlertSeverity, KPIBundle
from app.infrastructure import models


class MetricsService:
    SALE_PRICE_PER_LB = 2.2

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _safe_div(num: float, den: float) -> float:
        return round(num / den, 4) if den else 0.0

    def compute_metrics(self, cycle: models.Cycle) -> KPIBundle:
        feed_total = sum(f.feed_kg for f in cycle.feedings)
        dead_total = sum(m.dead_count for m in cycle.mortalities)
        alive = max(cycle.stocked_count - dead_total, 0)

        samples = sorted(cycle.samplings, key=lambda x: x.date)
        first_weight = samples[0].avg_weight_g if samples else 0
        last_weight = samples[-1].avg_weight_g if samples else 0
        period_days = max((samples[-1].date - samples[0].date).days, 1) if len(samples) > 1 else 1

        biomass_gain = alive * max(last_weight - first_weight, 0) / 1000
        estimated_biomass = alive * last_weight / 1000
        survival = self._safe_div(alive, cycle.stocked_count)
        adg = self._safe_div(last_weight - first_weight, period_days)
        fcr = self._safe_div(feed_total, biomass_gain)

        feed_cost = sum(f.feed_cost_usd for f in cycle.feedings)
        energy_cost = sum(f.energy_cost_usd for f in cycle.feedings)
        chemical_cost = sum(f.chemical_cost_usd for f in cycle.feedings)
        seed_cost = cycle.seed_cost
        lbs_estimated = estimated_biomass * 2.20462
        cost_lb = self._safe_div(feed_cost + energy_cost + seed_cost + chemical_cost, lbs_estimated)
        margin = round(self.SALE_PRICE_PER_LB - cost_lb, 4)

        return KPIBundle(
            cycle_id=cycle.id,
            feed_total_kg=round(feed_total, 2),
            biomass_gain_kg=round(biomass_gain, 2),
            estimated_biomass_kg=round(estimated_biomass, 2),
            survival_rate=round(survival, 4),
            adg_g_per_day=round(adg, 4),
            fcr=round(fcr, 4),
            cost_per_lb=round(cost_lb, 4),
            estimated_margin_per_lb=margin,
        )

    def trend_points(self, cycle: models.Cycle) -> list[dict]:
        feed_by_day = {f.date: f.feed_kg for f in cycle.feedings}
        mortality_by_day = {m.date: m.dead_count for m in cycle.mortalities}
        oxygen_by_day = {w.date: w.oxygen_mg_l for w in cycle.water_parameters}
        sample_by_day = {s.date: s.avg_weight_g for s in cycle.samplings}

        climate_by_day = {}
        for c in cycle.pond.farm.climate_records:
            climate_by_day[c.date] = c

        start = min(feed_by_day) if feed_by_day else cycle.start_date
        end = max(feed_by_day) if feed_by_day else cycle.start_date

        alive = cycle.stocked_count
        cumulative_feed = 0.0
        points = []
        recent_fcr_window = []

        current = start
        while current <= end:
            dead = mortality_by_day.get(current, 0)
            alive = max(alive - dead, 0)
            feed = feed_by_day.get(current, 0)
            cumulative_feed += feed
            weight = sample_by_day.get(current)
            biomass = (alive * weight / 1000) if weight else None
            if biomass and biomass > 0:
                recent_fcr_window.append(cumulative_feed / biomass)
            fcr_value = recent_fcr_window[-1] if recent_fcr_window else None
            climate = climate_by_day.get(current)
            points.append(
                {
                    "date": current,
                    "fcr": round(fcr_value, 4) if fcr_value else None,
                    "mortality": dead,
                    "avg_weight_g": weight,
                    "biomass_kg": round(biomass, 2) if biomass else None,
                    "temperature_c": climate.temperature_c if climate else None,
                    "rain_mm": climate.rain_mm if climate else None,
                    "oxygen_mg_l": oxygen_by_day.get(current),
                }
            )
            current += timedelta(days=1)
        return points


class AlertService:
    def __init__(self, metrics_service: MetricsService):
        self.metrics_service = metrics_service

    def generate_alerts(self, cycle: models.Cycle) -> list[Alert]:
        alerts: list[Alert] = []
        points = self.metrics_service.trend_points(cycle)

        fcr_series = [p for p in points if p["fcr"] is not None]
        for p in points:
            if p.get("oxygen_mg_l") is not None and p["oxygen_mg_l"] < 3:
                alerts.append(Alert(cycle.id, p["date"], AlertSeverity.critical, "Oxígeno por debajo de 3 mg/L", "oxygen"))
            if p["mortality"] > 180:
                alerts.append(Alert(cycle.id, p["date"], AlertSeverity.critical, "Mortalidad diaria anómala", "mortality"))
            if p["temperature_c"] is not None and (p["temperature_c"] < 26 or p["temperature_c"] > 33):
                alerts.append(Alert(cycle.id, p["date"], AlertSeverity.warning, "Temperatura fuera de rango 26-33°C", "temperature"))

        for idx in range(6, len(fcr_series)):
            prev = [p["fcr"] for p in fcr_series[idx - 6 : idx - 3]]
            curr = [p["fcr"] for p in fcr_series[idx - 3 : idx + 1]]
            if prev and curr and (sum(curr) / len(curr)) > (sum(prev) / len(prev)) * 1.05:
                alerts.append(
                    Alert(
                        cycle.id,
                        fcr_series[idx]["date"],
                        AlertSeverity.warning,
                        "Tendencia FCR 7d en alza",
                        "fcr_trend",
                    )
                )
                break

        rain_map = defaultdict(float)
        for c in cycle.pond.farm.climate_records:
            rain_map[c.date] = c.rain_mm
        for p in points:
            accum = sum(rain_map[p["date"] - timedelta(days=i)] for i in range(3))
            if accum > 80:
                alerts.append(Alert(cycle.id, p["date"], AlertSeverity.warning, "Lluvia acumulada 3d alta", "rain_3d"))
                break

        return sorted(alerts, key=lambda a: (a.date, a.severity.value), reverse=True)
