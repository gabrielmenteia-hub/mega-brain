# COPY DOCUMENT — Código Presença Magnética
> **Fase:** 6.5 | **Data:** 2026-04-02 | **Status:** Completo

---

## 1. TOM DE VOZ

**3 diretrizes objetivas:**

1. **Direto e masculino** — frases curtas, sem rodeios, sem condescendência. O produto trata o usuário como adulto capaz. Nunca "você consegue!" — sempre "aqui está o que fazer."
2. **Técnico, não motivacional** — o copy explica mecanismos, não promete milagres. "Conexão ativa porque reduz a defesa dela" em vez de "desperte a mulher dos seus sonhos."
3. **Sem julgamento** — o usuário está aprendendo. Feedback negativo é diagnóstico, não crítica. "Você fechou o loop cedo" em vez de "você errou."

---

## 2. NOMENCLATURA OFICIAL

| Elemento | Nome oficial no produto |
|----------|------------------------|
| Os 4 desejos | "Os 4 Desejos Primitivos" |
| Padrão do usuário | "Padrão de Presença" |
| Exercício no mundo real | "Missão" |
| Conversa com IA | "Simulação" |
| Personagem IA | "Persona" |
| Aula/módulo | "Lição" |
| Conjunto de lições | "Trilha" |
| Conversas de exemplo | "Biblioteca" |
| Pontuação por desejo | "Calibração" |
| Sequência de dias ativos | "Sequência" |

---

## 3. COPY POR TELA

---

### S01 — Cadastro

```
Headline:     Comece agora.
Subtítulo:    Crie sua conta grátis.
Label email:  E-mail
Label senha:  Senha
Placeholder email:  seu@email.com
Placeholder senha:  Mínimo 8 caracteres
Botão primário:     Criar conta
Botão Google:       Continuar com Google
Link footer:        Já tem conta? Entrar
```

---

### S02 — Login

```
Headline:        Bem-vindo de volta.
Subtítulo:       [vazio — não precisa]
Botão primário:  Entrar
Link footer:     Não tem conta? Criar grátis
Link secundário: Esqueci minha senha
```

---

### S03 — Onboarding: Diagnóstico

```
Headline:   Primeiro, vamos entender onde você está.
Subtítulo:  5 perguntas. Diagnóstico real. Sem julgamento.
Progress:   "Pergunta [N] de 5"
Botão nav:  Próximo

--- PERGUNTAS ---

P1: Quando você está conversando com uma mulher que te atrai, você geralmente...
  A) Fico travado, não sei o que falar
  B) Respondo rápido demais tentando agradar
  C) Sou direto mas a conversa esfria rápido
  D) Consigo conversar mas não crio atração

P2: Quando ela demora para responder, você...
  A) Mando outra mensagem logo
  B) Fico ansioso mas espero
  C) Não ligo, continuo meu dia
  D) Mando algo engraçado para quebrar o gelo

P3: Qual é o seu maior obstáculo em conversas?
  A) Não sei como sair do "oi, tudo bem"
  B) A conversa morre depois de um tempo
  C) Ela some depois de um bom começo
  D) Não sei como criar tensão sem parecer grosseiro

P4: Como as mulheres geralmente te veem?
  A) Como amigo, nunca como interesse romântico
  B) Como legal, mas sem química
  C) Como intenso demais ou carente
  D) Bem, mas perco quando avanço

P5: O que você quer aprender primeiro?
  A) Como criar conexão real do zero
  B) Como gerar desejo sem parecer forçado
  C) Como ser misterioso e interessante
  D) Como transmitir segurança e presença

--- RESULTADO ---

Headline:   Seu Padrão Identificado

[ANSIOSO]
Descrição:  Você responde rápido, monitora o celular e interpreta silêncio como rejeição.
            Isso cria pressão — e ela sente.
            Sua jornada começa pela Segurança: aprenda a ocupar espaço sem precisar de validação.

[NEUTRO]
Descrição:  Você é legal, mas não gera magnetismo.
            As conversas são confortáveis e terminam ali.
            Sua jornada começa pelo Desejo: aprenda a criar tensão sem forçar.

[DOMINANTE]
Descrição:  Você tem presença, mas perde na execução.
            Avança cedo, fecha o loop antes da hora ou não calibra o que ela está sentindo.
            Sua jornada começa pela Conexão: aprenda a ler e ampliar o estado dela antes de avançar.

CTA:        Começar Minha Jornada
```

---

### S04 — Dashboard

