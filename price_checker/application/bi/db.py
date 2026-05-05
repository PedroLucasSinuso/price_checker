from sqlalchemy import Engine, create_engine
from price_checker.core.config import settings

_engine: Engine | None = None


def get_bi_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=3,
            connect_args={"connect_timeout": 10},
        )
    return _engine