from price_checker.models.produto import Produto
from price_checker.schemas.produto_schema import ProdutoResponse
from pytest import approx

def criar_produto_teste() -> Produto:
    return Produto(
        id=1,
        codigo="1234567891234",
        codigo_chamada="000123",
        preco_custo=10.0,
        preco_venda=15.0,
        estoque=100,
        grupo="Eletrônicos",
        familia="Smartphones",
        nome="Smartphone XYZ"
    )

def test_produto_response():
    response = criar_produto_teste()
    assert response.id == 1
    assert response.codigo_chamada == "000123"
    assert response.grupo == "Eletrônicos"
    assert response.familia == "Smartphones"
    assert response.nome == "Smartphone XYZ"
    assert response.preco_venda == 15.0
    assert response.preco_custo == 10.0
    assert response.estoque == 100
    assert response.markup == approx(0.5, abs=0.01)
    assert response.margem == approx(0.33, abs=0.01)