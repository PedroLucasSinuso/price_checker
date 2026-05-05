from price_checker.application.bi.schema import COLUNAS
from price_checker.application.bi.domain.fluxo import Fluxo


class Trocas(Fluxo):
    def __init__(self, df):
        super().__init__(df)
        self.df = self.df[
            (self.df[COLUNAS.cancelado] != "*") &
            (self.df[COLUNAS.operacao] == "E") &
            (self.df[COLUNAS.devolucao].isin(["T", "D"]))
        ].reset_index(drop=True)