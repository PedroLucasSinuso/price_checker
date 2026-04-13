from price_checker.models.produto import Produto, ProdutoCodigo
from price_checker.models.cache_status import CacheStatus
from datetime import datetime

def carregar_produtos(session, produtos):
    session.query(ProdutoCodigo).delete()
    session.query(Produto).delete()

    session.add_all(produtos)

def atualizar_cache(session):
    session.query(CacheStatus).delete()
    session.add(CacheStatus(last_updated=datetime.now()))