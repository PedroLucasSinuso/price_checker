from typing import List, Optional
from sqlalchemy import select
from price_checker.repositories.interfaces import IProdutoRepository
from price_checker.models.produto import Produto, ProdutoCodigo

class ProdutoRepository(IProdutoRepository):
    """
    Implementação concreta do repositório de produtos usando SQLAlchemy. 
    Esta classe é responsável por interagir com o banco de dados para realizar operações relacionadas a produtos.
    """
    def __init__(self, session) -> None:
        self._session = session

    def listar_paginado(self, limit: int = 50, offset: int = 0):
        stmt = select(Produto).offset(offset).limit(limit)
        return self._session.execute(stmt).scalars().all()

    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:  
        stmt = (
            select(Produto)
            .join(ProdutoCodigo)
            .where(ProdutoCodigo.codigo == codigo)
           )
        return self._session.execute(stmt).scalars().first()

