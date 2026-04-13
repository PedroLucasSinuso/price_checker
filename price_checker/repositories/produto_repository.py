from typing import List, Optional
from sqlalchemy import select
from price_checker.models.produto import Produto, ProdutoCodigo

#Produto repository: classe responsável por acessar os dados dos produtos no banco de dados cache (SQLite)
class ProdutoRepository:
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

