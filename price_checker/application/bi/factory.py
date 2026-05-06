from datetime import date
from price_checker.application.bi.loader import carregar_fluxo
from price_checker.application.bi.domain.vendas import Vendas
from price_checker.application.bi.domain.trocas import Trocas


class DominioBI:
    """Contém os domínios de vendas e trocas para o período informado."""
    def __init__(self, vendas: Vendas, trocas: Trocas):
        """Inicializa com os domínios de vendas e trocas."""
        self.vendas = vendas
        self.trocas = trocas


def criar_dominio(data_inicio: date, data_fim: date) -> DominioBI:
    """Cria o domínio BI carregando os dados do PostgreSQL para o período."""
    df = carregar_fluxo(data_inicio, data_fim)
    return DominioBI(
        vendas=Vendas(df),
        trocas=Trocas(df),
    )