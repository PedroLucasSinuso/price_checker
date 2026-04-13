from price_checker.etl.query_loader import QueryLoader
from price_checker.etl.postgres_loader import PostgresLoader

class ProdutoExtractor:
    def __init__(self):
        self.produto_loader = PostgresLoader(QueryLoader.load("produto"))
        self.codigo_loader = PostgresLoader(QueryLoader.load("codigo"))

    def extract(self):
        return {
            "produtos": self.produto_loader.load(),
            "codigos": self.codigo_loader.load()
        }