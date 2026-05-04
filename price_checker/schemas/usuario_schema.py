from typing import Literal, Optional
from pydantic import BaseModel, field_validator


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

    @field_validator("password")
    @classmethod
    def senha_nao_vazia(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Senha não pode ser vazia")
        return v

    def tem_alteracao(self) -> bool:
        return self.password is not None or self.role is not None