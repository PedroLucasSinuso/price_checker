from price_checker.infrastructure.db.database import Base
from price_checker.infrastructure.db.session import sqlite_engine
import price_checker.domain.models.produto
import price_checker.domain.models.cache_status
import price_checker.domain.models.usuario
def init_db():
    Base.metadata.create_all(bind=sqlite_engine)