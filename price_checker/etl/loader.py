from sqlalchemy import text

from price_checker.db.session import PostgresSession

class PostgresLoader:
    def __init__(self, query: str):
        self.query = query

    def load(self) -> list[dict]:
        with PostgresSession() as session:
            result = session.execute(text(self.query))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
