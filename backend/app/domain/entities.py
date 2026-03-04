from dataclasses import dataclass
from datetime import date
from enum import Enum


class AlertSeverity(str, Enum):
    warning = "WARNING"
    critical = "CRITICAL"


@dataclass
class KPIBundle:
    cycle_id: int
    feed_total_kg: float
    biomass_gain_kg: float
    estimated_biomass_kg: float
    survival_rate: float
    adg_g_per_day: float
    fcr: float
    cost_per_lb: float
    estimated_margin_per_lb: float


@dataclass
class Alert:
    cycle_id: int
    date: date
    severity: AlertSeverity
    message: str
    metric: str
