from sqlalchemy import text
from price_checker.application.etl.interfaces import DataSource
from price_checker.infrastructure.db.session import PostgresSession
import logging

logger = logging.getLogger(__name__)


class PostgresLoader(DataSource):
    def __init__(self, query: str):
        self.query = query

    def load(self) -> list[dict]:
        logger.debug("Executando query no Postgres")

        if not PostgresSession:
            raise RuntimeError("PostgreSQL não configurado. Verifique as variáveis de ambiente.")

        with PostgresSession() as session:
            query = self.query.lstrip("\ufeff").strip()
            result = session.execute(text(query))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]