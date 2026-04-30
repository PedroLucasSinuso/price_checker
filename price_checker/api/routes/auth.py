from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import logging

from price_checker.api.deps import get_db, require_admin
from price_checker.infrastructure.repositories.usuario_repository import UsuarioRepository
from price_checker.application.services.auth_service import AuthService
from price_checker.schemas.auth_schema import TokenResponse
from price_checker.schemas.usuario_schema import UsuarioCreate, UsuarioPatch, UsuarioResponse
from price_checker.domain.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)


@router.post("/token", response_model=TokenResponse)
def login(dados: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    service = AuthService(UsuarioRepository(db))
    try:
        token = service.autenticar(dados.username, dados.password)
    except ValueError:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return TokenResponse(access_token=token)


@router.post("/register", response_model=UsuarioResponse, status_code=201)
def register(dados: UsuarioCreate, db=Depends(get_db), _admin: Usuario = Depends(require_admin)):
    service = AuthService(UsuarioRepository(db))
    try:
        usuario = service.registrar(dados)
        db.commit()
        return usuario
    except ValueError as e:
        logger.warning("Erro ao registrar usuario | Erro: %s", e)
        raise HTTPException(status_code=409, detail="Usuario ja existe ou dados invalidos")


@router.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(db=Depends(get_db), _admin: Usuario = Depends(require_admin)):
    return AuthService(UsuarioRepository(db)).listar()


@router.patch("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioPatch,
    db=Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    service = AuthService(UsuarioRepository(db))
    try:
        usuario = service.atualizar(usuario_id, dados)
        db.commit()
        return usuario
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/usuarios/{usuario_id}", status_code=204)
def excluir_usuario(
    usuario_id: int,
    db=Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    service = AuthService(UsuarioRepository(db))
    try:
        service.excluir(usuario_id, admin.id)
        db.commit()
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))