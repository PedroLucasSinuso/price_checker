# price_checker

API REST para consulta de preços e métricas de produtos, construída com **FastAPI** e **SQLite** como cache local de um banco **PostgreSQL** de origem.

> Projeto de portfólio desenvolvido como case técnico de backend/dados.

---

## Visão geral

O `price_checker` resolve um problema real de varejo: operadores precisam consultar preço, estoque, markup e margem de produtos rapidamente — via código de barras (EAN) ou código interno (PLU) — sem depender de conectividade contínua com o banco de dados principal.

A solução usa um pipeline ETL que extrai dados do PostgreSQL, transforma e carrega num cache SQLite local. A API FastAPI serve as consultas a partir desse cache.

```
PostgreSQL (fonte)
      │
      ▼
  ETL Pipeline
  ┌─────────────────────────────┐
  │  Extract → Transform → Load │
  └─────────────────────────────┘
      │
      ▼
  SQLite (cache local)
      │
      ▼
  FastAPI (API REST)
      │
      ▼
  Cliente (web / mobile)
```

---

## Stack

| Camada | Tecnologia |
|---|---|
| API | FastAPI |
| ORM | SQLAlchemy 2.0 (Mapped columns, relacionamentos) |
| Cache | SQLite |
| Fonte de dados | PostgreSQL |
| Validação | Pydantic v2 |
| Configuração | pydantic-settings + `.env` |
| Testes | pytest |

---

## Arquitetura

O projeto segue arquitetura em camadas com separação clara de responsabilidades:

```
price_checker/
├── api/
│   ├── deps.py                 # Injeção de dependência (sessão, repositório)
│   └── routes/
│       ├── produto.py          # Endpoints de produto
│       └── cache_status.py   # Endpoint de status do cache
├── application/
│   ├── services/
│   │   └── produto_service.py  # Regras de negócio
│   └── etl/
│       ├── extract/
│       │   └── extractor.py   # ProdutoExtractor — lê do Postgres
│       ├── transform/
│       │   └── transformer.py # Mapeamento de linhas para DTOs
│       ├── load/
│       │   └── loader.py     # Persistência no SQLite + atualização de cache
│       ├── pipeline.py       # Orquestrador ETL (Extract → Transform → Load)
│       ├── dto.py           # Data Transfer Objects
│       └── queries/
│           ├── produto.sql
│           └── codigo.sql
├── core/
│   ├── config.py             # Settings via pydantic-settings
│   └── logging_config.py     # Configuração de logging
├── domain/
│   ├── models/
│   │   ├── produto.py        # Produto, ProdutoCodigo (SQLAlchemy ORM)
│   │   └── cache_status.py  # CacheStatus (registro de última atualização)
│   └── value_objects/
│       └── codigo.py       # Classe Codigo: validação EAN8/12/13 e PLU6
├── infrastructure/
│   ├── db/
│   │   ├── database.py      # Base declarativa SQLAlchemy
│   │   ├── session.py     # Engines e sessions (Postgres + SQLite)
│   │   └── bootstrap.py   # Criação das tabelas (init_db)
│   ├── repositories/
│   │   └── produto_repository.py  # Acesso ao SQLite
│   └── postgres/
│       └── loader.py      # Executa queries SQL no Postgres
└── schemas/
    └── produto_schema.py  # ProdutoResponse (Pydantic)
```

**Fluxo de uma requisição:**

```
Request HTTP
    └─► Route (produto.py)
            ���─► ProdutoService
                    └─► Codigo (valida e normaliza o código)
                    └─► ProdutoRepository
                            └─► SQLite (cache)
                    └─► ProdutoResponse (Pydantic)
            └─► Response HTTP
```

