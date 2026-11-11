import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def check_connection() -> None:
    backend_directory = Path(__file__).resolve().parents[3]
    load_dotenv(backend_directory / ".env")

    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url:
        raise RuntimeError("Chưa cấu hình DATABASE_URL trong .env.")

    url = make_url(database_url)

    if url.drivername not in {
        "postgres",
        "postgresql",
        "postgresql+psycopg",
    }:
        raise RuntimeError("DATABASE_URL phải sử dụng PostgreSQL.")

    url = url.set(drivername="postgresql+psycopg")

    engine = create_engine(url, pool_pre_ping=True)

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database(), 1")
            ).one()

            print("Kết nối PostgreSQL thành công.")
            print(f"Database: {result[0]}")
            print(f"SELECT 1: {result[1]}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    check_connection()