from price_checker.domain.models.usuario import Usuario
from price_checker.infrastructure.repositories.usuario_repository import UsuarioRepository
from price_checker.schemas.usuario_schema import UsuarioCreate
from price_checker.application.utils.security import hash_password, verify_password
from price_checker.application.utils.jwt_handler import create_access_token


class AuthService:
    def __init__(self, repo: UsuarioRepository):
        self.repo = repo

    def autenticar(self, username: str, password: str) -> str:
        usuario = self.repo.buscar_por_username(username)

        if not usuario or not verify_password(password, usuario.hashed_password):
            raise ValueError("Credenciais inválidas")

        return create_access_token({"sub": usuario.username, "role": usuario.role})

    def registrar(self, dados: UsuarioCreate) -> Usuario:
        if self.repo.buscar_por_username(dados.username):
            raise ValueError(f"Username '{dados.username}' já está em uso")

        usuario = Usuario(
            username=dados.username,
            nome_exibicao=dados.nome_exibicao,
            role=dados.role,
            hashed_password=hash_password(dados.password),
        )

        return self.repo.criar(usuario)