# LOVABLE MASTER PROMPT — Código Presença Magnética
> **Versão:** 1.1 | **Data:** 2026-04-04 | **Update:** System prompt completo do simulador integrado na Edge Function `simulator-response`

---

# PRODUTO: Código Presença Magnética
# Tipo: Info APP web (PWA-ready)
# Stack: Lovable + Supabase
# Versão do prompt: 1.0 FINAL

---

## PRODUCT OVERVIEW

Crie um Info APP chamado **Código Presença Magnética**.

O produto ensina homens a ativarem os 4 desejos primitivos femininos (Conexão, Segurança, Desejo, Curiosidade) através de conversas profundas e naturais — não frases prontas, mas padrões de pensamento que geram atração genuína.

**Público:** Homens 20-40 anos, todos os níveis de experiência
**Proposta de valor:** Sistema de calibração de atração — fica mais preciso a cada uso, não é curso linear
**Diferencial:** Loop de feedback real + Simulador com personas variáveis

**Tom de voz:** Direto e masculino. Frases curtas, sem condescendência. Técnico, não motivacional. Sem julgamento — feedback é diagnóstico, não crítica. NUNCA use lorem ipsum.

---

## TECH STACK

- **Frontend:** React + Tailwind CSS + TypeScript
- **Backend:** Supabase (Auth, Database, Edge Functions)
- **Auth:** Email/senha + Google OAuth — redirect URL: `/auth/callback`
- **Banco:** PostgreSQL via Supabase com RLS ativo
- **Charts:** Recharts (para radar chart no perfil)
- **Edge Functions:** 4 funções (detalhadas abaixo)

---

## DESIGN SYSTEM

**Paleta de cores:**
```
Background principal:  #0D0D0D
Background card:       #1A1A1A
Background card hover: #2A2A2A
Accent primário:       #C9A84C  (dourado)
Accent secundário:     #8B0000  (vermelho escuro)
Texto principal:       #F5F5F5
Texto secundário:      #9A9A9A
Sucesso:               #2E7D32
Erro:                  #C62828
```

**Tipografia:**
- Títulos: font-weight 700, tracking-tight
- Corpo: font-weight 400, leading-relaxed
- Labels/badges: font-weight 600, uppercase, letter-spacing 0.05em

**Card padrão:**
```css
border-radius: 12px;
background: #1A1A1A;
border: 1px solid rgba(201, 168, 76, 0.15);
padding: 24px;
```
```css
/* hover */
border-color: rgba(201, 168, 76, 0.4);
```

**Badges dos 4 desejos (usar em TODO o sistema — componente DesireBadge):**
```
🔗 Conexão:     bg #1A237E  text #90CAF9
🛡️ Segurança:   bg #1B5E20  text #A5D6A7
🔥 Desejo:      bg #7F0000  text #EF9A9A
🌀 Curiosidade: bg #4A148C  text #CE93D8
```

**PatternBadge (padrão do usuário):**
```
ANSIOSO:    bg #7F0000  text #EF9A9A
NEUTRO:     bg #333333  text #9A9A9A
DOMINANTE:  bg #C9A84C  text #0D0D0D
```

**ProgressBar:** altura 6px, cor #C9A84C, background #333333, border-radius 99px

---

## CONSTANTES GLOBAIS (TypeScript)

```typescript
export const DESIRES = ['conexao', 'seguranca', 'desejo', 'curiosidade'] as const
export type Desire = typeof DESIRES[number]

export const PATTERNS = ['ansioso', 'neutro', 'dominante'] as const
export type Pattern = typeof PATTERNS[number]

export const DESIRE_CONFIG: Record<Desire, { label: string; icon: string; bg: string; text: string }> = {
  conexao:     { label: 'Conexão',     icon: '🔗', bg: '#1A237E', text: '#90CAF9' },
  seguranca:   { label: 'Segurança',   icon: '🛡️', bg: '#1B5E20', text: '#A5D6A7' },
  desejo:      { label: 'Desejo',      icon: '🔥', bg: '#7F0000', text: '#EF9A9A' },
  curiosidade: { label: 'Curiosidade', icon: '🌀', bg: '#4A148C', text: '#CE93D8' },
}
```

---

## DATABASE SCHEMA

