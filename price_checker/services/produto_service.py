from typing import List, Optional
from price_checker.repositories.interfaces import IProdutoRepository
from price_checker.models.produto import Produto

# Service: centraliza regras de negocio e coordena acesso ao repositorio.
class ProdutoService:
    def __init__(self, repo: IProdutoRepository):
        self.repo = repo

    def listar_paginado(self, limit: int = 50, offset: int = 0) -> List[Produto]:
        limit = max(1, min(limit, 100))  # Limite máximo de 100 para evitar sobrecarga
        return self.repo.listar_paginado(limit, offset)

    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:
        produto = self.repo.obter_por_codigo(codigo)
        
        if not produto:
            self._log_nao_encontrado(codigo)

        return produto

    def _log_nao_encontrado(self, codigo:str):
        print(f"Produto com código '{codigo}' não encontrado.")
        #todo: inserir em tabela persistida de logs para auditoria futura

