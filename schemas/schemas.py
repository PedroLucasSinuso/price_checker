from pydantic import BaseModel

class Produto(BaseModel):
    id: int
    codigo_chamada: str
    grupo: str
    familia: str
    nome: str
    descricao: str
    preco_venda: float
    preco_custo: float
    estoque: int
    codigo: str