```sql
-- ═══════════════════════════════════════════════════════
-- USERS
-- ═══════════════════════════════════════════════════════

create table users_profile (
  id              uuid references auth.users primary key,
  name            text not null,
  current_pattern text check (current_pattern in ('ansioso','neutro','dominante')),
  onboarding_done boolean default false,
  streak_days     integer default 0,
  streak_at_risk  boolean default false,
  last_active_at  timestamptz,
  created_at      timestamptz default now()
);

-- ═══════════════════════════════════════════════════════
-- PROGRESSO POR DESEJO (1 linha por desejo por usuário)
-- ═══════════════════════════════════════════════════════

create table desires_progress (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid references users_profile not null,
  desire     text check (desire in ('conexao','seguranca','desejo','curiosidade')),
  points     integer default 0 check (points >= 0 and points <= 100),
  updated_at timestamptz default now(),
  unique (user_id, desire)
);

-- ═══════════════════════════════════════════════════════
-- LIÇÕES
-- ═══════════════════════════════════════════════════════

create table lessons (
  id           uuid primary key default gen_random_uuid(),
  desire       text check (desire in ('conexao','seguranca','desejo','curiosidade')),
  type         text check (type in ('teoria','exemplo','exercicio')),
  title        text not null,
  content      text not null,
  order_index  integer not null,
  duration_min integer default 5,
  created_at   timestamptz default now()
);

create table lesson_progress (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid references users_profile not null,
  lesson_id    uuid references lessons not null,
  status       text check (status in ('disponivel','em_progresso','concluida')) default 'disponivel',
  completed_at timestamptz,
  unique (user_id, lesson_id)
);

-- ═══════════════════════════════════════════════════════
-- PERSONAS DO SIMULADOR
-- ═══════════════════════════════════════════════════════

create table personas (
  id                    uuid primary key default gen_random_uuid(),
  slug                  text unique not null,
  name                  text not null,
  description           text not null,
  profile_text          text not null,
  desire_tested         text not null,
  unlock_after_missions integer default 0
);

create table user_personas (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references users_profile not null,
  persona_id  uuid references personas not null,
  unlocked_at timestamptz default now(),
  unique (user_id, persona_id)
);

-- ═══════════════════════════════════════════════════════
-- SESSÕES DO SIMULADOR
-- ═══════════════════════════════════════════════════════

create table simulator_sessions (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid references users_profile not null,
  persona_id        uuid references personas not null,
  messages          jsonb default '[]',
  desires_activated jsonb default '{}',
  feedback_text     text,
  score             integer,
  status            text check (status in ('em_andamento','concluida')) default 'em_andamento',
  created_at        timestamptz default now(),
  completed_at      timestamptz
);

-- ═══════════════════════════════════════════════════════
-- MISSÕES
-- ═══════════════════════════════════════════════════════

create table missions (
  id               uuid primary key default gen_random_uuid(),
  title            text not null,
  description      text not null,
  desire_focus     text check (desire_focus in ('conexao','seguranca','desejo','curiosidade')),
  tool_name        text not null,
  tool_explanation text not null,
  tool_example     text not null,
  difficulty       text check (difficulty in ('iniciante','intermediario','avancado')),
  order_index      integer not null,
  created_at       timestamptz default now()
);

create table mission_logs (
  id                 uuid primary key default gen_random_uuid(),
  user_id            uuid references users_profile not null,
  mission_id         uuid references missions not null,
  status             text check (status in ('pendente','executando','registrada','analisada')) default 'pendente',
  what_i_said        text,
  her_reaction       text check (her_reaction in (
                       'fria','respondeu_mais','ficou_curiosa',
                       'avancou','visualizou_vacuo','sumiu'
                     )),
  user_notes         text,
  desires_activated  text[],
  system_feedback    text,
  pattern_identified text,
  skipped            boolean default false,
  scheduled_for      date default current_date,
  completed_at       timestamptz,
  created_at         timestamptz default now()
);

-- ═══════════════════════════════════════════════════════
-- BIBLIOTECA DE CONVERSAS
-- ═══════════════════════════════════════════════════════

create table conversations_library (
  id                uuid primary key default gen_random_uuid(),
  desire            text check (desire in ('conexao','seguranca','desejo','curiosidade')),
  persona_slug      text not null,
  situation         text not null,
  messages          jsonb not null,
  desires_activated text[],
  analysis          text not null,
  created_at        timestamptz default now()
);

-- ═══════════════════════════════════════════════════════
-- ÍNDICES
-- ═══════════════════════════════════════════════════════

create index idx_desires_progress_user   on desires_progress(user_id);
create index idx_lesson_progress_user    on lesson_progress(user_id);
create index idx_mission_logs_user       on mission_logs(user_id);
create index idx_mission_logs_scheduled  on mission_logs(scheduled_for);
create index idx_simulator_sessions_user on simulator_sessions(user_id);
create index idx_lessons_desire_order    on lessons(desire, order_index);
create index idx_missions_desire         on missions(desire_focus, order_index);
```

---

## RLS POLICIES

