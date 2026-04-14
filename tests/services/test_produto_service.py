import pytest
from unittest.mock import Mock
from price_checker.models.produto import Produto
from price_checker.services.produto_service import ProdutoService

# Fixtures
@pytest.fixture
def produto():
    return Produto(
        codigo_chamada="000123",
        nome="Teste",
        grupo="Grupo",
        familia="Familia",
        preco_custo=10,
        preco_venda=15,
        estoque=10,
        codigos=[],
    )

@pytest.fixture
def repo_mock(produto):
    repo = Mock()
    repo.obter_por_codigo.return_value = produto
    repo.listar_paginado.return_value = []
    return repo

# obter_com_metricas
def test_obter_com_metricas_chama_repo_com_codigo_normalizado(repo_mock):
    service = ProdutoService(repo_mock)

    service.obter_com_metricas(" 000123 ")

    repo_mock.obter_por_codigo.assert_called_once_with("000123")

def test_obter_com_metricas_retorna_response_com_codigo_buscado(repo_mock):
    service = ProdutoService(repo_mock)

    result = service.obter_com_metricas("000123")

    assert result is not None
    assert result.codigo_buscado == "000123"

def test_obter_com_metricas_produto_nao_encontrado(repo_mock):
    repo_mock.obter_por_codigo.return_value = None

    service = ProdutoService(repo_mock)

    result = service.obter_com_metricas("000123")

    assert result is None

def test_obter_com_metricas_codigo_invalido(repo_mock):
    service = ProdutoService(repo_mock)

    with pytest.raises(ValueError):
        service.obter_com_metricas("abc")

    repo_mock.obter_por_codigo.assert_not_called()
    
# listar_paginado
@pytest.mark.parametrize("limit_entrada, limit_esperado", [
    (200, 100),
    (0, 1),
    (50, 50),
])
def test_listar_paginado_clamp(repo_mock, limit_entrada, limit_esperado):
    service = ProdutoService(repo_mock)

    service.listar_paginado(limit=limit_entrada, offset=5)

    repo_mock.listar_paginado.assert_called_once_with(limit_esperado, 5)