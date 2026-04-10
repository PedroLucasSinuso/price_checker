from sqlalchemy import text

from price_checker.db.session import PostgresSession

class PostgresLoader:
    def __init__(self, query: str):
        self.query = query

    def load(self) -> list[dict]:
        with PostgresSession() as session:
            query = self.query.lstrip("\ufeff").strip()
            result = session.execute(text(query))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
