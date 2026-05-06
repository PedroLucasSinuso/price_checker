from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from price_checker.api.deps import require_supervisor
from price_checker.domain.models.usuario import Usuario
from price_checker.application.bi.factory import criar_dominio
from price_checker.application.bi.loader import carregar_fluxo
from price_checker.application.bi.domain.perdas import Perdas
from price_checker.application.bi.domain.consumo import Consumo
from price_checker.application.bi.reporting.relatorio import Relatorio
from price_checker.application.bi.reporting.relatorio_diario import RelatorioDiario
from price_checker.application.bi.reporting.relatorio_temporal import RelatorioTemporal
from price_checker.application.bi.reporting.relatorio_sku import RelatorioSku
from price_checker.application.bi.reporting.relatorio_movimento import RelatorioMovimento
from price_checker.application.bi.schema import Dimensao, Metrica
from price_checker.schemas.bi_schema import (
    KpisDTO,
    ItemDimensaoDTO,
    ItemCurvaAbcDTO,
    ItemRankingDTO,
    TrocasDTO,
    MovimentoDTO,
    PontoDiarioDTO,
    PontoHoraDTO,
    PontoDiaSemanDTO,
    SkuDTO,
)

router = APIRouter(prefix="/bi", tags=["BI"])


def _periodo(data_inicio: date, data_fim: date) -> tuple[date, date]:
    if data_fim < data_inicio:
        raise HTTPException(status_code=400, detail="data_fim não pode ser anterior a data_inicio")
    if (data_fim - data_inicio).days > 366:
        raise HTTPException(status_code=400, detail="Range máximo permitido é 366 dias")
    return data_inicio, data_fim

# ── KPIs ────────────────────────────────────────────────────────────

