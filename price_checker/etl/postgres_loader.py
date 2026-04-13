from sqlalchemy import text
from price_checker.etl.interfaces import DataSource
from price_checker.db.session import PostgresSession

class PostgresLoader(DataSource):
    def __init__(self, query: str):
        self.query = query

    def load(self) -> list[dict]:
        if not PostgresSession:
            raise RuntimeError("PostgreSQL não configurado. Verifique as variáveis de ambiente.")
        
        with PostgresSession() as session:
            query = self.query.lstrip("\ufeff").strip()
            result = session.execute(text(query))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
