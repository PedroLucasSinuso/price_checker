import pandas as pd
from price_checker.application.bi.domain.vendas import Vendas
from price_checker.application.bi.domain.trocas import Trocas
from price_checker.application.bi.domain.perdas import Perdas
from price_checker.application.bi.domain.consumo import Consumo
from price_checker.application.bi.schema import COLUNAS, Dimensao, Metrica
from price_checker.schemas.bi_schema import (
    KpisDTO,
    ItemDimensaoDTO,
    ItemCurvaAbcDTO,
    ItemRankingDTO,
    ItemMovimentoDTO,
    TrocasDTO,
    MovimentoDTO,
)


class Relatorio:
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

    def kpis(self) -> KpisDTO:
        df_vendas = self.vendas.df
        df_trocas = self.trocas.df
        df_perdas = self.perdas.df
        df_consumo = self.consumo.df

        faturamento_bruto = df_vendas[COLUNAS.receita].sum()
        total_trocas = df_trocas[COLUNAS.receita].abs().sum()
        total_perdas = df_perdas[COLUNAS.receita].abs().sum()
        total_consumo = df_consumo[COLUNAS.receita].abs().sum()
        faturamento_liquido = faturamento_bruto - total_trocas - total_perdas - total_consumo

        tickets = df_vendas.groupby(COLUNAS.id_documento)[COLUNAS.total_documento].first()
        qtd_tickets = len(tickets)
        ticket_medio = float(tickets.mean()) if qtd_tickets > 0 else 0.0
        itens_por_ticket = (
            float(df_vendas.groupby(COLUNAS.id_documento)[COLUNAS.qtd_item].sum().mean())
            if qtd_tickets > 0 else 0.0
        )

        return KpisDTO(
            faturamento_bruto=round(float(faturamento_bruto), 2),
            faturamento_liquido=round(float(faturamento_liquido), 2),
            total_trocas=round(float(total_trocas), 2),
            total_perdas=round(float(total_perdas), 2),
            total_consumo=round(float(total_consumo), 2),
            qtd_tickets=qtd_tickets,
            ticket_medio=round(ticket_medio, 2),
            itens_por_ticket=round(itens_por_ticket, 2),
        )

    def por_dimensao(self, dimensao: Dimensao, metrica: Metrica) -> list[ItemDimensaoDTO]:
        colunas_grupo = dimensao.colunas()
        col_metrica = metrica.value

        df_agrupado = (
            self.vendas.df
            .groupby(colunas_grupo)[col_metrica]
            .sum()
            .reset_index()
            .sort_values(col_metrica, ascending=False)
        )

        return [
            ItemDimensaoDTO(
                grupo=row.get(COLUNAS.grupo, ""),
                familia=row.get(COLUNAS.familia),
                produto=row.get(COLUNAS.produto),
                valor=round(float(row[col_metrica]), 2),
            )
            for row in df_agrupado.to_dict(orient="records")
        ]

    def curva_abc(self, dimensao: Dimensao) -> list[ItemCurvaAbcDTO]:
        colunas_grupo = dimensao.colunas()

        df_agrupado = (
            self.vendas.df
            .groupby(colunas_grupo)[COLUNAS.receita]
            .sum()
            .reset_index()
            .sort_values(COLUNAS.receita, ascending=False)
        )

        total = df_agrupado[COLUNAS.receita].sum()
        df_agrupado["participacao_pct"] = (df_agrupado[COLUNAS.receita] / total * 100).round(2)
        df_agrupado["participacao_acumulada"] = df_agrupado["participacao_pct"].cumsum().round(2)
        df_agrupado["curva"] = df_agrupado["participacao_acumulada"].apply(
            lambda acumulado: "A" if acumulado <= 80 else ("B" if acumulado <= 95 else "C")
        )

        return [
            ItemCurvaAbcDTO(
                grupo=row.get(COLUNAS.grupo, ""),
                familia=row.get(COLUNAS.familia),
                produto=row.get(COLUNAS.produto),
                receita=round(float(row[COLUNAS.receita]), 2),
                participacao_pct=row["participacao_pct"],
                participacao_acumulada=row["participacao_acumulada"],
                curva=row["curva"],
            )
            for row in df_agrupado.to_dict(orient="records")
        ]

    def ranking(self, metrica: Metrica, top: int = 10) -> list[ItemRankingDTO]:
        col_metrica = metrica.value

        df_ranking = (
            self.vendas.df
            .groupby([COLUNAS.codigo, COLUNAS.produto])[col_metrica]
            .sum()
            .reset_index()
            .sort_values(col_metrica, ascending=False)
            .head(top)
        )

        return [
            ItemRankingDTO(
                codigo=str(row[COLUNAS.codigo]),
                produto=str(row[COLUNAS.produto]),
                valor=round(float(row[col_metrica]), 2),
            )
            for row in df_ranking.to_dict(orient="records")
        ]

    def trocas_resumo(self) -> TrocasDTO:
        df_trocas = self.trocas.df
        df_vendas = self.vendas.df

        total_trocas = float(df_trocas[COLUNAS.receita].abs().sum())
        faturamento_bruto = float(df_vendas[COLUNAS.receita].sum())
        taxa_troca = (total_trocas / faturamento_bruto * 100) if faturamento_bruto > 0 else 0.0

        df_por_produto = (
            df_trocas
            .groupby([COLUNAS.codigo, COLUNAS.produto])[COLUNAS.receita]
            .sum()
            .abs()
            .reset_index()
            .sort_values(COLUNAS.receita, ascending=False)
        )

        return TrocasDTO(
            total_trocas=round(total_trocas, 2),
            taxa_troca_pct=round(taxa_troca, 2),
            por_produto=[
                ItemMovimentoDTO(
                    codigo=str(row[COLUNAS.codigo]),
                    produto=str(row[COLUNAS.produto]),
                    receita=round(float(row[COLUNAS.receita]), 2),
                )
                for row in df_por_produto.to_dict(orient="records")
            ],
        )

    def perdas_resumo(self) -> MovimentoDTO:
        df_perdas = self.perdas.df
        total = float(df_perdas[COLUNAS.receita].abs().sum())

        df_por_produto = (
            df_perdas
            .groupby([COLUNAS.codigo, COLUNAS.produto])[COLUNAS.receita]
            .sum()
            .abs()
            .reset_index()
            .sort_values(COLUNAS.receita, ascending=False)
        )

        return MovimentoDTO(
            total=round(total, 2),
            por_produto=[
                ItemMovimentoDTO(
                    codigo=str(row[COLUNAS.codigo]),
                    produto=str(row[COLUNAS.produto]),
                    receita=round(float(row[COLUNAS.receita]), 2),
                )
                for row in df_por_produto.to_dict(orient="records")
            ],
        )

    def consumo_resumo(self) -> MovimentoDTO:
        df_consumo = self.consumo.df
        total = float(df_consumo[COLUNAS.receita].abs().sum())

        df_por_produto = (
            df_consumo
            .groupby([COLUNAS.codigo, COLUNAS.produto])[COLUNAS.receita]
            .sum()
            .abs()
            .reset_index()
            .sort_values(COLUNAS.receita, ascending=False)
        )

        return MovimentoDTO(
            total=round(total, 2),
            por_produto=[
                ItemMovimentoDTO(
                    codigo=str(row[COLUNAS.codigo]),
                    produto=str(row[COLUNAS.produto]),
                    receita=round(float(row[COLUNAS.receita]), 2),
                )
                for row in df_por_produto.to_dict(orient="records")
            ],
        )