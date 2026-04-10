#Produto repository: classe responsável por acessar os dados dos produtos no banco de dados cache
#Repository com sessão interna porque não sei fazer com sessão externa
from contextlib import contextmanager
from typing import List, Optional
from sqlalchemy import insert, select
from price_checker.db.session import SqliteSession
from price_checker.models.produto import Produto


class ProdutoRepository:
    def __init__(self) -> None:
        pass

    @contextmanager
    def _session_scope(self):
        # Encapsula e gerencia a sessão do banco de dados 
        # Dívida técnica a ser resolvida posteriormente: sessão interna acoplada ao repositório
        # todo: refatorar para usar sessão externa
        session = SqliteSession()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def replace_all(self, produtos: List[Produto]) -> None:
        with self._session_scope() as session:
            session.query(Produto).delete()

            data = [
                {
                    "id": p.id,
                    "codigo_chamada": p.codigo_chamada,
                    "nome": p.nome,
                    "grupo": p.grupo,
                    "familia": p.familia,
                    "preco_venda": p.preco_venda,
                    "preco_custo": p.preco_custo,
                    "estoque": p.estoque,
                    "codigo": p.codigo,
                }
                for p in produtos
            ]

            session.execute(insert(Produto), data)

    def listar(self) -> List[Produto]:
        with self._session_scope() as session:
            return session.query(Produto).all()
        
    def obter_por_codigo(self, codigo: str) -> Optional[Produto]:  
        with self._session_scope() as session:
            stmt = select(Produto).where(Produto.codigo == codigo)
            return session.execute(stmt).scalars().first()

