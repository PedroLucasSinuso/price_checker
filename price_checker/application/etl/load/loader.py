from datetime import datetime, timezone
from sqlalchemy import delete, func
from sqlalchemy.orm import Session

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


def carregar_produtos(session: Session, produtos_dto: list[ProdutoDTO]) -> tuple[int, int]:
    session.execute(delete(ProdutoCodigo))
    session.execute(delete(Produto))

    produtos_orm = [_to_orm(p) for p in produtos_dto]

    session.add_all(produtos_orm)

    produtos_count = len(produtos_orm)
    codigos_count = sum(len(p.codigos) for p in produtos_orm)

    return produtos_count, codigos_count


def atualizar_cache(session: Session, status: str = "sucesso", erro: str | None = None):
    session.add(CacheStatus(
        last_updated=datetime.now(timezone.utc),
        status=status,
        erro=erro
    ))