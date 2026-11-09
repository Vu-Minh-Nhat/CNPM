from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker


class Database:
    def __init__(self, database_url: str):
        if not database_url or not database_url.strip():
            raise ValueError("Chưa cấu hình DATABASE_URL.")

        url = make_url(database_url.strip())

        if url.drivername not in {
            "postgres",
            "postgresql",
            "postgresql+psycopg",
        }:
            raise ValueError("DATABASE_URL phải sử dụng PostgreSQL.")

        url = url.set(drivername="postgresql+psycopg")

        self.engine = create_engine(
            url,
            pool_pre_ping=True,
        )

        self._session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def create_session(self) -> Session:
        return self._session_factory()

    def dispose(self) -> None:
        self.engine.dispose()