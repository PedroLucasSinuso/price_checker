from pytest import approx
from price_checker.models.produto import Produto, ProdutoCodigo

def test_metricas_produto():
    produto = Produto(
        codigo_chamada="000123",
        preco_custo=10.0,
        preco_venda=15.0,
        estoque=100,
        grupo="Eletrônicos",
        familia="Smartphones",
        nome="Smartphone XYZ",
        codigos=[
            ProdutoCodigo(codigo="1234567891234"),
            ProdutoCodigo( codigo_chamada="000123")
        ]
    )
    assert len(produto.codigos) == 2
    assert produto.codigos[0].codigo == "1234567891234"
    assert produto.markup == approx(0.5, abs=0.01)
    assert produto.margem == approx(0.33, abs=0.01)

