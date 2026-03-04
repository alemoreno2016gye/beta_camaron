from datetime import date
from pydantic import BaseModel


class FarmOut(BaseModel):
    id: int
    name: str
    location: str


class PondOut(BaseModel):
    id: int
    farm_id: int
    name: str
    area_ha: float


class CycleOut(BaseModel):
    id: int
    pond_id: int
    code: str
    start_date: date
    end_date: date | None
    stocked_count: int
    status: str


class MetricsOut(BaseModel):
    cycle_id: int
    feed_total_kg: float
    biomass_gain_kg: float
    estimated_biomass_kg: float
    survival_rate: float
    adg_g_per_day: float
    fcr: float
    cost_per_lb: float
    estimated_margin_per_lb: float


class AlertOut(BaseModel):
    cycle_id: int
    date: date
    severity: str
    message: str
    metric: str


class ClimateOut(BaseModel):
    farm_id: int
    date: date
    temperature_c: float
    rain_mm: float
    wind_kmh: float


class TrendPoint(BaseModel):
    date: date
    fcr: float | None
    mortality: int
    avg_weight_g: float | None
    biomass_kg: float | None
    temperature_c: float | None
    rain_mm: float | None


class DashboardOut(BaseModel):
    cycle_id: int
    points: list[TrendPoint]
