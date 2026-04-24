from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from price_checker.infrastructure.db.session import SqliteSession
from price_checker.infrastructure.repositories.produto_repository import ProdutoRepository
from price_checker.infrastructure.repositories.usuario_repository import UsuarioRepository
from price_checker.domain.models.usuario import Usuario
from price_checker.application.utils.jwt_handler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db():
    session = SqliteSession()
    try:
        yield session
    finally:
        session.close()


def get_produto_repository(db=Depends(get_db)):
    return ProdutoRepository(db)


def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)) -> Usuario:
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario = UsuarioRepository(db).buscar_por_username(username)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return usuario


def require_supervisor(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.role not in ("supervisor", "admin"):
        raise HTTPException(status_code=403, detail="Acesso restrito a supervisores")
    return usuario


def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return usuario