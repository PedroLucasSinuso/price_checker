from price_checker.etl.dto import ExtractResult, ProdutoRow, CodigoRow
from price_checker.etl.query_loader import QueryLoader
from price_checker.etl.postgres_loader import PostgresLoader

class ProdutoExtractor:
    def __init__(self):
        self.produto_loader = PostgresLoader(QueryLoader.load("produto"))
        self.codigo_loader = PostgresLoader(QueryLoader.load("codigo"))

    def extract(self) -> ExtractResult:
        produtos_raw = self.produto_loader.load()
        codigos_raw = self.codigo_loader.load()

        produtos = [
            ProdutoRow(**row)
            for row in produtos_raw
        ]

        codigos = [
            CodigoRow(**row)
            for row in codigos_raw
            if row["codigo"]  
        ]

        return ExtractResult(
            produtos=produtos,
            codigos=codigos,
        )