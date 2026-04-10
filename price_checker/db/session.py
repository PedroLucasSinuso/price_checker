from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from price_checker.core.config import settings

#Postgres
postgres_engine = create_engine(settings.postgres_url) if settings.postgres_url else None
PostgresSession = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

#SQLite
sqlite_engine = create_engine(
    settings.sqlite_url,future=True,
    connect_args={"check_same_thread": False}
)
SqliteSession = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)
