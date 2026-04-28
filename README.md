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
| Autenticação | JWT (python-jose) + bcrypt |

---

## Arquitetura

O projeto segue arquitetura em camadas com separação clara de responsabilidades:

```
price_checker/
├── api/
│   ├── deps.py            # Injeção de dependência
│   └── routes/
│       ├── produto.py      # Endpoints de produto
│       ├── auth.py         # Endpoints de autenticação
│       ├── admin.py        # Endpoints administrativos
│       └── cache_status.py
├── application/
│   ├── services/         # Regras de negócio
│   └── etl/
│       ├── extract/      # Extração do Postgres
│       ├── transform/    # Transformação para DTOs
│       ├── load/        # Persistência no SQLite
│       ├── pipeline.py   # Orquestrador ETL
│       ├── dto.py       # DTOs
│       └── queries/     # Queries SQL
├── core/
│   ├── config.py       # Settings
│   └── logging_config.py
├── domain/
│   ├── models/        # Entidades ORM
│   └── value_objects/
└── infrastructure/
│   ├── db/          # SQLAlchemy setup
│   ├── repositories/
│   └── postgres/   # Executor de queries
└── schemas/         # Schemas Pydantic
```

**Fluxo de uma requisição:**

```
Request HTTP
    └─► Route (produto.py)
            └─► ProdutoService
                    └─► Codigo (valida e normaliza o código)
                    └─► ProdutoRepository
                            └─► SQLite (cache)
                    └─► ProdutoResponse (Pydantic)
            └─► Response HTTP
```

---

## Endpoints

| Método | Rota | Descrição | Acesso |
|---|---|---|---|
| `POST` | `/auth/token` | Login e geração de token JWT | Público |
| `POST` | `/auth/register` | Criar novo usuário | Admin |
| `GET` | `/produtos/` | Lista produtos com paginação | Autenticado |
| `GET` | `/produtos/{codigo}` | Busca produto por EAN ou PLU (dados públicos) | Autenticado |
| `GET` | `/produtos/{codigo}/completo` | Busca produto com custo, markup e margem | Supervisor/Admin |
| `GET` | `/status/` | Retorna data/hora da última atualização do cache | Público |
| `POST` | `/admin/sync` | Dispara sync em background | Admin |
| `GET` | `/admin/sync/{job_id}` | Verifica status de um job | Admin |
| `GET` | `/admin/sync/` | Lista histórico de jobs | Admin |

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
# Rodar ETL (para popular o cache)
python -m price_checker.etl.run_etl
```

**Fases:**

1. **Extract** — `ProdutoExtractor` executa as queries `produto.sql` e `codigo.sql` no Postgres
2. **Transform** — agrupa códigos de barras por produto, converte para DTOs
3. **Load** — trunca e reinsere produtos e códigos no SQLite, registra timestamp em `CacheStatus`

> O ETL requer `POSTGRES_URL` configurado no `.env`. Sem ele, o `PostgresLoader` levanta `RuntimeError` com mensagem clara.

---

## Autenticação

A API utiliza **JWT (JSON Web Token)** para controle de acesso. O fluxo é:

1. **Login** — `POST /auth/token` com `username` e `password` retorna o `access_token`
2. **Uso** — informe o token no header `Authorization: Bearer <token>`

### Roles

| Role | Descrição |
|---|---|
| `operador` | Consulta básica (sem custo, markup, margem) |
| `supervisor` | Consulta completa de qualquer produto |
| `admin` | Administrador — pode criar outros usuários |

### Criando o primeiro admin

```bash
python scripts/create_admin.py admin "Administrador" sua_senha
```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
POSTGRES_URL=postgresql://usuario:senha@host:5432/banco
SQLITE_URL=sqlite:///./data/price_checker.db
JWT_SECRET=sua-chave-secreta-grande-e-aleatoria
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

| Variável | Obrigatória | Descrição |
|---|---|---|
| `POSTGRES_URL` | Sim (para ETL) | Connection string do banco de origem |
| `SQLITE_URL` | Sim | Caminho do banco SQLite local |
| `JWT_SECRET` | Sim | Chave secreta para assinar tokens JWT (gere uma string longa e aleatória) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | Tempo de expiração do token (padrão: 60 minutos) |

---

## Instalação e execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Inicializar banco e rodar ETL
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

A suíte cobre: validação de códigos (EAN/PLU), métricas do model (markup, margem, edge cases), serialização do schema Pydantic, regras de negócio do service (mock de repositório, clamp de paginação, código inválido) e transformação ETL, além de segurança (hash de senhas) e autenticação JWT.

### Testes de Integração API

Testes de integração cobrem todos os endpoints da API usando `FastAPI TestClient` com SQLite em memória:

```
tests/
├── api/
│   ├── conftest.py          # Fixtures (client, usuários, tokens)
│   └── test_api.py          # 26 casos de teste
├── etl/
│   └── test_transform.py
├── models/
│   └── test_produto_model.py
├── repositories/
│   └── test_produto_repository.py
├── schemas/
│   └── test_produto_schema.py
├── services/
│   ├── test_produto_service.py
│   └── test_auth_service.py
└── utils/
    ├── test_codigo.py
    └── test_security.py
```

#### Cobertura dos testes de integração

| Categoria | Casos |
|---|---|
| Autenticação (token) | Validação, credenciais inválidas, usuário inexistente, campos vazios |
| Registro de usuário | Admin cria usuário, sem autenticação, role inválida |
| Listagem de produtos | Autenticado, sem autenticação, paginação |
| Busca de produto | Por código válido, inexistente, código inválido |
| Detalhes completos | Supervisor/Admin acessa, Operador bloqueado, sem autenticação |
| Status do cache | Acesso público |
| Admin Sync | Trigger, permissões (supervisor/operador/anônimo), histórico, status de job |
| CORS | Headers em requisições OPTIONS |
| Repositories | Testes de repositórios com SQLite em memória |

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

- [x] Testes de integração da API com `TestClient` e banco SQLite em memória
- [ ] Endpoint de busca por nome (`GET /produtos/busca?q=`)
- [ ] Filtros por grupo e família em `GET /produtos/`
- [ ] Frontend mobile (PWA) com leitura de código de barras pela câmera
- [ ] Agendamento automático do ETL (cron)
- [ ] Endpoint para cancelar job em andamento
- [ ] Notificação (WebSocket) ao completar sync
- [x] Logging detalhado por fase ETL

---

## Autor

Desenvolvido como projeto de portfólio — backend Python / análise de dados.