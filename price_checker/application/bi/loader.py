from datetime import date
import pandas as pd
from sqlalchemy import text
from price_checker.application.bi.query_loader import BiQueryLoader
from price_checker.application.bi.db import get_bi_engine

MAX_RANGE_DIAS = 366


def _validar_periodo(data_inicio: date, data_fim: date) -> None:
    if data_fim < data_inicio:
        raise ValueError("data_fim não pode ser anterior a data_inicio")
    if (data_fim - data_inicio).days > MAX_RANGE_DIAS:
        raise ValueError(f"Range máximo permitido é {MAX_RANGE_DIAS} dias")


def carregar_fluxo(data_inicio: date, data_fim: date) -> pd.DataFrame:
    _validar_periodo(data_inicio, data_fim)
    sql = BiQueryLoader.load("fluxo")
    with get_bi_engine().connect() as conn:
        return pd.read_sql(
            text(sql),
            conn,
            params={
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
            },
        )


def carregar_fluxo_lancamento(
    data_lancamento_inicio: date,
    data_lancamento_fim: date,
) -> pd.DataFrame:
    _validar_periodo(data_lancamento_inicio, data_lancamento_fim)
    sql = BiQueryLoader.load("lancamento")
    with get_bi_engine().connect() as conn:
        return pd.read_sql(
            text(sql),
            conn,
            params={
                "data_lancamento_inicio": data_lancamento_inicio.isoformat(),
                "data_lancamento_fim": data_lancamento_fim.isoformat(),
            },
        )