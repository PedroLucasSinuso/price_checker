#Produto repository: classe responsável por acessar os dados dos produtos no banco de dados cache
#Repository com sessão interna porque não sei fazer com sessão externa
from contextlib import contextmanager
from typing import List, Dict, Optional
from sqlalchemy import insert, select
from ..db.session import SqliteSession
from ..models.produto import Produto
from ..utils.codigo import Codigo


class ProdutoRepository:
    def __init__(self) -> None:
        pass

    @contextmanager
    def _session_scope(self):
        # Encapsula e gerencia a sessão do banco de dados
        session = SqliteSession()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def replace_all(self, produtos: List[Dict]) -> None:
        with self._session_scope() as session:
            session.query(Produto).delete()
            session.execute(insert(Produto), produtos)

    def listar(self) -> List[Produto]:
        with self._session_scope() as session:
            return session.query(Produto).all()
        
    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:
        codigo_valor = Codigo(codigo).valor
        
        with self._session_scope() as session:
            stmt = select(Produto).where(Produto.codigo == codigo_valor)
            return session.execute(stmt).scalars().first()