```sql
-- Dados de usuário: acesso apenas ao próprio usuário
alter table users_profile        enable row level security;
alter table desires_progress     enable row level security;
alter table lesson_progress      enable row level security;
alter table user_personas        enable row level security;
alter table simulator_sessions   enable row level security;
alter table mission_logs         enable row level security;

create policy "user_own_data" on users_profile        using (id = auth.uid());
create policy "user_own_data" on desires_progress     using (user_id = auth.uid());
create policy "user_own_data" on lesson_progress      using (user_id = auth.uid());
create policy "user_own_data" on user_personas        using (user_id = auth.uid());
create policy "user_own_data" on simulator_sessions   using (user_id = auth.uid());
create policy "user_own_data" on mission_logs         using (user_id = auth.uid());

-- Conteúdo público: leitura para todos os autenticados
alter table lessons               enable row level security;
alter table personas              enable row level security;
alter table missions              enable row level security;
alter table conversations_library enable row level security;

create policy "authenticated_read" on lessons               for select using (auth.role() = 'authenticated');
create policy "authenticated_read" on personas              for select using (auth.role() = 'authenticated');
create policy "authenticated_read" on missions              for select using (auth.role() = 'authenticated');
create policy "authenticated_read" on conversations_library for select using (auth.role() = 'authenticated');
```

---

## EDGE FUNCTIONS

### 1. `on-user-created` — DB Webhook (INSERT em auth.users)
Cria automaticamente a linha em `users_profile` após cadastro.

### 2. `analyze-mission` — HTTP POST
```
Body: { mission_log_id: string }

Fluxo:
1. Busca mission_log + mission (ferramenta, foco, dificuldade)
2. Monta prompt GPT-4o-mini com: ferramenta usada, what_i_said, her_reaction, user_notes
3. GPT retorna JSON: { desires_activated: string[], pattern_identified: string, system_feedback: string }
4. UPDATE mission_logs SET desires_activated, pattern_identified, system_feedback, status='analisada'
5. UPDATE desires_progress: incrementa points para cada desejo ativado
6. Return { success: true, feedback: system_feedback }
```

### 3. `simulator-response` — HTTP POST
```
Body: { session_id: string, user_message: string }

Fluxo:
1. Busca simulator_session + persona (profile_text, desire_tested, name)
2. Reconstrói histórico de mensagens do jsonb
3. Monta SYSTEM PROMPT (abaixo) com persona injetada + histórico como messages
4. Chama GPT-4o-mini com response_format: { type: "json_object" }
5. GPT retorna JSON: { persona_response: string, feedback: Feedback, desires_activated: Record<Desire, number>, engagement_score: number }
6. UPDATE simulator_sessions SET messages (append), desires_activated (merge)
7. Return { persona_response, feedback, desires_activated, engagement_score }
```

**Tipo Feedback:**
```typescript
type Feedback = {
  status: '✅' | '❌' | '⚠️'
  summary: string          // 1 linha direta
  why: string              // explicação psicológica, 2-3 linhas
  alternative: string      // versão melhorada da mensagem dele
  engagement_score: number // 0-100
}
```

**SYSTEM PROMPT DA EDGE FUNCTION** (injetar `{{persona_name}}`, `{{persona_profile}}`, `{{desire_tested}}`):

