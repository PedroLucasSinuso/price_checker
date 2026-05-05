import pandas as pd
from price_checker.application.bi.schema import COLUNAS
from price_checker.application.bi.domain.fluxo import Fluxo


class Vendas(Fluxo):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.df = self.df[
            (self.df[COLUNAS.cancelado] != "*") &
            (self.df[COLUNAS.operacao] == "V")
        ].reset_index(drop=True)