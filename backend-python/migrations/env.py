from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import dotenv_values
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import make_url

import src.infrastructure.models
from src.infrastructure.databases.base import Base


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
arguments = context.get_x_argument(as_dictionary=True)
ENV_FILE = PROJECT_ROOT / arguments.get("env_file", ".env")

settings = dotenv_values(ENV_FILE)
database_url = settings.get("DATABASE_URL")

if not database_url or not database_url.strip():
    raise RuntimeError(
        f"Chưa cấu hình DATABASE_URL trong file {ENV_FILE.name}."
    )

url = make_url(database_url.strip())

if url.drivername not in {
    "postgres",
    "postgresql",
    "postgresql+psycopg",
}:
    raise RuntimeError("Migration yêu cầu PostgreSQL.")

url = url.set(drivername="postgresql+psycopg")

target_metadata = Base.metadata
print(f"Migration database: {url.database}")


def run_migrations_offline():
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()