```
You are a dual-mode AI agent for the Código Presença Magnética app.
You operate in two simultaneous modes during every interaction:

MODE A — PERSONA: You are {{persona_name}}, the woman in the simulation.
MODE B — ANALYST: You are the communication coach providing structured feedback.

Your mission is to help men develop genuine, confident communication
skills through realistic practice — not manipulation techniques.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## PERSONA PROFILE
{{persona_profile}}
Primary desire being tested: {{desire_tested}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## MODE A — PERSONA (Simulate with absolute realism)

You are a real woman with your own personality. Initial interest level: neutral
(not easy, not hard — realistic). Your response DYNAMICALLY CHANGES based on
the quality of his communication.

WHEN HE COMMUNICATES WELL (authenticity, confidence, humor, genuine attention):
- Your responses become longer and more engaged
- You ask questions back spontaneously
- Use more emojis and enthusiasm
- Give "hooks" for him to continue
- Response time (simulated) decreases

WHEN HE COMMUNICATES POORLY (neediness, generic messages, trying to impress):
- Your responses become short and dry
- No questions asked
- Emojis disappear
- After 3 bad responses in a row: stop responding

REALISTIC TESTS (apply naturally, never telegraph them):
- Unexpected short response → tests if he becomes needy
- Deliberate "delay" → tests insecurity
- Agreeing with everything → tests if he has his own opinion
- Small challenge/provocation → tests if he handles it with lightness

PROGRESSION:
- Messages 1-3: OPENING — first impression
- Messages 4-8: BUILDING — deepen connection
- Messages 9-12: QUALIFICATION — real compatibility
- Messages 13-15: TRANSITION — move toward meeting
- Final: LOGISTICS — set details

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## MODE B — ANALYST (Structured feedback after each message)

Evaluate his message against these criteria:

POSITIVE SIGNALS:
→ Authenticity: genuine personality, comfortable with imperfections
→ Calibrated confidence: makes statements, doesn't seek approval
→ Genuine attention: references what she said, asks real questions
→ Humor and lightness: creates fun moments without forcing
→ Respectful leadership: takes initiative, respects boundaries

PROBLEM SIGNALS:
→ Needy behavior: always responds instantly, tries too hard to please
→ Generic messages: "Hey how are you?" — could be sent to anyone
→ Trying to impress: talks about himself too much, disguised brags
→ Premature sexualization: excessive physical compliments, misplaced insinuations
→ Lack of investment: monosyllabic, doesn't contribute to conversation

SYMPTOM → DIMENSION DIAGNOSIS:
- Generic output → Persona/Role of his message is weak
- She ignores parts → His core request is buried
- Output varies too much → He's being ambiguous
- Wrong format → He didn't specify what he wanted back
- She does extras → No constraints on what NOT to do

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## OUTPUT FORMAT (MANDATORY — return valid JSON only)

{
  "persona_response": "<her response as the persona — realistic, dynamic>",
  "feedback": {
    "status": "<✅ | ❌ | ⚠️>",
    "summary": "<1 direct line: what happened>",
    "why": "<psychological explanation, 2-3 lines>",
    "alternative": "<improved version of his message, ready to use>"
  },
  "desires_activated": {
    "conexao": <0-100>,
    "seguranca": <0-100>,
    "desejo": <0-100>,
    "curiosidade": <0-100>
  },
  "engagement_score": <0-100>
}

ALWAYS:
- Separate persona response from analyst feedback (they are different JSON fields)
- Keep persona consistent within the simulation
- Always provide a concrete alternative in feedback, never just criticism
- Explain the psychological "why" of each evaluation
- Respect both genders — the goal is better men, not manipulators
- Return ONLY valid JSON, no markdown, no extra text

NEVER:
- Break character in persona_response
- Give vague feedback ("it was good", "could be better")
- Soften serious errors to avoid "hurting feelings"
- Teach manipulation or pressure techniques
- Advance stages without him demonstrating skills of the current stage
```

### 4. `generate-daily-mission` — Cron (meia-noite UTC-3)
Seleciona para cada usuário ativo a missão do desejo com menor `points` em `desires_progress`.

---

## AUTH & NAVIGATION

**Rotas públicas:** `/login`, `/cadastro`, `/onboarding`
**Rotas protegidas:** `/dashboard`, `/trilha/*`, `/simulador/*`, `/missao/*`, `/biblioteca`, `/perfil`

**Guard:** qualquer rota protegida sem `onboarding_done = true` → redirect `/onboarding`

**Bottom navigation (rotas protegidas, mobile-first):**
🏠 Dashboard | 🎯 Missão | 💬 Simulador | 📚 Biblioteca | 👤 Perfil

**Fluxo novo usuário:** Cadastro → `on-user-created` → `/onboarding` → `/dashboard`

---

## SCREENS

---

### TELA 1 — /cadastro — Cadastro

**Layout:**
- Logo centrado no topo
- Card central
- Campo email (type=email, placeholder="seu@email.com")
- Campo senha (type=password, placeholder="Mínimo 8 caracteres", toggle mostrar/ocultar)
- Botão primário full-width: **"Criar conta"** (dourado, desabilitado até validação)
- Divisor: "ou"
- Botão outline full-width: **"Continuar com Google"**
- Link footer: **"Já tem conta? Entrar"**

**Copy:**
- Headline: "Comece agora."
- Subtítulo: "Crie sua conta grátis."

**Validações visíveis:**
- Email inválido → borda vermelha + "E-mail inválido"
- Senha < 8 chars → "Mínimo 8 caracteres"
- E-mail já cadastrado (server) → toast "Esse e-mail já está em uso. Entrar?"

**Comportamento:**
- Submit → Supabase Auth signUp → trigger `on-user-created` → redirect `/onboarding`
- Google → popup OAuth → callback `/auth/callback` → redirect `/onboarding`

---

### TELA 2 — /login — Login

**Layout:** idêntico ao cadastro, sem campo confirmação de senha.

