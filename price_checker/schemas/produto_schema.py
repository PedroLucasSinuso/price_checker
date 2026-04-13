from pydantic import BaseModel

# Schema: define o formato/contrato de dados para validacao e resposta da API.
class ProdutoResponse(BaseModel):
    codigo_chamada: str
    grupo: str
    familia: str
    nome: str
    preco_venda: float
    preco_custo: float
    estoque: float
    markup: float
    margem: float
    codigo_buscado: str | None = None

    model_config = {
        "from_attributes": True
    }
