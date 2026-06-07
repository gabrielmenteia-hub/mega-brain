# SCREEN MAP + DETAILED SPEC — Código Presença Magnética
> **Fases:** 5 + 6 | **Data:** 2026-04-02 | **Status:** Completo

---

## ARQUITETURA DE NAVEGAÇÃO

- **Layout:** Mobile-first, bottom navigation fixa
- **Bottom nav (rotas protegidas):** 🏠 Dashboard | 🎯 Missão | 💬 Simulador | 📚 Biblioteca | 👤 Perfil
- **Rotas públicas:** /login, /cadastro, /onboarding (sem nav)
- **Breadcrumb:** apenas em trilha → `Trilha / Conexão / Lição 3`
- **Guard:** qualquer rota protegida sem onboarding_done=true → redirect /onboarding

---

## TELAS

---

### S01 — /cadastro — Cadastro

**Layout:**
- Logo centrado no topo
- Card central: título "Comece agora.", subtítulo "Crie sua conta grátis."
- Campo: email (type=email, placeholder="seu@email.com")
- Campo: senha (type=password, placeholder="Mínimo 8 caracteres", toggle mostrar/ocultar)
- Botão primário: "Criar conta" (full-width, dourado)
- Divisor: "ou"
- Botão Google OAuth: "Continuar com Google" (outline, full-width)
- Link footer: "Já tem conta? Entrar"

**Estados:**
- Default: campos vazios, botão desabilitado
- Loading: botão com spinner, campos bloqueados
- Erro validação: borda vermelha no campo + mensagem inline abaixo
- Erro server: toast vermelho no topo ("Esse e-mail já está em uso.")
- Sucesso: redirect automático → /onboarding

**Validações visíveis:**
- Email: formato inválido → "E-mail inválido"
- Senha: < 8 chars → "Mínimo 8 caracteres"
- Botão habilitado apenas com email válido + senha ≥ 8 chars

**Interações:**
- Submit → chama Supabase Auth signUp → trigger on-user-created → redirect /onboarding
- Google OAuth → popup Google → callback /auth/callback → redirect /onboarding

---

### S02 — /login — Login

**Layout:** idêntico ao S01 com:
- Título: "Bem-vindo de volta."
- Sem campo de confirmação de senha
- Botão: "Entrar"
- Link footer: "Não tem conta? Criar grátis"
- Link secundário: "Esqueci minha senha" (abaixo do botão)

**Estados:**
- Erro credenciais: toast vermelho "E-mail ou senha incorretos."
- Sucesso: redirect → /dashboard (se onboarding_done) ou /onboarding

---

### S03 — /onboarding — Diagnóstico

