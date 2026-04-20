from typing import List, Optional
from price_checker.infrastructure.repositories.interfaces import IProdutoRepository
from price_checker.domain.models.produto import Produto
import logging

logger = logging.getLogger(__name__)


class ProdutoService:
    def __init__(self, repo: IProdutoRepository):
        self.repo = repo

    def listar_paginado(self, limit: int = 50, offset: int = 0) -> List[Produto]:
        limit = max(1, min(limit, 100))
        return self.repo.listar_paginado(limit, offset)

    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:
        produto = self.repo.obter_por_codigo(codigo)

        if not produto:
            logger.warning("Produto não encontrado | codigo=%s", codigo)

        return produto