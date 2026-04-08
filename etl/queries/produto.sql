-- Estração de códigos e produtos do servidor principal 
-- e armazenamento em um banco de dados local SQLite

SELECT  c.iddetalhe         as id_detalhe,
        d.stdetalheativo    as ativo,
        d.cdprincipal       as codigo_chamada,
        g.nmgrupo           as grupo,
        f.dsfamilia         as familia,
        d.dsdetalhe         as sku,
        d.vlprecovenda      as preco_venda,
        d.vlprecocusto      as preco_custo,
        c.dscodigo          as codigo,
        e.qtestoque         as estoque
FROM wshop.codigos c
LEFT JOIN wshop.detalhe d   ON c.iddetalhe = d.iddetalhe
LEFT JOIN wshop.familia f   ON d.idfamilia = f.idfamilia
LEFT JOIN wshop.produto p   ON d.idproduto = p.idproduto
LEFT JOIN wshop.grupo   g   ON p.idgrupo = g.idgrupo
LEFT JOIN wshop.estoque e   ON d.iddetalhe = e.iddetalhe
WHERE e.dtreferencia = (
    SELECT MAX(e2.dtreferencia)
    FROM wshop.estoque e2
    WHERE e2.iddetalhe = e.iddetalhe
);
