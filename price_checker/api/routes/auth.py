from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import logging

from price_checker.api.deps import get_db, require_admin
from price_checker.infrastructure.repositories.usuario_repository import UsuarioRepository
from price_checker.application.services.auth_service import AuthService
from price_checker.schemas.auth_schema import TokenResponse
from price_checker.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
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