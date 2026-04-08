from pydantic import BaseModel, field_validator
from utils.codigo import Codigo

class Produto(BaseModel):
    id: int
    codigo_chamada: str
    grupo: str
    familia: str
    nome: str
    preco_venda: float
    preco_custo: float
    estoque: int
    codigo: str

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        return Codigo(v).valor
