from typing import List, Optional
from price_checker.repositories.produto_repository import ProdutoRepository
from price_checker.models.produto import Produto
from price_checker.utils.codigo import Codigo

# Service: centraliza regras de negocio e coordena acesso ao repositorio.
class ProdutoService:
    def __init__(self, repo: ProdutoRepository):
        self.repo = repo

    def listar_paginado(self, limit: int = 50, offset: int = 0) -> List[Produto]:
        limit = max(1, min(limit, 100))  # Limite máximo de 100 para evitar sobrecarga
        return self.repo.listar_paginado(limit, offset)

    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:
        return self.repo.obter_por_codigo(codigo)


