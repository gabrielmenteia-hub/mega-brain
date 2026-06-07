# TECHNICAL ARCHITECTURE — Código Presença Magnética
> **Fase:** 4 | **Data:** 2026-04-02 | **Status:** Completo

---

## 1. Stack Supabase Completa

### Auth Providers
- Email/senha (provider nativo Supabase)
- Google OAuth — configurar em: Supabase Dashboard → Authentication → Providers → Google
- Redirect URL: `/auth/callback`

### Storage Buckets
- MVP não requer buckets — personas usam avatares gerados via CSS/emoji
- Bucket `avatars` pode ser adicionado pós-MVP para upload de foto de perfil do usuário

### Edge Functions

| Função | Trigger | Responsabilidade |
|--------|---------|-----------------|
| `analyze-mission` | HTTP POST | Recebe `mission_log_id`, lê o registro, chama GPT-4o-mini, grava `system_feedback`, `pattern_identified`, `desires_activated` e atualiza `desires_progress` |
| `generate-daily-mission` | Cron (meia-noite UTC-3) | Seleciona missão do dia baseada no desejo com menor `points` em `desires_progress` para cada usuário ativo |
| `simulator-response` | HTTP POST | Recebe mensagem do usuário + `persona_id` + histórico da sessão, retorna resposta da persona + `desires_activated` parcial |
| `on-user-created` | DB Webhook (INSERT em auth.users) | Cria linha em `users_profile` automaticamente após cadastro |

---

## 2. Mapeamento Funcionalidade → Recurso Supabase

| Funcionalidade | Tabelas | Edge Function | Auth | Realtime |
|---------------|---------|---------------|------|----------|
| Cadastro/Login | `users_profile` | `on-user-created` | Sim | — |
| Onboarding (diagnóstico) | `users_profile` | — | Sim | — |
| Dashboard | `desires_progress`, `mission_logs`, `users_profile` | — | Sim | — |
| Trilha de Desejo | `lessons`, `lesson_progress` | — | Sim | — |
| Missão do Dia | `missions`, `mission_logs` | `analyze-mission` | Sim | — |
| Simulador | `personas`, `user_personas`, `simulator_sessions` | `simulator-response` | Sim | Sim (chat) |
| Biblioteca | `conversations_library` | — | Sim | — |
| Perfil | `users_profile`, `desires_progress`, `mission_logs` | — | Sim | — |

---

## 3. Componentes Lovable por Funcionalidade

### Componentes Compartilhados (src/components/shared/)
- `DesireBadge` — badge com cor e ícone do desejo
  - Props: `desire: 'conexao' | 'seguranca' | 'desejo' | 'curiosidade'`
  - Cores: conexao=#1A237E/text #90CAF9 | seguranca=#1B5E20/text #A5D6A7 | desejo=#7F0000/text #EF9A9A | curiosidade=#4A148C/text #CE93D8
- `PatternBadge` — badge do padrão do usuário
  - Props: `pattern: 'ansioso' | 'neutro' | 'dominante'`
