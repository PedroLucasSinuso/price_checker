import pytest
from contextlib import ExitStack
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from price_checker.main import app
from price_checker.api.deps import get_db
from price_checker.infrastructure.db.database import Base
from price_checker.application.utils.security import hash_password
from price_checker.domain.models.usuario import Usuario
from price_checker.schemas.bi_schema import SkuDTO, PontoDiarioDTO, PontoHoraDTO


# ─── Setup do banco de testes ────────────────────────────────────────────────

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="function")
def db_session(reset_db):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ─── Fixtures de usuários e tokens ───────────────────────────────────────────

@pytest.fixture
def usuario_operador(db_session):
    user = Usuario(
        username="operador1",
        nome_exibicao="Operador Um",
        role="operador",
        hashed_password=hash_password("senha123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def usuario_supervisor(db_session):
    user = Usuario(
        username="supervisor1",
        nome_exibicao="Supervisor Um",
        role="supervisor",
        hashed_password=hash_password("senha123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def usuario_admin(db_session):
    user = Usuario(
        username="admin1",
        nome_exibicao="Admin Um",
        role="admin",
        hashed_password=hash_password("senha123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_token(client: TestClient, username: str, password: str = "senha123") -> str:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": password},
    )
    return response.json()["access_token"]


@pytest.fixture
def token_operador(client, usuario_operador):
    return get_token(client, "operador1")


@pytest.fixture
def token_supervisor(client, usuario_supervisor):
    return get_token(client, "supervisor1")


@pytest.fixture
def token_admin(client, usuario_admin):
    return get_token(client, "admin1")


# ─── Helpers de período ───────────────────────────────────────────────────────

def _periodo_padrao() -> dict:
    return {
        "data_inicio": (date.today() - timedelta(days=30)).isoformat(),
        "data_fim": date.today().isoformat(),
    }


# ─── DataFrames de mock ───────────────────────────────────────────────────────

def _criar_df_vendas() -> pd.DataFrame:
    data_base = date.today() - timedelta(days=10)
    return pd.DataFrame([
        {
            "id_item": 1, "iddocumento": 100, "id_nfe": "NF001",
            "emissao": data_base, "hora": "14:30", "operacao": "V",
            "id_operacao": "VENDA", "cancelado": " ", "total_documento": 100.0,
            "tipo_devolucao": "", "grupo": "Eletronicos", "familia": "Smartphones",
            "codigo": "7891234567890", "produto": "Smartphone XYZ",
            "custo": 700.0, "venda": 999.99, "qtd_item": 1.0,
            "receita_produto": 999.99, "valor_unitario": 999.99,
        },
        {
            "id_item": 2, "iddocumento": 101, "id_nfe": "NF002",
            "emissao": data_base, "hora": "15:00", "operacao": "V",
            "id_operacao": "VENDA", "cancelado": " ", "total_documento": 200.0,
            "tipo_devolucao": "", "grupo": "Eletronicos", "familia": "Tablets",
            "codigo": "7891234567891", "produto": "Tablet ABC",
            "custo": 300.0, "venda": 499.99, "qtd_item": 2.0,
            "receita_produto": 999.98, "valor_unitario": 499.99,
        },
    ])


# ─── Fixture de mock do BI ────────────────────────────────────────────────────

@pytest.fixture
def mock_bi():
    with ExitStack() as stack:
        mock_carregar = stack.enter_context(
            patch("price_checker.api.routes.bi.carregar_fluxo")
        )
        MockRelatorio = stack.enter_context(
            patch("price_checker.api.routes.bi.Relatorio")
        )
        MockMovimento = stack.enter_context(
            patch("price_checker.api.routes.bi.RelatorioMovimento")
        )
        MockDiario = stack.enter_context(
            patch("price_checker.api.routes.bi.RelatorioDiario")
        )
        MockTemporal = stack.enter_context(
            patch("price_checker.api.routes.bi.RelatorioTemporal")
        )
        MockSku = stack.enter_context(
            patch("price_checker.api.routes.bi.RelatorioSku")
        )

        mock_carregar.return_value = _criar_df_vendas()

        inst_rel = MagicMock()
        MockRelatorio.return_value = inst_rel
        inst_rel.kpis.return_value = MagicMock(
            model_dump=MagicMock(return_value={
                "faturamento_bruto": 2000.0,
                "faturamento_liquido": 1500.0,
                "total_trocas": 500.0,
                "qtd_tickets": 2,
                "ticket_medio": 1000.0,
                "itens_por_ticket": 1.5,
            })
        )
        inst_rel.por_dimensao.return_value = [
            {"grupo": "Eletronicos", "familia": "Smartphones", "produto": "Smartphone XYZ", "valor": 999.99},
        ]
        inst_rel.curva_abc.return_value = [
            {
                "grupo": "Eletronicos", "familia": "Smartphones", "produto": "Smartphone XYZ",
                "receita": 999.99, "participacao_pct": 50.0, "participacao_acumulada": 50.0, "curva": "A",
            },
        ]
        inst_rel.ranking.return_value = [
            {"codigo": "7891234567890", "produto": "Smartphone XYZ", "valor": 999.99},
        ]
        inst_rel.trocas_resumo.return_value = MagicMock(
            model_dump=MagicMock(return_value={
                "total_trocas": 500.0,
                "taxa_troca_pct": 25.0,
                "por_produto": [{"codigo": "7891234567890", "produto": "Smartphone XYZ", "receita": 999.99}],
            })
        )

        inst_mov = MagicMock()
        MockMovimento.return_value = inst_mov
        inst_mov.resumo.return_value = MagicMock(
            model_dump=MagicMock(return_value={
                "total": 50.0,
                "por_produto": [{"codigo": "7891234567890", "produto": "Smartphone XYZ", "receita": 50.0}],
            })
        )

        inst_diario = MagicMock()
        MockDiario.return_value = inst_diario
        inst_diario.serie_temporal.return_value = [{"data": "2026-05-01", "valor": 999.99}]
        inst_diario.serie_por_produto.return_value = [{"data": "2026-05-01", "valor": 999.99}]

        inst_temp = MagicMock()
        MockTemporal.return_value = inst_temp
        inst_temp.por_hora.return_value = [{"hora": "14", "valor": 999.99}]
        inst_temp.por_dia_semana.return_value = [{"dia_semana": "Segunda", "valor": 999.99}]

        inst_sku = MagicMock()
        MockSku.return_value = inst_sku
        inst_sku.resumo.return_value = SkuDTO(
            codigo="123456",
            produto="Smartphone XYZ",
            grupo="Eletronicos",
            familia="Smartphones",
            receita_total=999.99,
            qtd_total=1.0,
            qtd_tickets=1,
            ticket_medio=999.99,
            ranking_dias=[PontoDiarioDTO(data="2026-05-01", valor=999.99)],
            distribuicao_hora=[PontoHoraDTO(hora="14", valor=999.99)],
        )

        yield {
            "carregar_fluxo": mock_carregar,
            "relatorio": MockRelatorio,
            "movimento": MockMovimento,
            "diario": MockDiario,
            "temporal": MockTemporal,
            "sku": MockSku,
        }


# ─── Testes ───────────────────────────────────────────────────────────────────

class TestKpis:
    def test_kpis_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/kpis",
            params=_periodo_padrao(),
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "faturamento_bruto" in data
        assert "faturamento_liquido" in data
        assert "total_trocas" in data

    def test_kpis_sem_token(self, client):
        response = client.get("/bi/kpis", params=_periodo_padrao())
        assert response.status_code == 401

    def test_kpis_operador_negado(self, client, token_operador):
        response = client.get(
            "/bi/kpis",
            params=_periodo_padrao(),
            headers={"Authorization": f"Bearer {token_operador}"},
        )
        assert response.status_code == 403

    def test_kpis_admin_permitido(self, client, token_admin, mock_bi):
        response = client.get(
            "/bi/kpis",
            params=_periodo_padrao(),
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200


class TestReceitaPorDimensao:
    def test_receita_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/receita",
            params={**_periodo_padrao(), "dimensao": "produto"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_quantidade_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/quantidade",
            params={**_periodo_padrao(), "dimensao": "grupo"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_dimensao_invalida(self, client, token_supervisor):
        response = client.get(
            "/bi/receita",
            params={**_periodo_padrao(), "dimensao": "invalido"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 422


class TestCurvaABC:
    def test_curva_abc_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/curva-abc",
            params={**_periodo_padrao(), "dimensao": "produto"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "curva" in data[0]
            assert data[0]["curva"] in ["A", "B", "C"]


class TestRanking:
    def test_ranking_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/ranking",
            params={**_periodo_padrao(), "metrica": "receita_produto", "top": 5},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_ranking_top_excedido(self, client, token_supervisor):
        response = client.get(
            "/bi/ranking",
            params={**_periodo_padrao(), "top": 999},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 422

    def test_ranking_top_zero(self, client, token_supervisor):
        response = client.get(
            "/bi/ranking",
            params={**_periodo_padrao(), "top": 0},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 422


class TestTrocas:
    def test_trocas_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/trocas",
            params=_periodo_padrao(),
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_trocas" in data
        assert "taxa_troca_pct" in data
        assert "por_produto" in data
        assert isinstance(data["por_produto"], list)


class TestPerdas:
    def test_perdas_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/perdas",
            params=_periodo_padrao(),
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "por_produto" in data

    def test_perdas_sem_token(self, client):
        response = client.get("/bi/perdas", params=_periodo_padrao())
        assert response.status_code == 401


class TestConsumo:
    def test_consumo_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/consumo",
            params=_periodo_padrao(),
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "por_produto" in data


class TestSerieDiaria:
    def test_diario_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/diario",
            params={**_periodo_padrao(), "metrica": "receita_produto"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "data" in data[0]
            assert "valor" in data[0]

    def test_diario_produto_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/diario/produto",
            params={**_periodo_padrao(), "codigo": "123456", "metrica": "receita_produto"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200

    def test_diario_produto_codigo_invalido(self, client, token_supervisor):
        response = client.get(
            "/bi/diario/produto",
            params={**_periodo_padrao(), "codigo": "abc"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 400


class TestDistribuicaoTemporal:
    def test_por_hora_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/temporal/hora",
            params={**_periodo_padrao(), "metrica": "receita_produto"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "hora" in data[0]
            assert "valor" in data[0]

    def test_por_dia_semana_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/temporal/dia-semana",
            params={**_periodo_padrao(), "metrica": "receita_produto"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "dia_semana" in data[0]
            assert "valor" in data[0]


class TestSku:
    def test_sku_sucesso(self, client, token_supervisor, mock_bi):
        response = client.get(
            "/bi/sku",
            params={**_periodo_padrao(), "codigo": "123456"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["codigo"] == "123456"
        assert "receita_total" in data
        assert "ranking_dias" in data
        assert "distribuicao_hora" in data

    def test_sku_nao_encontrado(self, client, token_supervisor, mock_bi):
        mock_bi["sku"].return_value.resumo.return_value = None
        response = client.get(
            "/bi/sku",
            params={**_periodo_padrao(), "codigo": "123456"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 404

    def test_sku_codigo_invalido(self, client, token_supervisor):
        response = client.get(
            "/bi/sku",
            params={**_periodo_padrao(), "codigo": "abc"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 400

    def test_sku_sem_token(self, client):
        response = client.get(
            "/bi/sku",
            params={**_periodo_padrao(), "codigo": "123456"},
        )
        assert response.status_code == 401


class TestValidacaoPeriodo:
    def test_data_fim_anterior(self, client, token_supervisor):
        hoje = date.today()
        response = client.get(
            "/bi/kpis",
            params={
                "data_inicio": hoje.isoformat(),
                "data_fim": (hoje - timedelta(days=5)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 400
        assert "anterior" in response.json()["detail"].lower()

    def test_range_excedido(self, client, token_supervisor):
        response = client.get(
            "/bi/kpis",
            params={
                "data_inicio": (date.today() - timedelta(days=400)).isoformat(),
                "data_fim": date.today().isoformat(),
            },
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 400
        assert "366" in response.json()["detail"]

    def test_data_inicio_ausente(self, client, token_supervisor):
        response = client.get(
            "/bi/kpis",
            params={"data_fim": date.today().isoformat()},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 422

    def test_data_fim_ausente(self, client, token_supervisor):
        response = client.get(
            "/bi/kpis",
            params={"data_inicio": date.today().isoformat()},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 422

    def test_formato_data_invalido(self, client, token_supervisor):
        response = client.get(
            "/bi/kpis",
            params={"data_inicio": "05/05/2026", "data_fim": "06/05/2026"},
            headers={"Authorization": f"Bearer {token_supervisor}"},
        )
        assert response.status_code == 422