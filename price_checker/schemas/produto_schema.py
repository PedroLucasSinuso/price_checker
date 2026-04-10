from pydantic import BaseModel

# Schema: define o formato/contrato de dados para validacao e resposta da API.
class ProdutoResponse(BaseModel):
    id: int
    codigo_chamada: str
    grupo: str
    familia: str
    nome: str
    preco_venda: float
    preco_custo: float
    estoque: int
    markup: float
    margem: float

    model_config = {
        "from_attributes": True
    }
