from price_checker.infrastructure.db.database import Base
from price_checker.infrastructure.db.session import sqlite_engine

def init_db():
    Base.metadata.create_all(bind=sqlite_engine)