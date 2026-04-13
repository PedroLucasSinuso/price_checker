from collections import defaultdict
from price_checker.models.produto import Produto, ProdutoCodigo

def transformar_produtos(produtos_rows, codigos_rows):
    codigos_por_produto = defaultdict(set)

    for row in codigos_rows:
        codigo = row["codigo"]
        codigo_chamada = row["codigo_chamada"]

        if not codigo:
            continue

        codigos_por_produto[codigo_chamada].add(codigo)

    produtos = []

    for row in produtos_rows:
        codigo_chamada = row["codigo_chamada"]
        codigos = codigos_por_produto.get(codigo_chamada, set())

        produto = Produto(
            codigo_chamada=codigo_chamada,
            nome=row["nome"],
            grupo=row["grupo"],
            familia=row["familia"],
            preco_custo=row["preco_custo"],
            preco_venda=row["preco_venda"],
            estoque=row["estoque"],
            codigos=[ProdutoCodigo(codigo=c) for c in codigos],
        )

        produtos.append(produto)

    return produtos