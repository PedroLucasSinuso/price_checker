from price_checker.etl.query_loader import QueryLoader
from price_checker.etl.loader import PostgresLoader
from price_checker.db.session import SqliteSession
from price_checker.models.produto import Produto, ProdutoCodigo


def map_produto(row: dict) -> Produto:
    return Produto(
        codigo_chamada=row["codigo_chamada"],
        nome=row["nome"],
        grupo=row["grupo"],
        familia=row["familia"],
        preco_venda=row["preco_venda"],
        preco_custo=row["preco_custo"],
        estoque=row["estoque"],
    )


def map_codigo(row: dict) -> ProdutoCodigo:
    return ProdutoCodigo(
        codigo=row["codigo"],
        codigo_chamada=row["codigo_chamada"],
    )


def dump_postgres_to_sqlite():
    produto_query = QueryLoader.load("produto")
    codigo_query = QueryLoader.load("codigo")

    produto_loader = PostgresLoader(produto_query)
    codigo_loader = PostgresLoader(codigo_query)

    produtos_rows = produto_loader.load()
    codigos_rows = codigo_loader.load()

    produtos = [map_produto(row) for row in produtos_rows]

    codigos_validos = []
    produtos_ids = {p.codigo_chamada for p in produtos}

    for row in codigos_rows:
        if row["codigo_chamada"] in produtos_ids:
            codigos_validos.append(map_codigo(row))

    with SqliteSession() as session:
        session.query(ProdutoCodigo).delete()
        session.query(Produto).delete()

        session.add_all(produtos)
        session.flush()

        session.add_all(codigos_validos)

        session.commit()