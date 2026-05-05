from price_checker.application.bi.schema import COLUNAS, CodigoOperacao
from price_checker.application.bi.domain.fluxo import Fluxo


class Perdas(Fluxo):
    def __init__(self, df):
        super().__init__(df)
        self.df = self.df[
            (self.df[COLUNAS.cancelado] != "*") &
            (self.df[COLUNAS.operacao] == "S") &
            (self.df[COLUNAS.id_operacao] == CodigoOperacao.PERDA) &
            (self.df[COLUNAS.id_nfe].notna())
        ].reset_index(drop=True)