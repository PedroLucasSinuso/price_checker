from typing import Literal, Optional
from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    username: str
    nome_exibicao: str
    password: str
    role: Literal["operador", "supervisor", "admin"]


class UsuarioResponse(BaseModel):
    id: int
    username: str
    nome_exibicao: str
    role: str

    model_config = {"from_attributes": True}

class UsuarioPatch(BaseModel):
    password: Optional[str] = None
    role: Optional[Literal["operador", "supervisor", "admin"]] = None

    def tem_alteracao(self) -> bool:
        return self.password is not None or self.role is not None