```
Saudação:         Bom dia, [nome].
Subtítulo padrão: Dia [X] da sua jornada.
Subtítulo streak: Sequência: [N] dias 🔥

Banner streak em risco:
  "Sua sequência está em risco. Complete uma ação hoje para não perder [N] dias."

--- CARD MISSÃO DO DIA ---
Label:      MISSÃO DE HOJE
Subtítulo:  Sua missão de hoje ativa [Desejo]. Leva ~10 minutos no mundo real.
CTA:        Iniciar Missão

--- GRID DOS 4 DESEJOS ---
CTA (sem progresso): Começar
CTA (com progresso): Continuar

--- CARD SIMULADOR ---
Título:     Simulador de Conversa
Subtítulo:  Pratique com 5 perfis femininos diferentes antes de jogar de verdade.
CTA:        Iniciar Simulação

--- CARD BIBLIOTECA ---
Título:     Conversas Reais
Subtítulo:  [N] exemplos comentados. Veja o mecanismo funcionando na prática.
CTA:        Ver Biblioteca
```

---

### S05 — Trilha do Desejo

```
Header:     Trilha de [Desejo]
Progresso:  [X] de [Y] lições concluídas

Status lições:
  Disponível:  [título] — [N] min
  Concluída:   ✅ [título]
  Bloqueada:   🔒 [título] — Complete a anterior para desbloquear

Toast bloqueio: "Complete a lição anterior primeiro."

Banner conclusão: "Trilha completa. Você dominou [Desejo]."
```

---

### S06 — Lição

```
[Conteúdo vem do banco — campo `content` da tabela lessons]

Botão ativo:     Concluir Lição
Botão concluída: ✅ Concluída — Ver próxima
```

---

### S07 — Simulador: Seleção de Persona

```
Headline:   Com quem você vai praticar hoje?

--- PERSONAS (MVP) ---

1. A Fechada
   Descrição: Respostas curtas, pouca energia. Você vai precisar criar motivo para ela continuar.
   Desejo testado: 🛡️ Segurança
   CTA: Escolher

2. A Provocadora
   Descrição: Direta, irônica, testa seus limites. Se você recuar, ela vai embora.
   Desejo testado: 🔥 Desejo
   CTA: Escolher

3. A Ocupada
   Descrição: Sempre com pressa. Janela de atenção curta. Cada mensagem sua precisa justificar a próxima.
   Desejo testado: 🔗 Conexão
   CTA bloqueado: 🔒 Complete 5 missões para desbloquear

4. A Emocional
   Descrição: Humor instável. O que funciona hoje pode não funcionar amanhã.
   Desejo testado: 🔗 Conexão + 🛡️ Segurança
   CTA bloqueado: 🔒 Complete 10 missões para desbloquear

5. A Independente
   Descrição: Não precisa de você. Não vai fingir interesse. Você tem que criar curiosidade do zero.
   Desejo testado: 🌀 Curiosidade
   CTA bloqueado: 🔒 Complete 15 missões para desbloquear
```

---

### S08 — Simulador: Chat

```
Header:           [Nome da Persona]
Indicador:        Desejos ativados: [badges] ou "—"
Placeholder input: Escreva sua mensagem...
Botão encerrar:   Encerrar

Typing indicator: "[Nome] está digitando..."

Modal confirmação encerrar:
  Título:   Encerrar simulação?
  Subtítulo: Você vai receber o feedback da conversa até aqui.
  Confirmar: Encerrar e ver resultado
  Cancelar:  Continuar praticando
```

---

### S09 — Simulador: Feedback

```
Headline:   Resultado da Simulação
Subtítulo:  Com [Nome da Persona]

Seção desejos:      Desejos Ativados
[Se nenhum]:        Nenhum desejo ativado nesta conversa.

Seção positivo:     O que funcionou
Seção negativo:     O que travou
Seção sugestão:     1 ajuste para a próxima vez

Feedback positivo (exemplos):
  "Você ativou Curiosidade. Ela não vai parar de pensar nisso."
  "Você criou tensão sem forçar. Segurança ativada."
  "Seu timing foi preciso. Loop aberto funcionou."

Feedback negativo (exemplos):
  "Você fechou o loop cedo demais. Ela não teve motivo pra voltar."
  "Você recuou quando ela testou. Desejo quebrado."
  "Você respondeu rápido demais. Criou pressão, não atração."

Feedback vácuo:
  "Ela leu. Ela escolheu não responder. Você não criou o motivo certo."

CTA primário:     Registrar como Missão Real
CTA secundário:   Praticar Novamente
```

---

### S10 — Missão: Briefing

```
Label dificuldade:
  iniciante     → INICIANTE
  intermediario → INTERMEDIÁRIO
  avancado      → AVANÇADO

Seção ferramenta:   A Ferramenta de Hoje
Seção exemplo:      Na prática:

CTA inicial:   Fui! Vou tentar agora

Card pós-clique:
  Título:   Agora vá ao mundo real.
  Texto:    Aplique a ferramenta em uma conversa real. Volte aqui para registrar o resultado.
  CTA:      Registrar Resultado
```

