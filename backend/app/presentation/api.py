import csv
import io
import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.application.repositories import ClimateRepository, CycleRepository, FarmRepository, PondRepository
from app.application.services import AlertService, MetricsService
from app.infrastructure.db import get_db
from app.infrastructure import models
from app.presentation.schemas import AlertOut, ClimateOut, CycleOut, DashboardOut, FarmOut, MetricsOut, PondOut

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/farms", response_model=list[FarmOut])
def list_farms(db: Session = Depends(get_db)):
    return FarmRepository(db).list()


@router.get("/ponds", response_model=list[PondOut])
def list_ponds(farm_id: int | None = None, db: Session = Depends(get_db)):
    return PondRepository(db).list(farm_id=farm_id)


@router.get("/cycles", response_model=list[CycleOut])
def list_cycles(pond_id: int | None = None, db: Session = Depends(get_db)):
    return CycleRepository(db).list(pond_id=pond_id)


def _load_cycle(db: Session, cycle_id: int) -> models.Cycle:
    stmt = (
        select(models.Cycle)
        .options(
            selectinload(models.Cycle.feedings),
            selectinload(models.Cycle.mortalities),
            selectinload(models.Cycle.water_parameters),
            selectinload(models.Cycle.samplings),
            selectinload(models.Cycle.pond).selectinload(models.Pond.farm).selectinload(models.Farm.climate_records),
        )
        .where(models.Cycle.id == cycle_id)
    )
    cycle = db.scalars(stmt).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return cycle


@router.get("/metrics", response_model=MetricsOut)
def get_metrics(cycle_id: int = Query(...), db: Session = Depends(get_db)):
    cycle = _load_cycle(db, cycle_id)
    metrics = MetricsService(db).compute_metrics(cycle)
    return metrics.__dict__


@router.get("/alerts", response_model=list[AlertOut])
def get_alerts(cycle_id: int = Query(...), db: Session = Depends(get_db)):
    cycle = _load_cycle(db, cycle_id)
    alerts = AlertService(MetricsService(db)).generate_alerts(cycle)
    return [
        {
            "cycle_id": a.cycle_id,
            "date": a.date,
            "severity": a.severity.value,
            "message": a.message,
            "metric": a.metric,
        }
        for a in alerts
    ]


@router.get("/climate", response_model=list[ClimateOut])
def get_climate(
    farm_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    date_to = date_to or date.today()
    date_from = date_from or date_to - timedelta(days=30)
    return ClimateRepository(db).list(farm_id=farm_id, date_from=date_from, date_to=date_to)


@router.get("/cycles/{cycle_id}/dashboard", response_model=DashboardOut)
def get_dashboard(cycle_id: int, db: Session = Depends(get_db)):
    cycle = _load_cycle(db, cycle_id)
    points = MetricsService(db).trend_points(cycle)
    stripped = [{k: v for k, v in p.items() if k != "oxygen_mg_l"} for p in points]
    return {"cycle_id": cycle_id, "points": stripped}


@router.get("/reports/export")
def export_report(cycle_id: int, db: Session = Depends(get_db)):
    cycle = _load_cycle(db, cycle_id)
    metrics = MetricsService(db).compute_metrics(cycle)
    alerts = AlertService(MetricsService(db)).generate_alerts(cycle)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    for key, value in metrics.__dict__.items():
        writer.writerow([key, value])
    writer.writerow([])
    writer.writerow(["alerts_date", "severity", "metric", "message"])
    for alert in alerts:
        writer.writerow([alert.date.isoformat(), alert.severity.value, alert.metric, alert.message])

    output.seek(0)
    logger.info("Generated report for cycle_id=%s", cycle_id)
    headers = {"Content-Disposition": f"attachment; filename=cycle_{cycle_id}_report.csv"}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)
