from sqlalchemy import delete

from price_checker.models.produto import Produto, ProdutoCodigo
from price_checker.models.cache_status import CacheStatus
from datetime import datetime, timezone

def carregar_produtos(session, produtos):
    session.execute(delete(ProdutoCodigo))
    session.execute(delete(Produto))

    session.add_all(produtos)

def atualizar_cache(session, status="sucesso", erro=None):
    session.add(CacheStatus(
        last_updated=datetime.now(timezone.utc),
        status=status,
        erro=erro
    ))