**Copy:**
- Headline: "Bem-vindo de volta."
- Botão: "Entrar"
- Link footer: "Não tem conta? Criar grátis"
- Link secundário abaixo do botão: "Esqueci minha senha"

**Erro:** toast "E-mail ou senha incorretos."
**Sucesso:** redirect `/dashboard` (se onboarding_done) ou `/onboarding`

---

### TELA 3 — /onboarding — Diagnóstico

**Layout:**
- Progress bar no topo (5 steps, preenchimento dourado)
- Label: "Pergunta [N] de 5"
- Card central: pergunta em h2 (font-size 20px, weight 700)
- 4 botões full-width, fundo #1A1A1A — estado selecionado: borda #C9A84C
- Botão "Próximo" fixo no rodapé — ativo só após seleção

**Copy:**
- Headline: "Primeiro, vamos entender onde você está."
- Subtítulo: "5 perguntas. Diagnóstico real. Sem julgamento."

**Perguntas:**

P1: "Quando você está conversando com uma mulher que te atrai, você geralmente..."
  A) Fico travado, não sei o que falar
  B) Respondo rápido demais tentando agradar
  C) Sou direto mas a conversa esfria rápido
  D) Consigo conversar mas não crio atração

P2: "Quando ela demora para responder, você..."
  A) Mando outra mensagem logo
  B) Fico ansioso mas espero
  C) Não ligo, continuo meu dia
  D) Mando algo engraçado para quebrar o gelo

P3: "Qual é o seu maior obstáculo em conversas?"
  A) Não sei como sair do "oi, tudo bem"
  B) A conversa morre depois de um tempo
  C) Ela some depois de um bom começo
  D) Não sei como criar tensão sem parecer grosseiro

P4: "Como as mulheres geralmente te veem?"
  A) Como amigo, nunca como interesse romântico
  B) Como legal, mas sem química
  C) Como intenso demais ou carente
  D) Bem, mas perco quando avanço

P5: "O que você quer aprender primeiro?"
  A) Como criar conexão real do zero
  B) Como gerar desejo sem parecer forçado
  C) Como ser misterioso e interessante
  D) Como transmitir segurança e presença

**Lógica do padrão:**
- Maioria A/B → ANSIOSO
- Maioria B/C misturadas → NEUTRO
- Maioria C/D → DOMINANTE

**Tela de resultado:**
- Headline: "Seu Padrão Identificado"
- PatternBadge grande centralizado
- Descrição do padrão:
  - ANSIOSO: "Você responde rápido, monitora o celular e interpreta silêncio como rejeição. Isso cria pressão — e ela sente. Sua jornada começa pela Segurança: aprenda a ocupar espaço sem precisar de validação."
  - NEUTRO: "Você é legal, mas não gera magnetismo. As conversas são confortáveis e terminam ali. Sua jornada começa pelo Desejo: aprenda a criar tensão sem forçar."
  - DOMINANTE: "Você tem presença, mas perde na execução. Avança cedo, fecha o loop antes da hora ou não calibra o que ela está sentindo. Sua jornada começa pela Conexão: aprenda a ler e ampliar o estado dela antes de avançar."
- CTA: "Começar Minha Jornada" → salva padrão em `users_profile`, `onboarding_done = true` → redirect `/dashboard`

---

### TELA 4 — /dashboard — Dashboard Principal

**Layout (scroll vertical, mobile-first):**

**Header:**
- H1 dourado: "Bom dia, [nome]."
- Subtítulo: "Dia [X] da sua jornada." OU "Sequência: [N] dias 🔥" (se streak > 0)
- PatternBadge pequeno, canto direito
- Banner laranja (se streak_at_risk=true): "Sua sequência está em risco. Complete uma ação hoje para não perder [N] dias."

**Card Missão do Dia (full-width, gradient dourado sutil nas bordas):**
- Label badge vermelho escuro uppercase: "MISSÃO DE HOJE"
- Título h2 da missão
- DesireBadge do foco
- Subtítulo: "Sua missão de hoje ativa [Desejo]. Leva ~10 minutos no mundo real."
- Botão: "Iniciar Missão" → `/missao/:id`

**Grid 2x2 dos 4 Desejos:**
- Cada card: DesireBadge + nome + ProgressBar (points/100) + "[X] lições concluídas"
- CTA: "Começar" (points=0) ou "Continuar" → `/trilha/:desejo`

**Card Simulador:**
- Título: "Simulador de Conversa"
- Subtítulo: "Pratique com 5 perfis femininos diferentes antes de jogar de verdade."
- Botão: "Iniciar Simulação" → `/simulador`

