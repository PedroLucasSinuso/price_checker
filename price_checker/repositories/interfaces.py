from typing import Optional
from abc import ABC, abstractmethod
from price_checker.models.produto import Produto


class IProdutoRepository(ABC):
    """
    Interface que define o contrato para o repositório de produtos. Qualquer implementação deve seguir esta interface.

    """
    @abstractmethod
    def listar_paginado(self, limit: int, offset: int) -> list[Produto]:
        pass

    @abstractmethod
    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:
        pass