- `ProgressBar` — barra 0-100, cor accent dourado (#C9A84C)
  - Props: `value: number`, `label?: string`
- `MissionCard` — card da missão do dia com badge de desejo e CTA
- `LessonCard` — card de lição com tipo, título, duração e status (bloqueado/disponível/concluído)

### Por Tela

| Tela | Componentes específicos |
|------|------------------------|
| `/onboarding` | `DiagnosticQuestion`, `DiagnosticResult`, `StepProgress` |
| `/dashboard` | `DailyMissionCard`, `DesireGrid`, `SimulatorCard`, `LibraryCard` |
| `/trilha/:desejo` | `TrailHeader`, `LessonList`, `LessonContent`, `LessonNav` |
| `/simulador` | `PersonaSelector`, `PersonaCard`, `ChatInterface`, `ChatMessage`, `SimulatorFeedback`, `DesireActivationMap` |
| `/missao/:id` | `MissionBriefing`, `MissionForm`, `ReactionSelector`, `MissionAnalysis` |
| `/biblioteca` | `LibraryFilters`, `ConversationCard`, `ConversationModal` |
| `/perfil` | `RadarChart` (Recharts), `MissionHistory`, `StatsGrid` |

---

## 4. Estrutura de Arquivos

```
src/
├── pages/
│   ├── Login.tsx
│   ├── Cadastro.tsx
│   ├── Onboarding.tsx
│   ├── Dashboard.tsx
│   ├── Trilha.tsx          # /trilha/:desejo
│   ├── Simulador.tsx
│   ├── Missao.tsx          # /missao/:id
│   ├── Biblioteca.tsx
│   └── Perfil.tsx
├── components/
│   ├── shared/
│   │   ├── DesireBadge.tsx
│   │   ├── PatternBadge.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── MissionCard.tsx
│   │   └── LessonCard.tsx
│   ├── dashboard/
│   │   ├── DailyMissionCard.tsx
│   │   └── DesireGrid.tsx
│   ├── simulator/
│   │   ├── ChatInterface.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── PersonaSelector.tsx
│   │   ├── PersonaCard.tsx
│   │   ├── SimulatorFeedback.tsx
│   │   └── DesireActivationMap.tsx
│   ├── mission/
│   │   ├── MissionBriefing.tsx
│   │   ├── MissionForm.tsx
│   │   ├── ReactionSelector.tsx
│   │   └── MissionAnalysis.tsx
│   └── profile/
│       ├── RadarChart.tsx
│       ├── MissionHistory.tsx
│       └── StatsGrid.tsx
├── lib/
│   ├── supabase.ts         # client singleton
│   ├── desires.ts          # helpers de cálculo de progresso
│   └── missions.ts         # helpers de seleção e análise
├── hooks/
│   ├── useAuth.ts
│   ├── useDesires.ts
│   └── useMission.ts
└── types/
    └── index.ts            # interfaces TypeScript espelhando o schema

supabase/
└── functions/
    ├── analyze-mission/index.ts
    ├── generate-daily-mission/index.ts
    ├── simulator-response/index.ts
    └── on-user-created/index.ts
```

---

## 5. Constantes Globais

```typescript
// src/types/index.ts

export const DESIRES = ['conexao', 'seguranca', 'desejo', 'curiosidade'] as const
export type Desire = typeof DESIRES[number]

export const PATTERNS = ['ansioso', 'neutro', 'dominante'] as const
export type Pattern = typeof PATTERNS[number]

export const DESIRE_CONFIG: Record<Desire, { label: string; icon: string; bg: string; text: string }> = {
  conexao:    { label: 'Conexão',    icon: '🔗', bg: '#1A237E', text: '#90CAF9' },
  seguranca:  { label: 'Segurança',  icon: '🛡️', bg: '#1B5E20', text: '#A5D6A7' },
  desejo:     { label: 'Desejo',     icon: '🔥', bg: '#7F0000', text: '#EF9A9A' },
  curiosidade:{ label: 'Curiosidade',icon: '🌀', bg: '#4A148C', text: '#CE93D8' },
}
```

---

## 6. Fluxo de Análise de Missão (Edge Function)

```
POST /functions/v1/analyze-mission
Body: { mission_log_id: string }

1. Busca mission_log + mission (ferramenta, foco, dificuldade)
2. Monta prompt GPT-4o-mini com:
   - Ferramenta usada
   - O que o usuário disse (what_i_said)
   - Reação dela (her_reaction)
   - Notas do usuário (user_notes)
3. GPT retorna JSON: { desires_activated[], pattern_identified, system_feedback }
4. UPDATE mission_logs SET desires_activated, pattern_identified, system_feedback, status='analisada'
5. UPDATE desires_progress: +points para cada desejo ativado
6. RETURN { success: true, feedback: system_feedback }
```

---

## 7. Fluxo do Simulador (Edge Function)

```
POST /functions/v1/simulator-response
Body: { session_id: string, user_message: string }

1. Busca simulator_session + persona (profile_text, desire_tested)
2. Reconstrói histórico de mensagens do jsonb
3. Monta prompt com: persona profile + histórico + nova mensagem do usuário
4. GPT retorna: { response: string, desires_activated: Record<Desire, number> }
5. UPDATE simulator_sessions SET messages (append), desires_activated (merge)
6. RETURN { response, desires_activated }
```

---

**QG-05 — Stack técnica completa. Zero TBDs. Pronto para Fase 5 (UX Design detalhado).**
