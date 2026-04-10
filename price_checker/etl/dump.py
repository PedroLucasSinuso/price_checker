from price_checker.etl.query_loader import QueryLoader
from price_checker.etl.loader import PostgresLoader
from price_checker.repositories.produto_repository import ProdutoRepository
from price_checker.models.produto import Produto

def row_to_dict(row: dict) -> dict:
    return {
        "id": row["id_detalhe"],
        "codigo_chamada": row["codigo_chamada"],
        "nome": row["nome"],
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

    # Resolve a incompatibilidade entre os nomes das colunas do Postgres e os atributos do modelo Produto
    # Dívida técnica a ser resolvida posteriormente: ETL acoplado ao modelo de dados
    #todo: refatorar para desacoplar o ETL do modelo de dados
    produtos = [Produto(**row_to_dict(row)) for row in rows] 


    repo = ProdutoRepository()
    repo.replace_all(produtos)

