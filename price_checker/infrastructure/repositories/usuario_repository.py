from typing import Optional, List
from sqlalchemy import select
from price_checker.domain.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, session):
        self._session = session

    def buscar_por_username(self, username: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.username == username)
        return self._session.execute(stmt).scalars().first()

    def buscar_por_id(self, id: int) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.id == id)
        return self._session.execute(stmt).scalars().first()

    def listar(self) -> List[Usuario]:
        stmt = select(Usuario).order_by(Usuario.id)
        return list(self._session.execute(stmt).scalars().all())

    def criar(self, usuario: Usuario) -> Usuario:
        self._session.add(usuario)
        self._session.flush()
        return usuario

    def excluir(self, usuario: Usuario) -> None:
        self._session.delete(usuario)
        self._session.flush()