**Layout:**
- Progress bar no topo (steps 1-5, preenchimento dourado)
- Passo atual em texto: "Pergunta 2 de 5"
- Card central: pergunta em texto grande (font-size 20px, weight 700)
- 4 botões de resposta full-width, fundo #1A1A1A, borda sutil
  - Estado selecionado: borda dourada (#C9A84C), background leve
- Botão "Próximo" → ativo somente após seleção, posição fixa no rodapé

**Tela de resultado (passo 6):**
- Título: "Seu Padrão Identificado"
- Badge grande centralizado: ANSIOSO | NEUTRO | DOMINANTE
  - ANSIOSO: vermelho escuro | NEUTRO: cinza | DOMINANTE: dourado
- 3 linhas descrevendo o padrão (texto pré-definido por padrão)
- Botão: "Começar Minha Jornada" → redirect /dashboard

**Estados:**
- Loading no submit do passo 5: spinner no botão, salva padrão em users_profile

**Lógica de cálculo do padrão:**
- Maioria de respostas ansiosas (opções A/B) → ANSIOSO
- Maioria neutras (opções B/C misturadas) → NEUTRO
- Maioria dominantes (opções C/D) → DOMINANTE

---

### S04 — /dashboard — Dashboard Principal

**Layout (mobile, scroll vertical):**

1. **Header** (não-fixed, dentro do scroll)
   - Linha 1: "Bom dia, [nome]." (h1, dourado)
   - Linha 2: "Dia X da sua jornada" OU "Sequência: N dias 🔥"
   - PatternBadge (canto direito, tamanho sm)

2. **Card Missão do Dia** (full-width, gradient sutil dourado nas bordas)
   - Badge "MISSÃO DE HOJE" (label uppercase, vermelho escuro)
   - Título da missão (h2)
   - DesireBadge do foco
   - Tempo estimado: "~10 minutos no mundo real"
   - Botão: "Iniciar Missão" → /missao/:id

3. **Grid dos 4 Desejos** (2 colunas, 2 linhas)
   - Cada card: DesireBadge + nome + ProgressBar + "X lições concluídas"
   - CTA: "Continuar" (se iniciado) ou "Começar" (se points=0)
   - Click → /trilha/:desejo

4. **Card Simulador**
   - Título + subtítulo + botão "Iniciar Simulação" → /simulador

5. **Card Biblioteca**
   - Título + "N exemplos comentados" + botão "Ver Biblioteca" → /biblioteca

**Estados:**
- Loading inicial: skeleton loaders em todos os cards
- Missão do dia ausente (edge case): card alternativo "Nenhuma missão gerada ainda. Tente amanhã."
- Streak em risco (streak_at_risk=true): banner topo laranja "Sua sequência está em risco! Complete uma ação hoje."

---

### S05 — /trilha/:desejo — Trilha do Desejo

**Layout:**
- Header: DesireBadge grande + nome do desejo + ProgressBar da trilha completa (X de Y lições)
- Lista vertical de lições (LessonCard por item):
  - Ícone do tipo: 📖 teoria | 💬 exemplo | ⚡ exercício
  - Título + duração em minutos
  - Status: 🔒 bloqueado (cinza) | disponível (normal) | ✅ concluído (check dourado)
  - Lição ativa: borda dourada, ligeiramente expandida
- Lições bloqueadas: não clicáveis, cursor not-allowed, opacity 0.5

**Estados:**
- Loading: skeleton list
- Trilha concluída: banner "Trilha completa! Você dominou [Desejo]." com confetti sutil

**Interações:**
- Click em lição disponível → /trilha/:desejo/:licao
- Click em lição bloqueada → toast "Complete a lição anterior primeiro."

---

### S06 — /trilha/:desejo/:licao — Lição

**Layout:**
- Breadcrumb: "Trilha / [Desejo] / [Título]"
- Badge do tipo (teoria/exemplo/exercício) + DesireBadge
- Título h1
- Conteúdo completo (markdown renderizado, linha de 65ch máxima)
- Barra de progresso de leitura (fixed top, 2px, dourada)
- Botão fixo no rodapé: "Concluir Lição" → marca status='concluida', redirect S05

**Estados:**
- Já concluída: botão substituído por "✅ Concluída — Ver próxima"
- Loading ao concluir: spinner no botão

**Micro-interação:** ao clicar "Concluir Lição", animação de check dourado expandindo antes de redirecionar (300ms).

---

### S07 — /simulador — Simulador: Seleção de Persona

**Layout:**
- Título: "Com quem você vai praticar hoje?"
- Lista de 5 PersonaCards:
  - Avatar (emoji grande ou inicial em círculo colorido)
  - Nome + descrição 2 linhas
  - DesireBadge do desejo testado
  - Botão "Escolher" (ativo) ou "🔒 Desbloqueie com 5 missões" (bloqueado)

**MVP personas (2 desbloqueadas por default):**
1. **A Fechada** — testa Segurança — desbloqueada
2. **A Provocadora** — testa Desejo — desbloqueada
3. **A Ocupada** — testa Conexão — bloqueia após 5 missões
4. **A Emocional** — testa Conexão+Segurança — bloqueia após 10 missões
5. **A Independente** — testa Curiosidade — bloqueia após 15 missões

**Estados:**
- Loading: skeleton cards
- Nenhuma sessão anterior: mostrar todas as personas com status correto
- Persona bloqueada: card com overlay escuro + ícone 🔒 + tooltip "X missões para desbloquear"

---

### S08 — /simulador/:sessao — Simulador: Chat

**Layout:**
- Header fixo: nome da persona + DesireBadge do contexto + botão "Encerrar"
- Indicador discreto abaixo do header: "Desejos ativados: [badges ativos ou —]"
- Área de mensagens (scroll):
  - Mensagem dela: alinhada esquerda, bg #2A2A2A, border-radius 12px 12px 12px 0
  - Mensagem do usuário: alinhada direita, bg dourado baixa opacidade (#C9A84C22), border-radius 12px 12px 0 12px
  - Timestamp discreto abaixo de cada mensagem
- Input fixo no rodapé: textarea (max 3 linhas, auto-grow) + botão enviar (seta dourada)
- Primeira mensagem vem da persona (gerada pela Edge Function no início da sessão)

**Estados:**
- Loading (aguardando resposta da persona): indicador "digitando..." animado (3 pontos pulsando)
- Erro de rede: toast "Falha ao enviar. Tente novamente." + botão retry
- Sessão encerrada: redirect automático → S09

**Interações:**
- Enviar mensagem → POST /functions/v1/simulator-response → append mensagem + resposta no JSONB
- Botão "Encerrar" → modal confirmação "Encerrar simulação?" → confirmar → atualiza status='concluida' → S09

---

### S09 — /simulador/:sessao/feedback — Simulador: Feedback

**Layout:**
- Título: "Resultado da Simulação"
- Subtítulo: "Com [Nome da Persona]"
- **Mapa dos 4 desejos:** 4 cards em grid 2x2, cada um com DesireBadge + barra de % ativação (0-100%)
- Seção "O que funcionou": lista com ícone ✅ (máx 3 itens)
- Seção "O que travou": lista com ícone ⚠️ (máx 2 itens)
- Sugestão cirúrgica: card destacado "1 ajuste para a próxima vez" (texto específico da IA)
- 2 CTAs:
  - "Registrar como Missão Real" → cria mission_log com dados da sessão → S11
  - "Praticar Novamente" → cria nova sessão com mesma persona → S08

---

### S10 — /missao/:id — Missão: Briefing

**Layout:**
- DesireBadge do foco + badge de dificuldade (iniciante/intermediário/avançado)
- Título h1 + descrição da missão (2-3 linhas)
- Seção "A Ferramenta de Hoje":
  - Nome da ferramenta (h2, dourado)
  - Explicação (parágrafo)
  - Exemplo prático em card destacado (fundo #1A1A1A, borda esquerda dourada 3px)
- Botão fixo rodapé: "Fui! Vou tentar agora" → atualiza status='executando' → permanece na tela
  - Após clique: botão some, aparece card "Agora vá ao mundo real. Volte aqui para registrar o resultado." + botão "Registrar Resultado" → S11

**Estados:**
- Missão já executando: pula diretamente para o card de registro
- Missão já analisada: redireciona para S12

---

### S11 — /missao/:id/registro — Missão: Registro

**Layout:**
- Título: "Como foi?"
- Textarea: "O que você disse ou mandou?" (obrigatório, placeholder com exemplo curto)
- Seção "A reação dela:" — 6 botões grandes full-width (seleção única):
  - ❄️ Ficou fria
  - 💬 Respondeu mais
  - 🌀 Ficou curiosa
  - ⚡ Avançamos
  - 👁️ Visualizou e não respondeu
  - 👻 Sumiu
  - Estado selecionado: borda dourada, check no canto
- Textarea opcional: "O que você acha que funcionou ou travou?" (placeholder "Opcional. Sua análise melhora o diagnóstico.")
- Botão fixo rodapé: "Enviar para Análise" → POST /functions/v1/analyze-mission → loading state → S12

**Estados:**
- Botão desabilitado até: textarea obrigatória preenchida + reação selecionada
- Loading (aguardando IA): tela de loading intermediária "Analisando sua missão..." com spinner dourado (2-4s)

---

### S12 — /missao/:id/analise — Missão: Análise

**Layout:**
- Título: "Diagnóstico da Missão"
- Seção "Desejos ativados": badges dos desejos ativados (ou "Nenhum ativado" em cinza)
- Seção "Padrão identificado": 1 parágrafo do system_feedback
- Seção "Ajuste sugerido": card destacado com 1 recomendação específica
- ProgressBar por desejo (atualizada com novos pontos)
- Botão: "Voltar ao Dashboard" → S04

**Estados:**
- Loading (caso acesse direto): busca dados da análise, mostra skeleton
- Análise ainda em processamento: "Sua análise está sendo preparada..." + auto-refresh a cada 3s

---

### S13 — /biblioteca — Biblioteca

**Layout:**
- Filtros no topo:
  - Tabs por desejo: Todos | 🔗 Conexão | 🛡️ Segurança | 🔥 Desejo | 🌀 Curiosidade
  - Dropdown: "Persona: Todas ▾"
- Grid de ConversationCards (1 coluna mobile):
  - DesireBadge + badge da persona (nome, cor neutra)
  - Situação (1 linha, negrito)
  - Preview: 3-4 mensagens alternadas (compactas, sem timestamps)
  - Botão: "Ver Análise Completa"
- Modal ao clicar "Ver Análise":
  - Conversa completa com timestamps
  - Análise linha a linha (formato: mensagem → comentário em itálico dourado)
  - Botão fechar

**Estados:**
- Loading: skeleton cards
- Empty state (filtro sem resultado): "Nenhuma conversa encontrada para esse filtro." (ícone + texto)
- Biblioteca vazia: "Nenhuma conversa na biblioteca ainda. Em breve."

---

### S14 — /perfil — Perfil

**Layout:**
- Header: nome + PatternBadge (tamanho lg)
- **Radar Chart** (Recharts, 4 eixos = 4 desejos, 0-100):
  - Fundo transparente, linhas #333, área preenchida com dourado baixa opacidade
  - Labels com DesireBadge miniatura
- **Estatísticas** (grid 3 colunas):
  - Total de missões realizadas
  - Streak atual (dias)
  - Desejo mais forte (badge) | Desejo mais fraco (badge)
- **Histórico de Missões** (lista, últimas 20):
  - Data | Título | DesireBadge | badge de reação (ex: ⚡ Avançamos) | badge do padrão identificado
  - Clicável → modal com análise completa da missão
- **CTA inferior** (visível após 30 missões): "Refazer Diagnóstico" (outline, não chamativo)

**Estados:**
- Loading: skeleton
- Sem missões: "Nenhuma missão registrada ainda. A teoria sem prática não muda nada."
- Histórico com paginação: "Ver mais" ao atingir 20 itens exibidos

---

## 5 MICRO-INTERAÇÕES CRÍTICAS

1. **Seleção de resposta no onboarding:** ao clicar, botão escala 1.02 + borda dourada aparece em 150ms → botão "Próximo" anima entrada (fade-in)
2. **Conclusão de lição:** ícone de check dourado pulsa e expande (escala 1→1.5→1) em 300ms antes do redirect
3. **Envio de mensagem no simulador:** mensagem do usuário aparece instantaneamente (otimistic UI), depois "digitando..." da persona em 500ms
4. **Seleção de reação na missão:** botão selecionado recebe borda dourada + ícone ✓ no canto superior direito com transição 200ms
5. **Atualização de progresso pós-análise:** ProgressBar dos desejos anima de valor anterior para novo valor (transição 800ms, ease-out) ao entrar na tela S12

---

**QG-06 — Screen Map completo. Todas as 14 telas nomeadas, detalhadas e com estados mapeados. Pronto para Fase 6.5 (Copy completo).**
