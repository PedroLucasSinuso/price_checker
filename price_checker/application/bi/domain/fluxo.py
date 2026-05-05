import pandas as pd
from price_checker.application.bi.schema import COLUNAS


class Fluxo:
    def __init__(self, df: pd.DataFrame):
        self.df = self._padronizar(df.copy())

    def _padronizar(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.str.strip().str.lower()
        df[COLUNAS.receita] = pd.to_numeric(df[COLUNAS.receita], errors="coerce").fillna(0.0)
        df[COLUNAS.qtd_item] = pd.to_numeric(df[COLUNAS.qtd_item], errors="coerce").fillna(0.0)
        return df