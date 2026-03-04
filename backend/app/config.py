import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/altama")
API_TITLE = "ALTAMA Shrimp Intelligence API"
DB_STARTUP_MAX_RETRIES = int(os.getenv("DB_STARTUP_MAX_RETRIES", "20"))
DB_STARTUP_RETRY_DELAY_SECONDS = float(os.getenv("DB_STARTUP_RETRY_DELAY_SECONDS", "2"))
