# Price Checker API - Contexto para Frontend

## Visão Geral

API REST para consulta de preços e métricas de produtos. Construída com FastAPI + SQLite (cache local de PostgreSQL).

## Base URL

```
http://localhost:8000
```

## Documentação Interativa

```
http://localhost:8000/docs
```

---

## Autenticação

A API usa **JWT Bearer Token**.

### Fluxo

1. Fazer login em `POST /auth/token` com username/password
2. Receber `access_token` na resposta
3. Incluir token em todas requisições autenticadas:

```
Authorization: Bearer <access_token>
```

### Tipo de Resposta do Token

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Endpoints

### Auth

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/auth/token` | Não | Login - retorna JWT |
| POST | `/auth/register` | Admin | Criar usuário |

### Login (`POST /auth/token`)

**Request (form-data):**
```
username: string
password: string
```

**Response 200:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Response 401:**
```json
{
  "detail": "Credenciais inválidas"
}
```

### Registro (`POST /auth/register`)

**Request (JSON):**
```json
{
  "username": "string",
  "nome_exibicao": "string",
  "password": "string",
  "role": "operador | supervisor | admin"
}
```

**Response 201:**
```json
{
  "id": 1,
  "username": "operador1",
  "nome_exibicao": "Operador Um",
  "role": "operador"
}
```

**Response 409:** Username duplicado

**Response 403:** Sem permissão de admin

---

### Produtos

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/produtos/` | Qualquer | Lista produtos (paginado) |
| GET | `/produtos/{codigo}` | Qualquer | Busca pública por código |
| GET | `/produtos/{codigo}/completo` | Supervisor/Admin | Busca completa (com custo) |

### Listar (`GET /produtos/`)

**Query Parameters:**
- `limit` (int, default: 50, max: 100)
- `offset` (int, default: 0)

**Response 200:**
```json
[
  {
    "codigo_chamada": "7891234567895",
    "grupo": "Eletrônicos",
    "familia": "Celulares",
    "nome": "Smartphone XYZ",
    "preco_venda": 999.99,
    "estoque": 50.0,
    "codigo_buscado": "7891234567895"
  }
]
```

### Busca Pública (`GET /produtos/{codigo}`)

Aceita: EAN-13, EAN-12, EAN-8, PLU-6 (código de 6 dígitos)

**Response 200:**
```json
{
  "codigo_chamada": "7891234567895",
  "grupo": "Eletrônicos",
  "familia": "Celulares",
  "nome": "Smartphone XYZ",
  "preco_venda": 999.99,
  "estoque": 50.0,
  "codigo_buscado": "7891234567895"
}
```

**Response 400:** Código inválido

**Response 404:** Produto não encontrado

### Busca Completa (`GET /produtos/{codigo}/completo`)

Retorna dados completos incluindo custo e margens.

**Response 200:**
```json
{
  "codigo_chamada": "7891234567895",
  "grupo": "Eletrônicos",
  "familia": "Celulares",
  "nome": "Smartphone XYZ",
  "preco_venda": 999.99,
  "preco_custo": 750.00,
  "estoque": 50.0,
  "codigo_buscado": "7891234567895",
  "markup": 0.333,
  "margem": 0.25
}
```

**Response 403:** Operador sem permissão (acesso restrito a supervisores)

---

### Status Cache

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/status/` | Não | Última atualização do cache |

**Response 200:**
```json
{
  "last_updated": "2024-01-15T10:30:00Z"
}
```

---

### Admin Sync

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/admin/sync` | Admin | Dispara sync ETL |
| GET | `/admin/sync/{job_id}` | Admin | Status de um job |
| GET | `/admin/sync` | Admin | Lista histórico |

### Trigger Sync (`POST /admin/sync`)

**Response 200:**
```json
{
  "job_id": 1,
  "status": "started",
  "message": "Sync iniciado em background"
}
```

### Status Sync (`GET /admin/sync/{job_id}`)

**Response 200:**
```json
{
  "job_id": 1,
  "started_at": "2024-01-15T10:30:00Z",
  "finished_at": "2024-01-15T10:31:00Z",
  "status": "sucesso | em_progresso | erro",
  "produtos_count": 1500,
  "codigos_count": 3200,
  "error_message": null
}
```

### Listar Histórico (`GET /admin/sync`)

**Query Parameters:**
- `limit` (int, default: 10)

**Response 200:**
```json
{
  "jobs": [...],
  "total": 5
}
```

---

## Roles e Permissões

| Role | Permissões |
|------|------------|
| `operador` | Listar/buscar produtos (dados públicos), status cache |
| `supervisor` | Tudo acima + detalhes completos de produtos |
| `admin` | Tudo acima + criar usuários + gerenciar sync ETL |

---

## Códigos de Status HTTP

| Status | Significado |
|--------|-------------|
| 200 | Sucesso |
| 201 | Criado |
| 400 | Código inválido |
| 401 | Não autenticado / Token inválido |
| 403 | Sem permissão |
| 404 | Não encontrado |
| 409 | Conflito (ex: username duplicado) |
| 422 | Validação falhou |
| 500 | Erro interno |

---

## Formatos de Código Suportados

| Tipo | Tamanho | Exemplo |
|------|---------|---------|
| EAN-13 | 13 dígitos | `7891234567895` |
| EAN-12 | 12 dígitos | `789123456789` |
| EAN-8 | 8 dígitos | `78936478` |
| PLU-6 | 6 dígitos | `123456` |

A API normaliza códigos automaticamente (remove espaços e hífens).

---

## CORS

A API não tem CORS configurado explicitamente. Para desenvolvimento local, o frontend em `localhost:3000` deve funcionar. Em produção, configurar apropriadamente.

---

## Variáveis de Ambiente Necessárias

```env
JWT_SECRET=sua-chave-secreta-minimo-32-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=60
SQLITE_URL=sqlite:///./price_checker.db
```

---

## Exemplo de Código Frontend

### Login e Busca de Produto

```typescript
const API_BASE = 'http://localhost:8000';

async function login(username: string, password: string): Promise<string> {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${API_BASE}/auth/token`, {
    method: 'POST',
    body: formData,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  if (!response.ok) throw new Error('Login falhou');
  const data = await response.json();
  return data.access_token;
}

async function buscarProduto(token: string, codigo: string) {
  const response = await fetch(`${API_BASE}/produtos/${codigo}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });

  if (response.status === 404) return null;
  if (!response.ok) throw new Error('Erro na busca');
  return response.json();
}
```