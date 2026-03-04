# ALTAMA Shrimp Intelligence (MVP SaaS)

MVP full-stack para camaroneras con **datos 100% simulados**, listo para demo local en un día.

## Stack
- Backend: FastAPI + SQLAlchemy + Pydantic + pytest
- Frontend: Next.js (App Router) + TypeScript + Recharts
- DB: PostgreSQL
- Infra: Docker Compose

## Arquitectura (Clean + SOLID)
`backend/app` está organizado por capas:
- `domain/`: entidades de negocio puras (KPIs, Alert).
- `application/`: servicios y casos de uso (`MetricsService`, `AlertService`, repositorios).
- `infrastructure/`: ORM, DB session, seed reproducible.
- `presentation/`: routers FastAPI y schemas de salida.

Decisiones de diseño:
1. **Controladores delgados**: la lógica de negocio vive en `application/services.py`.
2. **Cálculo reproducible**: seed fijo (`SEED=42`) y reglas determinísticas para demo.
3. **UX de demo**: dashboards y alertas visibles con 3+ alertas críticas simuladas.

## Estructura del repo
```
/backend
  /app
    /domain
    /application
    /infrastructure
    /presentation
  /tests
/frontend (Next app router)
docker-compose.yml
README.md
```

## Requisitos
- Docker + Docker Compose plugin

## Setup local (rápido)
```bash
docker compose up --build -d
```

Servicios:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- DB PostgreSQL: localhost:5432

## Seed de datos simulados
> Genera automáticamente 2 fincas, 20 piscinas, ciclos activos/históricos y 120 días de series productivas por ciclo.

```bash
docker compose exec backend python -m app.infrastructure.seed
```

## Endpoints principales
- `GET /farms`
- `GET /ponds?farm_id=...`
- `GET /cycles?pond_id=...`
- `GET /metrics?cycle_id=...`
- `GET /alerts?cycle_id=...`
- `GET /climate?farm_id=...&date_from=...&date_to=...`
- `GET /cycles/{cycle_id}/dashboard`
- `GET /reports/export?cycle_id=...` (CSV)

## KPIs implementados
- FCR = `feed_total / biomass_gain`
- Biomasa estimada = `vivos_estimados * peso_promedio`
- Supervivencia = `vivos_estimados / sembrados`
- ADG = `delta_peso / delta_dias`
- Costo por lb = `(balanceado + energía + larvas + químicos)/libras_estimadas`
- Margen = `precio_venta_lb - costo_lb`

## Reglas de alertas
- Oxígeno < 3 mg/L => **CRITICAL**
- Tendencia FCR 7d al alza => **WARNING**
- Mortalidad diaria > umbral => **CRITICAL**
- Temperatura fuera 26-33 => **WARNING**
- Lluvia acumulada 3d alta => **WARNING**

## Testing mínimo
```bash
docker compose exec backend pytest -q
```

## Usuario / contraseña demo
No aplica en este MVP (sin auth para acelerar demo).

## Demo script (8-10 minutos)
1. **(1 min) Contexto**: explicar problema en camaronera y qué resuelve ALTAMA.
2. **(1 min) Home ejecutivo**: abrir `/`, mostrar fincas, ciclos activos, alertas críticas.
3. **(2 min) Farm detail**: entrar a una finca, revisar piscinas y estados operativos.
4. **(2 min) Cycle dashboard**: abrir un ciclo activo y recorrer 4 gráficos:
   - FCR en el tiempo
   - Mortalidad diaria
   - Peso y biomasa
   - Clima vs FCR
5. **(1 min) Alert Center**: filtrar CRITICAL/WARNING y revisar historial.
6. **(1 min) Reports**: descargar CSV y abrirlo para mostrar KPIs + alertas.
7. **(1 min) API/OpenAPI**: abrir `/docs` y mostrar endpoints.
8. **(1 min) Cierre**: roadmap (auth, IoT real, modelos predictivos).

## Comandos útiles
```bash
# levantar todo
docker compose up --build

# seed reproducible
docker compose exec backend python -m app.infrastructure.seed

# tests backend
docker compose exec backend pytest -q
```
