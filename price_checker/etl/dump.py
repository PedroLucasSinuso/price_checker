from price_checker.db.session import SqliteSession
from price_checker.etl.extract import ProdutoExtractor
from price_checker.etl.transform import transformar_produtos
from price_checker.etl.load import carregar_produtos, atualizar_cache

def dump_postgres_to_sqlite():
    extractor = ProdutoExtractor()

    # EXTRACT
    data = extractor.extract()

    # TRANSFORM
    produtos = transformar_produtos(
        data["produtos"],
        data["codigos"]
    )

    # LOAD
    with SqliteSession() as session:
        try:
            with session.begin():
                carregar_produtos(session, produtos)
                atualizar_cache(session)

        except Exception as e:
            with session.begin():
                atualizar_cache(session, status="erro", erro=str(e))
                
            raise RuntimeError(f"Erro ao carregar dados no SQLite: {e}")
            