**Card Biblioteca:**
- Título: "Conversas Reais"
- Subtítulo: "[N] exemplos comentados. Veja o mecanismo funcionando na prática."
- Botão: "Ver Biblioteca" → `/biblioteca`

**Estados:**
- Loading: skeleton loaders em todos os cards
- Missão ausente: "Nenhuma missão gerada ainda. Tente amanhã."

---

### TELA 5 — /trilha/:desejo — Trilha do Desejo

**Layout:**
- Header: DesireBadge grande + "Trilha de [Desejo]" + ProgressBar + "[X] de [Y] lições concluídas"
- Lista de LessonCards:
  - Ícone tipo: 📖 teoria | 💬 exemplo | ⚡ exercício
  - Título + duração
  - Status: 🔒 bloqueado (opacity 0.5, não clicável) | disponível | ✅ concluído (dourado)
  - Lição ativa: borda dourada, ligeiramente expandida
- Toast ao clicar bloqueada: "Complete a lição anterior primeiro."
- Banner trilha completa: "Trilha completa. Você dominou [Desejo]."

---

### TELA 6 — /trilha/:desejo/:licao — Lição

**Layout:**
- Breadcrumb: "Trilha / [Desejo] / [Título]"
- DesireBadge + badge do tipo (teoria/exemplo/exercício)
- Título h1
- Conteúdo markdown renderizado (max-width 65ch)
- Barra de progresso de leitura (fixed top, 2px, #C9A84C)
- Botão fixo rodapé: "Concluir Lição" → status='concluida', +points no desejo, redirect trilha
  - Já concluída: "✅ Concluída — Ver próxima"
- Micro-interação ao concluir: check dourado expande (escala 1→1.5→1 em 300ms) antes do redirect

---

### TELA 7 — /simulador — Seleção de Persona

**Layout:**
- Headline: "Com quem você vai praticar hoje?"
- 5 PersonaCards:
  - Avatar (emoji grande em círculo colorido)
  - Nome + descrição 2 linhas
  - DesireBadge do desejo testado
  - CTA: "Escolher" (desbloqueada) ou "🔒 Complete [N] missões para desbloquear" (bloqueada)
  - Bloqueada: overlay escuro, cursor not-allowed

**Personas:**

1. **A Fechada** — "Respostas curtas, pouca energia. Você vai precisar criar motivo para ela continuar." — 🛡️ Segurança — desbloqueada por padrão
2. **A Provocadora** — "Direta, irônica, testa seus limites. Se você recuar, ela vai embora." — 🔥 Desejo — desbloqueada por padrão
3. **A Ocupada** — "Sempre com pressa. Janela de atenção curta. Cada mensagem sua precisa justificar a próxima." — 🔗 Conexão — desbloqueia após 5 missões
4. **A Emocional** — "Humor instável. O que funciona hoje pode não funcionar amanhã." — 🔗🛡️ Conexão + Segurança — desbloqueia após 10 missões
5. **A Independente** — "Não precisa de você. Não vai fingir interesse. Você tem que criar curiosidade do zero." — 🌀 Curiosidade — desbloqueia após 15 missões

---

### TELA 8 — /simulador/:sessao — Simulador: Chat

**Layout:**
- Header fixo: nome da persona + DesireBadge + botão "Encerrar" (direita)
- Indicador abaixo do header: "Desejos ativados: [badges]" (atualiza após cada resposta)
- Área de mensagens (scroll):
  - Mensagem da persona: esquerda, bg #2A2A2A, border-radius 12px 12px 12px 0
  - Mensagem do usuário: direita, bg rgba(201,168,76,0.13), border-radius 12px 12px 0 12px
  - Timestamp discreto (#9A9A9A, font-size 11px) abaixo de cada mensagem
- A primeira mensagem vem da persona (gerada ao iniciar a sessão)
- Indicador "digitando...": 3 pontos pulsando, cor #9A9A9A
- Input fixo rodapé: textarea auto-grow (max 3 linhas), placeholder "Escreva sua mensagem...", botão enviar seta dourada

**Comportamento:**
- Enviar → POST `/functions/v1/simulator-response` → append no JSONB
- Erro de rede → toast "Falha ao enviar. Verifique sua conexão e tente novamente."
- Botão "Encerrar" → modal confirmação:
  - Título: "Encerrar simulação?"
  - Subtítulo: "Você vai receber o feedback da conversa até aqui."
  - Confirmar: "Encerrar e ver resultado" → status='concluida' → `/simulador/:sessao/feedback`
  - Cancelar: "Continuar praticando"

---

### TELA 9 — /simulador/:sessao/feedback — Simulador: Feedback

**Layout:**
- Headline: "Resultado da Simulação"
- Subtítulo: "Com [Nome da Persona]"
- Grid 2x2 dos 4 desejos: DesireBadge + ProgressBar de % ativação + número
- Seção "O que funcionou": lista com ✅ (máx 3 itens)
- Seção "O que travou": lista com ⚠️ (máx 2 itens)
- Card destacado "1 ajuste para a próxima vez": fundo #1A1A1A, borda esquerda #C9A84C 3px
- CTAs:
  - Primário: "Registrar como Missão Real" → cria mission_log → `/missao/:id/registro`
  - Secundário outline: "Praticar Novamente" → nova sessão, mesma persona

**Copy de feedback:**
- Positivo: "Você ativou Curiosidade. Ela não vai parar de pensar nisso."
- Negativo: "Você fechou o loop cedo demais. Ela não teve motivo pra voltar."
- Vácuo: "Ela leu. Ela escolheu não responder. Você não criou o motivo certo."
- Recuo: "Você recuou quando ela testou. Desejo quebrado."

---

### TELA 10 — /missao/:id — Missão: Briefing

**Layout:**
- DesireBadge + badge dificuldade (INICIANTE | INTERMEDIÁRIO | AVANÇADO)
- Título h1 + descrição da missão
- Seção "A Ferramenta de Hoje":
  - Nome da ferramenta (h2, #C9A84C)
  - Explicação (parágrafo)
  - Card "Na prática:" fundo #1A1A1A, borda esquerda #C9A84C 3px, com `tool_example`
- Botão fixo rodapé: "Fui! Vou tentar agora" → status='executando'
  - Após clique: botão some, aparece card: "Agora vá ao mundo real. Aplique a ferramenta em uma conversa real. Volte aqui para registrar o resultado." + botão "Registrar Resultado" → `/missao/:id/registro`

**Redirect automático:**
- status='executando' → mostrar direto o card de registro
- status='analisada' → redirect `/missao/:id/analise`

---

### TELA 11 — /missao/:id/registro — Missão: Registro

**Layout:**
- Headline: "Como foi?"
- Textarea obrigatória:
  - Label: "O que você disse ou mandou?"
  - Placeholder: "Ex: 'Perguntei sobre o projeto dela e deixei uma pergunta aberta no final.'"
- Headline "A reação dela:" + 6 botões grandes full-width (seleção única):
  - ❄️ Ficou fria
  - 💬 Respondeu mais
  - 🌀 Ficou curiosa
  - ⚡ Avançamos
  - 👁️ Visualizou e não respondeu
  - 👻 Sumiu
  - Estado selecionado: borda #C9A84C + ícone ✓ canto superior direito (transição 200ms)
- Textarea opcional:
  - Label: "O que você acha que funcionou ou travou?"
  - Placeholder: "Opcional. Sua análise melhora o diagnóstico."
- Botão fixo rodapé: "Enviar para Análise" — ativo apenas com textarea obrigatória + reação preenchidas
  - Ao enviar: tela de loading "Analisando sua missão... Isso leva alguns segundos." → POST `analyze-mission` → redirect `/missao/:id/analise`

**Validação:** reação não selecionada ao tentar enviar → toast "Selecione a reação antes de enviar."

---

### TELA 12 — /missao/:id/analise — Missão: Análise

**Layout:**
- Headline: "Diagnóstico da Missão"
- Seção "Desejos Ativados": DesireBadges dos desires_activated (ou "Nenhum desejo ativado. Veja o ajuste sugerido abaixo.")
- Seção "Padrão Identificado": `pattern_identified` (1 parágrafo)
- Card "Ajuste para a Próxima": `system_feedback` com borda esquerda dourada
- ProgressBars dos 4 desejos animadas (transição 800ms ease-out do valor anterior para o novo)
- CTA: "Voltar ao Dashboard"

**Estados:**
- Análise em processamento: "Sua análise está sendo preparada. Atualizando em instantes." + auto-refresh 3s

---

### TELA 13 — /biblioteca — Biblioteca

**Layout:**
- Headline: "Conversas Reais"
- Subtítulo: "Veja o mecanismo funcionando na prática."
- Filtros: tabs (Todos | 🔗 Conexão | 🛡️ Segurança | 🔥 Desejo | 🌀 Curiosidade) + dropdown "Persona: Todas ▾"
- Grid de ConversationCards:
  - DesireBadge + badge da persona (nome)
  - Situação (1 linha, negrito)
  - Preview de 3-4 mensagens alternadas (compacto)
  - CTA: "Ver Análise Completa"
- Modal ao clicar:
  - Conversa completa com timestamps
  - Análise linha a linha (comentário em itálico #C9A84C após cada mensagem relevante)
  - Botão fechar ✕

**Empty states:**
- Filtro sem resultado: "Nenhuma conversa encontrada para esse filtro."
- Biblioteca vazia: "Nenhuma conversa na biblioteca ainda. Em breve."

---

### TELA 14 — /perfil — Perfil

**Layout:**
- Header: nome + PatternBadge (tamanho lg)
- **Radar Chart** (Recharts, 4 eixos = 4 desejos, 0-100):
  - Fundo transparente, linhas #333, área preenchida #C9A84C com opacity 0.2
  - Labels com DesireBadge miniatura em cada eixo
  - Headline: "Sua Calibração"
- **Grid de stats** (3 colunas):
  - "Missões realizadas: [N]"
  - "Sequência atual: [N] dias"
  - "Mais forte: [DesireBadge] | Mais fraco: [DesireBadge]"
  - Headline: "Em Números"
- **Histórico de Missões** (lista, últimas 20):
  - Headline: "Histórico de Missões"
  - Por item: data | título | DesireBadge | badge da reação | padrão identificado
  - Clicável → modal com análise completa
  - Paginação: "Ver mais missões"
- **CTA inferior** (visível após 30 missões):
  - Botão outline: "Refazer Diagnóstico"
  - Subtítulo: "Disponível após 30 missões. Seu padrão pode ter mudado."

**Empty state missões:** "Nenhuma missão registrada ainda. A teoria sem prática não muda nada."

---

## BUSINESS RULES

1. Nenhuma rota protegida é acessível sem `onboarding_done = true`
2. Lições desbloqueadas estritamente em sequência por `order_index`
3. Simulador começa com 2 personas: A Fechada + A Provocadora
4. A cada 5 missões completadas, nova persona desbloqueada (verificado via COUNT de mission_logs com status='analisada')
5. Missão do dia gerada com base no desejo de menor `points` em `desires_progress`
6. Missão pode ser pulada 1x por semana sem penalidade no streak (campo `skipped=true`)
7. Missão só é concluída após registro da reação (status='registrada') e análise (status='analisada')
8. Streak resetado após 48h sem `last_active_at` atualizado
9. Padrão recalculado automaticamente após 30 missões (`system_feedback` da IA atualiza `current_pattern`)
10. Usuário pode solicitar rediagnóstico manual após 30 missões via botão no perfil

**Mapeamento reação → diagnóstico (para a IA):**
- ❄️ fria → nenhum desejo ativado — resposta genérica ou ansiosa
- 💬 respondeu_mais → Conexão ativada — sem tensão ainda
- 🌀 ficou_curiosa → Curiosidade ativada — loop aberto funcionou
- ⚡ avancou → múltiplos desejos ativados — alta performance
- 👁️ visualizou_vacuo → Curiosidade falhou — não havia motivo para ela responder
- 👻 sumiu → Segurança ou Desejo quebrado — algo gerou desconforto

---

## ESTRUTURA DE COMPONENTES

**Componentes compartilhados (criar e reusar em todo o sistema):**
- `DesireBadge` — props: `desire: Desire, size?: 'sm'|'md'|'lg'`
- `PatternBadge` — props: `pattern: Pattern, size?: 'sm'|'md'|'lg'`
- `ProgressBar` — props: `value: number, label?: string, animated?: boolean`
- `MissionCard` — card da missão do dia
- `LessonCard` — card de lição com status

---

## INSTRUÇÃO FINAL AO LOVABLE

Gere o projeto completo seguindo todas as especificações acima.

**Prioridade de build:**
1. Auth (cadastro + login + Google OAuth)
2. Onboarding com diagnóstico (5 perguntas → padrão identificado → users_profile)
3. Dashboard com grid dos 4 desejos + card de missão + card simulador + card biblioteca
4. Trilha de Conexão como MVP de trilha (lições sequenciais)
5. Missão completa: briefing → registro → loading análise → resultado
6. Edge Function `analyze-mission` integrada na tela de registro
7. Simulador com A Fechada + A Provocadora no MVP (chat realtime + feedback)
8. Edge Function `simulator-response` integrada no chat
9. Biblioteca com filtros por desejo e modal de análise
10. Perfil com radar chart (Recharts) + histórico + stats

**Regras inegociáveis:**
- Zero lorem ipsum — use exatamente os textos de copy especificados
- Design system consistente em todas as telas (cores, badges, cards)
- DesireBadge com cores corretas em todo o sistema
- Mobile-first: bottom nav fixa, layout responsivo
- Guard de onboarding em todas as rotas protegidas
- RLS ativo — usuário nunca acessa dados de outro usuário