@router.get("/kpis", response_model=KpisDTO)
def kpis(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Calcula e retorna os KPIs de vendas e trocas para o período informado."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    dominio = criar_dominio(data_inicio, data_fim)
    return Relatorio(dominio.vendas, dominio.trocas).kpis()


# ── Receita e Quantidade por Dimensão ───────────────────────────────

@router.get("/receita", response_model=list[ItemDimensaoDTO])
def receita_por_dimensao(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    dimensao: Dimensao = Query(Dimensao.PRODUTO),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna a receita agregada por dimensão (produto, grupo, família) no período."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    dominio = criar_dominio(data_inicio, data_fim)
    return Relatorio(dominio.vendas, dominio.trocas).por_dimensao(dimensao, Metrica.RECEITA)


@router.get("/quantidade", response_model=list[ItemDimensaoDTO])
def quantidade_por_dimensao(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    dimensao: Dimensao = Query(Dimensao.PRODUTO),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna a quantidade vendida agregada por dimensão no período."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    dominio = criar_dominio(data_inicio, data_fim)
    return Relatorio(dominio.vendas, dominio.trocas).por_dimensao(dimensao, Metrica.QUANTIDADE)


# ── Curva ABC ─────────────────────────────────────────────────────────

@router.get("/curva-abc", response_model=list[ItemCurvaAbcDTO])
def curva_abc(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    dimensao: Dimensao = Query(Dimensao.PRODUTO),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Gera a curva ABC de produtos baseada na receita no período informado."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    dominio = criar_dominio(data_inicio, data_fim)
    return Relatorio(dominio.vendas, dominio.trocas).curva_abc(dimensao)


# ── Ranking ──────────────────────────────────────────────────────────

@router.get("/ranking", response_model=list[ItemRankingDTO])
def ranking(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    metrica: Metrica = Query(Metrica.RECEITA),
    top: int = Query(default=10, ge=1, le=100),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna o ranking de produtos por métrica (receita ou quantidade) no período."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    dominio = criar_dominio(data_inicio, data_fim)
    return Relatorio(dominio.vendas, dominio.trocas).ranking(metrica, top)


# ── Trocas ───────────────────────────────────────────────────────────

@router.get("/trocas", response_model=TrocasDTO)
def trocas(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna o resumo de trocas (devoluções) com métricas e breakdown por produto."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    dominio = criar_dominio(data_inicio, data_fim)
    return Relatorio(dominio.vendas, dominio.trocas).trocas_resumo()


# ── Perdas ───────────────────────────────────────────────────────────

@router.get("/perdas", response_model=MovimentoDTO)
def perdas(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna o resumo de perdas (quebras de estoque) no período informado."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    df = carregar_fluxo(data_inicio, data_fim)
    return RelatorioMovimento(Perdas(df)).resumo()


# ── Consumo ─────────────────────────────────────────────────────────

@router.get("/consumo", response_model=MovimentoDTO)
def consumo(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna o resumo de consumo interno (uso próprio) no período informado."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    df = carregar_fluxo(data_inicio, data_fim)
    return RelatorioMovimento(Consumo(df)).resumo()


# ── Série Temporal Diária ─────────────────────────────────────────

@router.get("/diario", response_model=list[PontoDiarioDTO])
def serie_diaria(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    metrica: Metrica = Query(Metrica.RECEITA),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna a série temporal diária de vendas para o período informado."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    dominio = criar_dominio(data_inicio, data_fim)
    return RelatorioDiario(dominio.vendas).serie_temporal(metrica)


@router.get("/diario/produto", response_model=list[PontoDiarioDTO])
def serie_diaria_produto(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    codigo: str = Query(...),
    metrica: Metrica = Query(Metrica.RECEITA),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna a série temporal diária de um produto específico no período."""
    from price_checker.domain.value_objects.codigo import Codigo
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    try:
        codigo_valido = Codigo(codigo).valor
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail=f"Código inválido: {codigo!r}")
    dominio = criar_dominio(data_inicio, data_fim)
    return RelatorioDiario(dominio.vendas).serie_por_produto(codigo_valido, metrica)


# ── Distribuição Temporal ─────────────────────────────────────────

@router.get("/temporal/hora", response_model=list[PontoHoraDTO])
def distribuicao_hora(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    metrica: Metrica = Query(Metrica.RECEITA),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna a distribuição de vendas por hora do dia no período informado."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    dominio = criar_dominio(data_inicio, data_fim)
    return RelatorioTemporal(dominio.vendas).por_hora(metrica)


@router.get("/temporal/dia-semana", response_model=list[PontoDiaSemanDTO])
def distribuicao_dia_semana(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    metrica: Metrica = Query(Metrica.RECEITA),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna a distribuição de vendas por dia da semana no período informado."""
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    dominio = criar_dominio(data_inicio, data_fim)
    return RelatorioTemporal(dominio.vendas).por_dia_semana(metrica)


# ── SKU ─────────────────────────────────────────────────────────────

@router.get("/sku", response_model=SkuDTO)
def sku(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    codigo: str = Query(...),
    _usuario: Usuario = Depends(require_supervisor),
):
    """Retorna o resumo completo de um SKU (produto) no período informado."""
    from price_checker.domain.value_objects.codigo import Codigo
    data_inicio, data_fim = _periodo(data_inicio, data_fim)
    try:
        codigo_valido = Codigo(codigo).valor
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail=f"Código inválido: {codigo!r}")
    dominio = criar_dominio(data_inicio, data_fim)
    resultado = RelatorioSku(dominio.vendas, codigo_valido).resumo()
    if resultado is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado no período informado")
    return resultado


# ── Exportação Excel (TODO: implementar futuramente) ─────────────
# @router.get("/exportar/excel")
# def exportar_excel(
#     data_inicio: date = Query(...),
#     data_fim: date = Query(...),
#     relatorio: str = Query(...),
#     dimensao: Dimensao = Query(Dimensao.PRODUTO),
#     metrica: Metrica = Query(Metrica.RECEITA),
#     top: int = Query(default=10, ge=1, le=100),
#     codigo: str = Query(default=None),
#     _usuario: Usuario = Depends(require_supervisor),
# ):
#     from price_checker.application.bi.reporting.exportador import ExportadorExcel
#     from price_checker.domain.value_objects.codigo import Codigo
#     import io
#
#     data_inicio, data_fim = _periodo(data_inicio, data_fim)
#
#     opcoes_validas = {
#         "kpis", "receita", "quantidade",
#         "curva-abc", "ranking", "trocas",
#         "perdas", "consumo", "diario", "sku"
#     }
#     if relatorio not in opcoes_validas:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Relatório inválido. Opções: {sorted(opcoes_validas)}"
#         )
#     
#     dominio = criar_dominio(data_inicio, data_fim)
#     rel = Relatorio(dominio.vendas, dominio.trocas)
#     exportador = ExportadorExcel()
#     dados: dict = {}
#
#     if relatorio == "kpis":
#         dados["KPIs"] = [rel.kpis().model_dump()]
#     elif relatorio == "receita":
#         dados["Receita"] = [i.model_dump() for i in rel.por_dimensao(dimensao, Metrica.RECEITA)]
#     elif relatorio == "quantidade":
#         dados["Quantidade"] = [i.model_dump() for i in rel.por_dimensao(dimensao, Metrica.QUANTIDADE)]
#     elif relatorio == "curva-abc":
#         dados["Curva ABC"] = [i.model_dump() for i in rel.curva_abc(dimensao)]
#     elif relatorio == "ranking":
#         dados["Ranking"] = [i.model_dump() for i in rel.ranking(metrica, top)]
#     elif relatorio == "trocas":
#         trocas_dto = rel.trocas_resumo()
#         dados["Trocas Resumo"] = [{"total_trocas": trocas_dto.total_trocas, "taxa_troca_pct": trocas_dto.taxa_troca_pct}]
#         dados["Trocas por Produto"] = [i.model_dump() for i in trocas_dto.por_produto]
#     elif relatorio == "perdas":
#         df = carregar_fluxo(data_inicio, data_fim)
#         perdas_dto = RelatorioMovimento(Perdas(df)).resumo()
#         dados["Perdas Resumo"] = [{"total": perdas_dto.total}]
#         dados["Perdas por Produto"] = [i.model_dump() for i in perdas_dto.por_produto]
#     elif relatorio == "consumo":
#         df = carregar_fluxo(data_inicio, data_fim)
#         consumo_dto = RelatorioMovimento(Consumo(df)).resumo()
#         dados["Consumo Resumo"] = [{"total": consumo_dto.total}]
#         dados["Consumo por Produto"] = [i.model_dump() for i in consumo_dto.por_produto]
#     elif relatorio == "diario":
#         dados["Série Diária"] = [i.model_dump() for i in RelatorioDiario(dominio.vendas).serie_temporal(metrica)]
#     elif relatorio == "sku":
#         if not codigo:
#             raise HTTPException(status_code=400, detail="Parâmetro 'codigo' obrigatório para relatório SKU")
#         try:
#             codigo_valido = Codigo(codigo).valor
#         except (ValueError, TypeError):
#             raise HTTPException(status_code=400, detail=f"Código inválido: {codigo!r}")
#         resultado = RelatorioSku(dominio.vendas, codigo_valido).resumo()
#         if resultado is None:
#             raise HTTPException(status_code=404, detail="Produto não encontrado no período informado")
#         dados["SKU"] = [resultado.model_dump(exclude={"ranking_dias", "distribuicao_hora"})]
#         dados["Ranking Dias"] = [i.model_dump() for i in resultado.ranking_dias]
#         dados["Distribuição Hora"] = [i.model_dump() for i in resultado.distribuicao_hora]
#
#     conteudo = exportador.exportar(dados)
#     nome_arquivo = f"bi_{relatorio}_{data_inicio}_{data_fim}.xlsx"
#
#     return StreamingResponse(
#         io.BytesIO(conteudo),
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"},
#     )
