from datetime import date
from price_checker.application.bi.loader import carregar_fluxo, carregar_fluxo_lancamento
from price_checker.application.bi.domain.vendas import Vendas
from price_checker.application.bi.domain.trocas import Trocas
from price_checker.application.bi.domain.perdas import Perdas
from price_checker.application.bi.domain.consumo import Consumo


class DominioBI:
    def __init__(
        self,
        vendas: Vendas,
        trocas: Trocas,
        perdas: Perdas,
        consumo: Consumo,
    ):
        self.vendas = vendas
        self.trocas = trocas
        self.perdas = perdas
        self.consumo = consumo


def criar_dominio(
    data_inicio: date,
    data_fim: date,
    data_lancamento_inicio: date | None = None,
    data_lancamento_fim: date | None = None,
) -> DominioBI:
    df = carregar_fluxo(data_inicio, data_fim)

    vendas = Vendas(df)
    trocas = Trocas(df)

    if data_lancamento_inicio and data_lancamento_fim:
        df_lanc = carregar_fluxo_lancamento(data_lancamento_inicio, data_lancamento_fim)
        perdas = Perdas(df_lanc)
        consumo = Consumo(df_lanc)
    else:
        perdas = Perdas(df)
        consumo = Consumo(df)

    return DominioBI(vendas, trocas, perdas, consumo)