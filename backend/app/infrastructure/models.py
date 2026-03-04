from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db import Base


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[str] = mapped_column(String(120), nullable=False)

    ponds: Mapped[list["Pond"]] = relationship(back_populates="farm")
    climate_records: Mapped[list["ClimateDaily"]] = relationship(back_populates="farm")


class Pond(Base):
    __tablename__ = "ponds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    area_ha: Mapped[float] = mapped_column(Float, nullable=False)

    farm: Mapped[Farm] = relationship(back_populates="ponds")
    cycles: Mapped[list["Cycle"]] = relationship(back_populates="pond")


class Cycle(Base):
    __tablename__ = "cycles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pond_id: Mapped[int] = mapped_column(ForeignKey("ponds.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date | None] = mapped_column(Date)
    stocked_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    seed_cost: Mapped[float] = mapped_column(Float, default=0)

    pond: Mapped[Pond] = relationship(back_populates="cycles")
    feedings: Mapped[list["FeedingDaily"]] = relationship(back_populates="cycle")
    mortalities: Mapped[list["MortalityDaily"]] = relationship(back_populates="cycle")
    water_parameters: Mapped[list["WaterParameterDaily"]] = relationship(back_populates="cycle")
    samplings: Mapped[list["WeeklySampling"]] = relationship(back_populates="cycle")


class FeedingDaily(Base):
    __tablename__ = "feeding_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("cycles.id"), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    feed_kg: Mapped[float] = mapped_column(Float, nullable=False)
    feed_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    energy_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    chemical_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)

    cycle: Mapped[Cycle] = relationship(back_populates="feedings")


class MortalityDaily(Base):
    __tablename__ = "mortality_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("cycles.id"), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    dead_count: Mapped[int] = mapped_column(Integer, nullable=False)

    cycle: Mapped[Cycle] = relationship(back_populates="mortalities")


class WaterParameterDaily(Base):
    __tablename__ = "water_parameter_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("cycles.id"), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    oxygen_mg_l: Mapped[float] = mapped_column(Float, nullable=False)
    ph: Mapped[float] = mapped_column(Float, nullable=False)

    cycle: Mapped[Cycle] = relationship(back_populates="water_parameters")


class WeeklySampling(Base):
    __tablename__ = "weekly_sampling"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("cycles.id"), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    avg_weight_g: Mapped[float] = mapped_column(Float, nullable=False)

    cycle: Mapped[Cycle] = relationship(back_populates="samplings")


class ClimateDaily(Base):
    __tablename__ = "climate_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    rain_mm: Mapped[float] = mapped_column(Float, nullable=False)
    wind_kmh: Mapped[float] = mapped_column(Float, nullable=False)

    farm: Mapped[Farm] = relationship(back_populates="climate_records")
