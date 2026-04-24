from typing import Optional
from sqlalchemy import select
from price_checker.domain.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, session):
        self._session = session

    def buscar_por_username(self, username: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.username == username)
        return self._session.execute(stmt).scalars().first()

    def criar(self, usuario: Usuario) -> Usuario:
        self._session.add(usuario)
        self._session.flush()
        return usuario