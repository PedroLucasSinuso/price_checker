from .query_loader import QueryLoader
from .loader import PostgresLoader
from ..repositories.produto import ProdutoRepository


def row_to_dict(row: dict) -> dict:
    return {
        "id": row["id_detalhe"],
        "codigo_chamada": row["codigo_chamada"],
        "nome": row["sku"],
        "grupo": row["grupo"],
        "familia": row["familia"],
        "preco_venda": row["preco_venda"],
        "preco_custo": row["preco_custo"],
        "estoque": row["estoque"],
        "codigo": row["codigo"],
    }


def dump_postgres_to_sqlite():
    query = QueryLoader.load("produto")

    loader = PostgresLoader(query)
    rows = loader.load()

    produtos = [row_to_dict(row) for row in rows]

    repo = ProdutoRepository()
    repo.replace_all(produtos)
