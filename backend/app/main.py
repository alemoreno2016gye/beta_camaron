import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import API_TITLE, DB_STARTUP_MAX_RETRIES, DB_STARTUP_RETRY_DELAY_SECONDS
from app.infrastructure.db import Base, SessionLocal, engine
from app.presentation.api import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title=API_TITLE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def _wait_for_db_ready() -> None:
    last_error: Exception | None = None
    for attempt in range(1, DB_STARTUP_MAX_RETRIES + 1):
        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            logger.info("Database connection ready on attempt %s", attempt)
            return
        except SQLAlchemyError as exc:
            last_error = exc
            logger.warning(
                "Database not ready (attempt %s/%s). Retrying in %ss.",
                attempt,
                DB_STARTUP_MAX_RETRIES,
                DB_STARTUP_RETRY_DELAY_SECONDS,
            )
            time.sleep(DB_STARTUP_RETRY_DELAY_SECONDS)

    raise RuntimeError("Database was not ready before startup timeout") from last_error


@app.on_event("startup")
def startup():
    _wait_for_db_ready()
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema ensured")


app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
