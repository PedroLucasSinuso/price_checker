from ..db.database import Base
from ..db.session import sqlite_engine

def init_db():
    Base.metadata.create_all(bind=sqlite_engine)