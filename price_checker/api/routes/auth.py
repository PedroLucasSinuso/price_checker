from fastapi import APIRouter, Depends, HTTPException
from price_checker.api.deps import get_db, require_admin
from price_checker.infrastructure.repositories.usuario_repository import UsuarioRepository
from price_checker.application.services.auth_service import AuthService
from price_checker.schemas.auth_schema import LoginRequest, TokenResponse
from price_checker.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from price_checker.domain.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=TokenResponse)
def login(dados: LoginRequest, db=Depends(get_db)):
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
        raise HTTPException(status_code=409, detail=str(e))