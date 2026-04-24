from typing import Literal
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