---

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/produtos/` | Lista produtos com paginação |
| `GET` | `/produtos/{codigo}` | Busca produto por EAN ou PLU |
| `GET` | `/status/` | Retorna data/hora da última atualização do cache |

### Parâmetros de listagem

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `limit` | int | 50 | Máximo de resultados (clamped entre 1–100) |
| `offset` | int | 0 | Paginação por offset |

### Exemplo de resposta — `GET /produtos/{codigo}`

```json
{
  "codigo_chamada": "000123",
  "nome": "Smartphone XYZ",
  "grupo": "Eletrônicos",
  "familia": "Smartphones",
  "preco_venda": 1599.90,
  "preco_custo": 980.00,
  "estoque": 42.0,
  "markup": 0.6326,
  "margem": 0.3876,
  "codigo_buscado": "7891234567890"
}
```

### Códigos de status

| Status | Situação |
|---|---|
| `200` | Produto encontrado |
| `400` | Código inválido (formato não reconhecido) |
| `404` | Produto não encontrado no cache |

---

## Validação de códigos

A classe `Codigo` em `domain/value_objects/codigo.py` valida e normaliza automaticamente os formatos suportados:

| Formato | Tamanho | Validação |
|---|---|---|
| EAN-13 | 13 dígitos | Checksum módulo 10 |
| EAN-12 | 12 dígitos | Checksum módulo 10 |
| EAN-8 | 8 dígitos | Checksum módulo 10 |
| PLU-6 | 6 dígitos | Apenas numérico |

Espaços e hífens são removidos automaticamente na normalização. O campo `codigo_buscado` na resposta reflete o código após normalização.

---

## ETL

O pipeline ETL sincroniza dados do PostgreSQL para o SQLite local. Por padrão é executado manualmente; a configuração `cache_refresh_interval` (em segundos) está disponível para agendamento externo.

```bash
python -m price_checker.etl.run_etl
```

**Fases:**

1. **Extract** — `ProdutoExtractor` executa as queries `produto.sql` e `codigo.sql` no Postgres
2. **Transform** — agrupa códigos de barras por produto, converte para DTOs
3. **Load** — trunca e reinsere produtos e códigos no SQLite, registra timestamp em `CacheStatus`

> O ETL requer `POSTGRES_URL` configurado no `.env`. Sem ele, o `PostgresLoader` levanta `RuntimeError` com mensagem clara.

---

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
POSTGRES_URL=postgresql://usuario:senha@host:5432/banco
SQLITE_URL=sqlite:///./price_checker.db
CACHE_REFRESH_INTERVAL=3600
```

| Variável | Obrigatória | Descrição |
|---|---|---|
| `POSTGRES_URL` | Sim (para ETL) | Connection string do banco de origem |
| `SQLITE_URL` | Sim | Caminho do banco SQLite local |
| `CACHE_REFRESH_INTERVAL` | Não | Intervalo de refresh em segundos (padrão: 3600) |

---

## Instalação e execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar ETL (para популяция inicial do cache)
python -m price_checker.etl.run_etl

# Subir a API
uvicorn price_checker.main:app --reload
```

A documentação interativa estará disponível em `http://localhost:8000/docs`.

---

## Testes

```bash
pytest
```

A suíte cobre: validação de códigos (EAN/PLU), métricas do model (markup, margem, edge cases), serialização do schema Pydantic, regras de negócio do service (mock de repositório, clamp de paginação, código inválido) e transformação ETL.

```
tests/
├── etl/
│   └── test_transform.py
├── models/
│   └── test_produto_model.py
├── schemas/
│   └── test_produto_schema.py
├── services/
│   └── test_produto_service.py
└── utils/
    └── test_codigo.py
```

---

## Decisões de design

**SQLite como cache** — desacopla a API da disponibilidade do banco de origem. Consultas locais são rápidas e não geram carga no Postgres operacional.

**Separação Model / Schema** — `Produto` (SQLAlchemy) representa a entidade persistida; `ProdutoResponse` (Pydantic) define o contrato da API. Métricas computadas (`markup`, `margem`) ficam como `@property` no model e são expostas pelo schema via `from_attributes`.

**Arquitetura em camadas** — o projeto segue a estrutura domain/application/infrastructure, isolando regras de negócio (domain, application) de detalhes técnicos (infrastructure).

**Injeção de dependência** — a sessão do banco é gerenciada pelo `Depends` do FastAPI (`deps.py`), mantendo o repositório desacoplado do ciclo de vida da request.

**Transform puro** — a camada de transformação ETL recebe apenas DTOs (não dicts), garantindo tipagem consistente e testes mais confiáveis.

**Classe `Codigo`** — encapsula validação, normalização e detecção de tipo de código de barras como Value Object imutável, isolando essa lógica do service.

---

## Melhorias planejadas

- [ ] Testes de integração da API com `TestClient` e banco SQLite em memória
- [ ] Endpoint de busca por nome (`GET /produtos/busca?q=`)
- [ ] Filtros por grupo e família em `GET /produtos/`
- [ ] Endpoint para disparo manual do ETL via HTTP (`POST /etl/trigger`)
- [ ] Frontend mobile (PWA) com leitura de código de barras pela câmera
- [ ] Agendamento automático do ETL

---

## Autor

Desenvolvido como projeto de portfólio — backend Python / análise de dados.