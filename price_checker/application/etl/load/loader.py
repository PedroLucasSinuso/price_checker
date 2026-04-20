from datetime import datetime, timezone
from sqlalchemy import delete

from price_checker.application.etl.dto import ProdutoDTO
from price_checker.domain.models.produto import Produto, ProdutoCodigo
from price_checker.domain.models.cache_status import CacheStatus


def _to_orm(produto_dto: ProdutoDTO):
    return Produto(
        codigo_chamada=produto_dto.codigo_chamada,
        nome=produto_dto.nome,
        grupo=produto_dto.grupo,
        familia=produto_dto.familia,
        preco_custo=produto_dto.preco_custo,
        preco_venda=produto_dto.preco_venda,
        estoque=produto_dto.estoque,
        codigos=[
            ProdutoCodigo(
                codigo=c.codigo,
                codigo_chamada=c.codigo_chamada
            )
            for c in produto_dto.codigos
        ],
    )


def carregar_produtos(session, produtos_dto):
    session.execute(delete(ProdutoCodigo))
    session.execute(delete(Produto))

    produtos_orm = [_to_orm(p) for p in produtos_dto]

    session.add_all(produtos_orm)


def atualizar_cache(session, status="sucesso", erro=None):
    session.add(CacheStatus(
        last_updated=datetime.now(timezone.utc),
        status=status,
        erro=erro
    ))