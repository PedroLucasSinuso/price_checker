from typing import List, Optional
from price_checker.repositories.produto_repository import ProdutoRepository
from price_checker.models.produto import Produto
from price_checker.utils.codigo import Codigo
from price_checker.schemas.produto_schema import ProdutoResponse

# Service: centraliza regras de negocio e coordena acesso ao repositorio.
class ProdutoService:
    def __init__(self, repo: ProdutoRepository):
        self.repo = repo

    def listar(self) -> List[Produto]:
        return self.repo.listar()

    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:
        codigo_valido = Codigo(codigo)
        return self.repo.obter_por_codigo(codigo_valido.valor)

    def obter_com_metricas(self, codigo: str) -> Optional[ProdutoResponse]:
        produto = self.obter_por_codigo(codigo)
        if not produto:
            return None
        return ProdutoResponse.model_validate(produto)