---

### S11 — Missão: Registro

```
Headline:   Como foi?

Label textarea obrigatória:  O que você disse ou mandou?
Placeholder:                 Ex: "Perguntei sobre o projeto dela e deixei uma pergunta aberta no final."

Headline reações:   A reação dela:
Reações:
  ❄️  Ficou fria
  💬  Respondeu mais
  🌀  Ficou curiosa
  ⚡  Avançamos
  👁️  Visualizou e não respondeu
  👻  Sumiu

Label textarea opcional:  O que você acha que funcionou ou travou?
Placeholder:              Opcional. Sua análise melhora o diagnóstico.

CTA:   Enviar para Análise

Tela de loading:
  Texto:  Analisando sua missão...
  Sub:    Isso leva alguns segundos.
```

---

### S12 — Missão: Análise

```
Headline:   Diagnóstico da Missão

Seção desejos:    Desejos Ativados
[Se nenhum]:      Nenhum desejo ativado. Veja o ajuste sugerido abaixo.

Seção padrão:     Padrão Identificado
Seção ajuste:     Ajuste para a Próxima

Label progresso:  Sua Calibração Atual

CTA:   Voltar ao Dashboard

Loading (acesso direto):
  Texto: Carregando diagnóstico...

Análise em processamento:
  Texto: Sua análise está sendo preparada...
  Sub:   Atualizando em instantes.
```

---

### S13 — Biblioteca

```
Headline:   Conversas Reais
Subtítulo:  Veja o mecanismo funcionando na prática.

Filtro tabs:    Todos | 🔗 Conexão | 🛡️ Segurança | 🔥 Desejo | 🌀 Curiosidade
Dropdown:       Persona: Todas ▾

CTA card:   Ver Análise Completa

Modal:
  Título:   Análise da Conversa
  Fechar:   ✕

Empty state (filtro): "Nenhuma conversa encontrada para esse filtro."
Empty state (vazio):  "Nenhuma conversa na biblioteca ainda. Em breve."
```

---

### S14 — Perfil

```
Seção radar:      Sua Calibração
Seção stats:      Em Números

Labels stats:
  Total de missões:  Missões realizadas
  Streak:            Sequência atual
  Mais forte:        Desejo mais forte
  Mais fraco:        Desejo mais fraco

Seção histórico:  Histórico de Missões
Paginação:        Ver mais missões

CTA rediagnóstico (após 30 missões):
  Texto:   Refazer Diagnóstico
  Sub:     Disponível após 30 missões. Seu padrão pode ter mudado.

Empty state missões: "Nenhuma missão registrada ainda. A teoria sem prática não muda nada."
```

---

## 4. MICROCOPY CRÍTICOS (TOP 10)

| # | Contexto | Texto |
|---|----------|-------|
| 1 | Email já cadastrado | "Esse e-mail já está em uso. Entrar?" |
| 2 | Senha incorreta | "E-mail ou senha incorretos." |
| 3 | Sessão expirada | "Sua sessão expirou. Entre novamente." |
| 4 | Erro de rede (simulador) | "Falha ao enviar. Verifique sua conexão e tente novamente." |
| 5 | Lição bloqueada (toast) | "Complete a lição anterior primeiro." |
| 6 | Missão sem registro após 24h | "Você iniciou essa missão mas não registrou o resultado. O que aconteceu?" |
| 7 | Reação não selecionada (validação) | "Selecione a reação antes de enviar." |
| 8 | Análise em processamento | "Sua análise está sendo preparada. Atualizando em instantes." |
| 9 | Persona bloqueada (tooltip) | "Complete [N] missões para desbloquear [Nome]." |
| 10 | Streak zerado | "Sua sequência foi resetada. Recomece hoje." |

---

## 5. EMAILS TRANSACIONAIS

### Boas-vindas (após cadastro)
```
Assunto:  Seu Código foi ativado.
Corpo:
  [Nome],

  Seu diagnóstico está pronto.

  Você identificou seu Padrão de Presença.
  Agora começa a parte real: missões no mundo real, simulações, calibração.

  Acesse seu painel:
  [Botão: Acessar agora]

  — Código Presença Magnética
```

### Lembrete de streak em risco (após 20h sem atividade)
```
Assunto:  Sua sequência de [N] dias está em risco.
Corpo:
  [Nome],

  Você tem [N] dias consecutivos.
  Faltam 4 horas para a sequência ser resetada.

  Complete uma ação agora — lição, simulação ou missão.

  [Botão: Acessar agora]
```

---

**QG-07 — Copy completo. Zero lorem ipsum. Todas as 14 telas com texto real. Pronto para Fase 7 (Lovable Master Prompt final).**
