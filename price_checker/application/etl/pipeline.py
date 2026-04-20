from price_checker.infrastructure.db.session import SqliteSession
from price_checker.application.etl.extract.extractor import ProdutoExtractor
from price_checker.application.etl.transform.transformer import transformar_produtos
from price_checker.application.etl.load.loader import carregar_produtos, atualizar_cache
import logging

logger = logging.getLogger(__name__)


def run_etl():
    logger.info("Iniciando ETL")

    extractor =ProdutoExtractor()

    data = extractor.extract()

    logger.info("Extract concluído | produtos=%s codigos=%s", len(data.produtos), len(data.codigos))

    produtos = transformar_produtos(
        data.produtos,
        data.codigos
    )

    logger.info("Transform concluído | total=%s", len(produtos))

    with SqliteSession() as session:
        try:
            with session.begin():
                carregar_produtos(session, produtos)
                atualizar_cache(session)

            logger.info("Load concluído com sucesso")

        except Exception as e:
            logger.exception("Erro no ETL | Erro: %s", e)

            session.rollback()
            atualizar_cache(session, status="erro", erro=str(e))
            session.commit()

            raise RuntimeError(f"Erro ao carregar dados no SQLite: {e}")