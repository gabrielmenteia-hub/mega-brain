# AlphaChat — Setup Guide

## Pré-requisitos

- Python 3.11+
- Node.js 18+
- Conta Supabase (free tier serve)
- Conta Pinecone (free tier serve)
- Chave Anthropic Claude
- Chave OpenAI (só para embeddings)
- Conta Stripe (opcional — só necessário para pagamentos)

---

## STEP 1 — Supabase

1. Criar projeto em https://supabase.com
2. Ir em **Settings → API** e copiar:
   - Project URL
   - `anon` key
   - `service_role` key
   - **JWT Secret** (aba "JWT Settings")
3. Abrir **SQL Editor** e executar o conteúdo de `docs/SUPABASE_SCHEMA.sql`

---

## STEP 2 — Pinecone

1. Criar conta em https://pinecone.io
2. Criar index chamado `alphachat-knowledge`:
   - Dimension: **1536**
   - Metric: **cosine**
   - Cloud: AWS us-east-1 (free serverless)
3. Copiar API Key em **API Keys**

---

## STEP 3 — Stripe (opcional)

Necessário apenas para ativar pagamentos. Pule se quiser rodar só com plano gratuito.

1. Criar conta em https://dashboard.stripe.com
2. **Developers → API Keys** → copiar `Secret key` (começa com `sk_test_`)
3. Criar dois produtos em **Products**:
   - **Pro** — R$ 29,90/mês → copiar o Price ID (`price_xxx`)
   - **Master** — R$ 59,90/mês → copiar o Price ID (`price_xxx`)
4. Criar webhook em **Developers → Webhooks**:
   - Endpoint URL: `https://seu-backend.com/api/subscription/webhook`
   - Eventos: `checkout.session.completed`, `customer.subscription.deleted`, `customer.subscription.updated`
   - Copiar **Signing secret** (`whsec_xxx`)

> **Desenvolvimento local:** use o [Stripe CLI](https://stripe.com/docs/stripe-cli) para receber webhooks localmente:
> ```bash
> stripe listen --forward-to localhost:8000/api/subscription/webhook
> ```

---

## STEP 4 — Backend

```bash
cd backend

# Criar e ativar virtualenv
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
```

Editar `.env` e preencher:

| Variável | Onde encontrar |
|----------|----------------|
| `SUPABASE_URL` | Supabase → Settings → API → Project URL |
| `SUPABASE_KEY` | Supabase → Settings → API → anon key |
| `SUPABASE_SERVICE_KEY` | Supabase → Settings → API → service_role key |
| `SUPABASE_JWT_SECRET` | Supabase → Settings → API → JWT Secret |
| `PINECONE_API_KEY` | Pinecone → API Keys |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `OPENAI_API_KEY` | platform.openai.com → API Keys |
| `STRIPE_SECRET_KEY` | Stripe → Developers → API Keys |
| `STRIPE_WEBHOOK_SECRET` | Stripe → Developers → Webhooks → Signing secret |
| `STRIPE_PRICE_PRO` | Stripe → Products → Pro → Price ID |
| `STRIPE_PRICE_MASTER` | Stripe → Products → Master → Price ID |

```bash
# Rodar o servidor
uvicorn app.main:app --reload
```

API em: http://localhost:8000  
Documentação interativa: http://localhost:8000/docs

---

## STEP 5 — Popular Pinecone

Necessário antes de usar a Biblioteca do app. Rodar uma vez só.

```bash
# Dentro de backend/ com venv ativo
python scripts/populate_pinecone.py
# Usa ../knowledge/unified_knowledge_base.json por padrão
# Para caminho customizado:
# python scripts/populate_pinecone.py --input /caminho/para/knowledge_base.json
```

Aguardar até ver: `População concluída. Total no index: 89 vetores.`

---

## STEP 6 — Mobile

```bash
cd mobile
npm install
cp .env.example .env
```

Editar `mobile/.env`:

| Variável | Valor local | Produção |
|----------|-------------|----------|
| `API_URL` | `http://localhost:8000` | `https://api.seudominio.com` |
| `SUPABASE_URL` | `https://xxx.supabase.co` | mesmo |
| `SUPABASE_ANON_KEY` | `eyJ...` (anon key) | mesmo |

> **Android com backend local:** usar `http://10.0.2.2:8000` no lugar de `localhost`.

```bash
npx expo start
```

- **Web:** http://localhost:8081
- **iOS/Android:** escanear QR com o app Expo Go

---

## Estrutura do Projeto

```
alphachat/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/           → config, database, auth (JWT)
│   │   ├── api/routes/     → sessions, messages, progress, knowledge, subscription
│   │   ├── services/       → character_engine, coach_analyzer, knowledge_retriever
│   │   └── models/
│   ├── scripts/
│   │   └── populate_pinecone.py
│   ├── requirements.txt
│   └── .env.example
├── mobile/                 → React Native + Expo Router
│   ├── app/
│   │   ├── (auth)/         → onboarding, login
│   │   ├── (tabs)/         → dashboard, library, profile
│   │   └── session/        → setup, [id], analysis/[id]
│   ├── lib/                → api.ts, store.ts, supabase.ts
│   └── .env.example
├── knowledge/
│   └── unified_knowledge_base.json
└── docs/
    ├── SETUP.md
    └── SUPABASE_SCHEMA.sql
```

---

## Verificação rápida

Após subir o backend, confirme que está funcionando:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

Após login no app, checar no Supabase → Table Editor se o usuário foi criado com as 5 skills inicializadas (`user_skills`).
