# price_checker

[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

API REST para consulta de preços e métricas de produtos, construída com **FastAPI** e **SQLite** como cache local de um banco **PostgreSQL** de origem.

> Projeto de portfólio desenvolvido para resolver um problema real de varejo: operadores precisam consultar informações rápidas sem depender de conectividade constante com o banco principal.

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
| Autenticação | JWT (PyJWT) + bcrypt |
| Gerenciador | uv |

---

## Arquitetura

O projeto segue arquitetura em camadas com separação clara de responsabilidades, aplicando princípios SOLID e DRY:

```
price_checker/
├── domain/
│   ├── models/        # Entidades ORM (SQLAlchemy)
│   ├── value_objects/ # Objetos de valor (ex: validação de códigos)
│   └── enums.py     # RolesEnum (escalável para SaaS)
├── application/
│   ├── services/      # Regras de negócio
│   ├── bi/           # Business Intelligence (relatórios)
│   │   ├── queries/ # SQLs externos (BiQueryLoader)
│   │   └── reporting/ # Relatórios por dimensão
│   └── etl/
│       ├── extract/   # Extração do Postgres
│       ├── transform/ # Transformação para DTOs
│       ├── load/      # Persistência no SQLite
│       ├── queries/  # Queries SQL (QueryLoader)
│       └── pipeline.py # Orquestrador ETL
├── infrastructure/
│   ├── db/          # SQLAlchemy setup + session factory
│   ├── repositories/ # Acesso a dados (interfaces)
│   └── postgres/    # Executor de queries
├── api/
│   ├── deps.py      # Injeção de dependência + require_role helper
│   └── routes/      # Endpoints FastAPI
│       ├── produto.py
│       ├── auth.py
│       ├── admin.py
│       └── cache_status.py
├── core/
│   ├── config.py     # Settings (pydantic-settings)
│   └── logging_config.py
└── schemas/         # Schemas Pydantic (contratos da API)
```

**Refatorações recentes:**
- `BaseQueryLoader` com herança para evitar SQL hardcoded (DRY/SOLID)
- `RolesEnum` para escalabilidade de permissões (preparando para SaaS)
- Proxy Vite para tunnel único (Cloudflare)

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
uv run python -m price_checker.etl.run_etl
```

**Fases:**

1. **Extract** — `ProdutoExtractor` executa as queries SQL externas no Postgres (via `QueryLoader`)
2. **Transform** — agrupa códigos de barras por produto, converte para DTOs
3. **Load** — trunca e reinsere produtos e códigos no SQLite, registra timestamp em `CacheStatus`

> Queries SQL foram extraídas para arquivos `.sql` seguindo padrão DRY com `BaseQueryLoader`.

---

## Autenticação

A API utiliza **JWT (JSON Web Token)** para controle de acesso. O fluxo é:

1. **Login** — `POST /auth/token` com `username` e `password` retorna o `access_token`
2. **Uso** — informe o token no header `Authorization: Bearer <token>`

### Roles e Permissões

O sistema usa `RolesEnum` (enum escalável) para controle de acesso:

| Role | Descrição | Permissões |
|------|-----------|-------------|
| `operador` | Consulta básica | Vê preço, estoque (sem custo/margem) |
| `supervisor` | Gerência | Consulta completa + relatórios |
| `admin` | Administrador | Tudo + gerenciamento de usuários |

> O `require_role()` helper centraliza a lógica de permissões, eliminando strings hardcoded.

### Criando o primeiro admin

```bash
uv run python scripts/create_admin.py admin "Administrador" sua_senha
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
# Clone o repositório
git clone https://github.com/seu-usuario/price_checker.git
cd price_checker

# Instale as dependências (usando uv)
uv sync

# Configure o .env (veja seção Configuração)
cp .env.example .env
# Edite o .env com suas credenciais

# Inicializar banco e rodar ETL
uv run python -m price_checker.etl.run_etl

# Subir a API (com auto-reload)
uv run uvicorn price_checker.main:app --reload --host 0.0.0.0 --port 8000
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

## Business Intelligence

O módulo BI permite análise de vendas, trocas, perdas e consumo:

- Relatórios por dimensão (produto, grupo, família)
- Curva ABC automática
- Análise temporal (por hora, dia da semana)
- KPIs (faturamento, ticket médio, itens por ticket)

> SQLs organizados em `bi/queries/` com `BiQueryLoader` (herda de `BaseQueryLoader`).  
> Endpoints de BI estão em desenvolvimento.

---

## Melhorias planejadas

- [x] Testes de integração da API com `TestClient` e banco SQLite em memória
- [x] Refatoração SQL (BaseQueryLoader + Herança)
- [x] RolesEnum para escalabilidade SaaS
- [x] Proxy Vite para tunnel único (Cloudflare)
- [x] Logging detalhado por fase ETL
- [ ] Endpoint de busca por nome (`GET /produtos/busca?q=`)
- [ ] Filtros por grupo e família em `GET /produtos/`
- [ ] Endpoints de BI (relatórios e dashboards)
- [ ] Frontend mobile (PWA) com leitura de código de barras pela câmera
- [ ] Agendamento automático do ETL (cron)
- [ ] Endpoint para cancelar job em andamento
- [ ] Notificação (WebSocket) ao completar sync

---

## Lições Aprendidas

- SQL hardcoded é um pesadelo de manutenção → refatorei para arquivos externos com herança
- Strings hardcoded de roles limitam escalabilidade → criei RolesEnum
- Testes não são opcionais → cobrem 26+ casos de uso
- Documentação é parte do código → README vivo e atualizado

---

## Autor

Desenvolvido por **Pedro Lucas** como case técnico de backend Python / análise de dados.

- Contato: pedrolucas.sinuso@gmail.com
- LinkedIn: [linkedin.com/in/pedro-sinuso](https://www.linkedin.com/in/pedro-sinuso)
- GitHub: [github.com/PedroLucasSinuso](https://github.com/PedroLucasSinuso)

> Gostou do projeto? Deixe uma estrela e me conte o que melhoraria!