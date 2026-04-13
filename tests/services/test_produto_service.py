from pytest import approx
from unittest.mock import Mock
from price_checker.models.produto import Produto
from price_checker.schemas.produto_schema import ProdutoResponse
from price_checker.services.produto_service import ProdutoService

def test_produto_response():
    produto = Produto(
        codigo_chamada="000123",
        nome="Teste",
        grupo="Grupo",
        familia="Familia",
        preco_custo=10,
        preco_venda=15,
        estoque=10
    )

    response = ProdutoResponse.model_validate(produto)

    assert response.codigo_chamada == "000123"
    assert response.nome == "Teste"
    assert response.markup == approx(0.5, abs=0.01)
    assert response.margem == approx(0.33, abs=0.01)

def test_obter_com_metricas():
    produto_mock = Produto(
        codigo_chamada="000123",
        nome="Teste",
        grupo="Grupo",
        familia="Familia",
        preco_custo=10,
        preco_venda=15,
        estoque=10
    )

    repo_mock = Mock()
    repo_mock.obter_por_codigo.return_value = produto_mock

    service = ProdutoService(repo_mock)

    result = service.obter_com_metricas("000123")

    assert result is not None
    assert result.codigo_chamada == "000123"