from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure import models


class FarmRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[models.Farm]:
        return self.db.scalars(select(models.Farm)).all()


class PondRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, farm_id: int | None = None) -> list[models.Pond]:
        stmt = select(models.Pond)
        if farm_id:
            stmt = stmt.where(models.Pond.farm_id == farm_id)
        return self.db.scalars(stmt).all()


class CycleRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, pond_id: int | None = None) -> list[models.Cycle]:
        stmt = select(models.Cycle)
        if pond_id:
            stmt = stmt.where(models.Cycle.pond_id == pond_id)
        return self.db.scalars(stmt).all()

    def get(self, cycle_id: int) -> models.Cycle | None:
        return self.db.get(models.Cycle, cycle_id)


class ClimateRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, farm_id: int, date_from: date, date_to: date) -> list[models.ClimateDaily]:
        stmt = (
            select(models.ClimateDaily)
            .where(models.ClimateDaily.farm_id == farm_id)
            .where(models.ClimateDaily.date >= date_from)
            .where(models.ClimateDaily.date <= date_to)
            .order_by(models.ClimateDaily.date)
        )
        return self.db.scalars(stmt).all()
