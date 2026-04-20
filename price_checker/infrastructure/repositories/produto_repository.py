from typing import Optional
from sqlalchemy import select
from price_checker.infrastructure.repositories.interfaces import IProdutoRepository
from price_checker.domain.models.produto import Produto, ProdutoCodigo
import logging

logger = logging.getLogger(__name__)


class ProdutoRepository(IProdutoRepository):
    def __init__(self, session) -> None:
        self._session = session

    def listar_paginado(self, limit: int = 50, offset: int = 0):
        logger.debug("Query listar_paginado | limit=%s offset=%s", limit, offset)
        stmt = select(Produto).offset(offset).limit(limit)
        return self._session.execute(stmt).scalars().all()

    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:
        logger.debug("Query obter_por_codigo | codigo=%s", codigo)
        stmt = (
            select(Produto)
            .join(ProdutoCodigo)
            .where(ProdutoCodigo.codigo == codigo)
        )
        return self._session.execute(stmt).scalars().first()