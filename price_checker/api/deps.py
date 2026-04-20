from fastapi import Depends
from price_checker.infrastructure.db.session import SqliteSession
from price_checker.infrastructure.repositories.produto_repository import ProdutoRepository


def get_db():
    session = SqliteSession()
    try:
        yield session
    finally:
        session.close()

def get_produto_repository(db=Depends(get_db)):
    return ProdutoRepository(db)