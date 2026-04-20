from typing import Optional
from abc import ABC, abstractmethod
from price_checker.domain.models.produto import Produto


class IProdutoRepository(ABC):
    @abstractmethod
    def listar_paginado(self, limit: int, offset: int) -> list[Produto]:
        pass

    @abstractmethod
    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:
        pass