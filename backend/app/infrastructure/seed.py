import random
from datetime import date, timedelta

from app.infrastructure.db import Base, SessionLocal, engine
from app.infrastructure.models import (
    ClimateDaily,
    Cycle,
    Farm,
    FeedingDaily,
    MortalityDaily,
    Pond,
    WaterParameterDaily,
    WeeklySampling,
)

SEED = 42


def run_seed():
    random.seed(SEED)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        farms = [
            Farm(name="ALTAMA Costa Norte", location="Guayas"),
            Farm(name="ALTAMA Estero Azul", location="El Oro"),
        ]
        db.add_all(farms)
        db.flush()

        ponds: list[Pond] = []
        for farm in farms:
            for i in range(1, 11):
                ponds.append(Pond(farm_id=farm.id, name=f"P-{i:02d}", area_ha=round(random.uniform(0.8, 1.4), 2)))
        db.add_all(ponds)
        db.flush()

        today = date.today()
        all_cycles: list[Cycle] = []

        for farm in farms:
            farm_ponds = [p for p in ponds if p.farm_id == farm.id]
            for idx, pond in enumerate(farm_ponds):
                active = Cycle(
                    pond_id=pond.id,
                    code=f"ACT-{farm.id}-{idx+1}",
                    start_date=today - timedelta(days=119),
                    end_date=None,
                    stocked_count=120000,
                    status="active",
                    seed_cost=120000 * 0.012,
                )
                historical = Cycle(
                    pond_id=pond.id,
                    code=f"HIS-{farm.id}-{idx+1}",
                    start_date=today - timedelta(days=260),
                    end_date=today - timedelta(days=140),
                    stocked_count=115000,
                    status="closed",
                    seed_cost=115000 * 0.011,
                )
                all_cycles.extend([active, historical])

        db.add_all(all_cycles)
        db.flush()

        for farm in farms:
            for d in range(0, 365):
                cdate = today - timedelta(days=d)
                temp = random.uniform(27, 32)
                rain = max(0, random.gauss(18, 15))
                wind = random.uniform(7, 24)
                if d in (2, 3, 4):
                    rain += 35
                if d == 7:
                    temp = 34.8
                db.add(ClimateDaily(farm_id=farm.id, date=cdate, temperature_c=round(temp, 2), rain_mm=round(rain, 2), wind_kmh=round(wind, 2)))

        for cycle in all_cycles:
            days = 120
            start = cycle.start_date
            for d in range(days):
                cdate = start + timedelta(days=d)
                day_factor = 1 + (d / days)
                feed_kg = random.uniform(45, 130) * day_factor
                if d > 100:
                    feed_kg *= 1.1
                if d in (108, 109, 110):
                    feed_kg *= 1.25
                db.add(
                    FeedingDaily(
                        cycle_id=cycle.id,
                        date=cdate,
                        feed_kg=round(feed_kg, 2),
                        feed_cost_usd=round(feed_kg * 0.92, 2),
                        energy_cost_usd=round(feed_kg * 0.08, 2),
                        chemical_cost_usd=round(feed_kg * 0.03, 2),
                    )
                )

                mortality = int(random.uniform(20, 120))
                if d in (111, 112):
                    mortality = 240
                db.add(MortalityDaily(cycle_id=cycle.id, date=cdate, dead_count=mortality))

                oxygen = random.uniform(3.6, 5.8)
                if d == 113:
                    oxygen = 2.4
                db.add(WaterParameterDaily(cycle_id=cycle.id, date=cdate, oxygen_mg_l=round(oxygen, 2), ph=round(random.uniform(7.2, 8.4), 2)))

                if d % 7 == 0:
                    avg_weight = 1.5 + (d * 0.33) + random.uniform(-0.4, 0.6)
                    db.add(WeeklySampling(cycle_id=cycle.id, date=cdate, avg_weight_g=round(max(avg_weight, 1), 2)))

        db.commit()
        print("Seed completed successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
