import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/altama")
API_TITLE = "ALTAMA Shrimp Intelligence API"
