# EXECUÇÃO: Dia 1 — ClickUp Foundation + Copy Setup

> **Tempo:** 3-4 horas  
> **Deliverable:** Workflow de Copy funcionando no ClickUp  
> **Status:** PRONTO PARA COMEÇAR HOJE

---

## Pré-requisitos (30 min antes de começar)

- [ ] Tenha à mão: API keys para ClickUp (vamos usar)
- [ ] Acesso a: docs/IMPLEMENTACAO-OPERACIONAL-COPY-TRAFFIC.md (referência)
- [ ] Bloco de tempo: 3-4h sem interrupções
- [ ] Café ☕

---

## PARTE 1: ClickUp Account + Workspace (30 min)

### Step 1.1: Criar Conta ClickUp

1. Vá para https://clickup.com
2. Clique "Sign Up"
3. Email: [seu email]
4. Senha: [crie uma forte]
5. Workspace name: **"[Seu Nome] - Infoproduto"**
   - Exemplo: "Gabriel - Infoproduto"
6. Clique "Create Workspace"

**Pronto?** ✓

---

### Step 1.2: Criar Space: Marketing

1. No ClickUp, clique **"+ Add Space"**
2. Nome: **"Marketing"**
3. Color: Blue (para visual)
4. Clique "Create"

**Pronto?** ✓

---

### Step 1.3: Criar Folder: Copy Production

1. Dentro de Marketing, clique **"+ Add Folder"**
2. Nome: **"Copy Production"**
3. Clique "Create"

**Pronto?** ✓

---

## PARTE 2: Criar Lists + Templates (45 min)

### Step 2.1: Criar as 4 Lists

Dentro de Copy Production, crie 4 listas:

**List 1: Copy Queue**
- [ ] Clique "+ Add List"
- [ ] Nome: "Copy Queue"
- [ ] View: Board (Kanban melhor para workflow)
- [ ] Color: Verde

**List 2: Copy In Progress**
- [ ] "+ Add List" → "Copy In Progress" → Board

**List 3: Copy Review**
- [ ] "+ Add List" → "Copy Review" → Board

**List 4: Copy Approved**
- [ ] "+ Add List" → "Copy Approved" → Board

**Pronto?** ✓

---

### Step 2.2: Criar Campos Customizados (Copy)

Estes campos vão funcionar em TODAS as tasks de copy.

Em Copy Production (Folder level), clique ⚙️ **Settings → Custom Fields**

Crie estes 12 campos:

**Campo 1: Tipo de Demanda**
```
Name: Tipo de Demanda
Type: Dropdown
Options:
  - vsl-copy
  - email-sequence
  - landing-page
  - video-script
  - ads-copy
  - sales-letter
Required: Yes
```

**Campo 2: Avatar**
```
Name: Avatar
Type: Dropdown
Options:
  - male-entrepreneur-35-50
  - female-coach-30-45
  - agency-owner-40-55
  - solopreneur-25-35
  - [custom]
Required: Yes
```

**Campo 3: Tema/Foco**
```
Name: Tema/Foco
Type: Text
Example: "high-ticket-closing"
Required: Yes
```

**Campo 4: Hook Identificado**
```
Name: Hook Identificado
Type: Checkbox
Required: Yes (to move to Approved)
```

**Campo 5: CTA Definido**
```
Name: CTA Definido
Type: Checkbox
Required: Yes
```

**Campo 6: Prova Social Presente**
```
Name: Prova Social Presente
Type: Checkbox
```

**Campo 7: Wordcount Estimado**
```
Name: Wordcount Estimado
Type: Number
Example: 1500
```

**Campo 8: CMO Approval**
```
Name: CMO Approval
Type: Dropdown
Options:
  - Pending
  - Approved
  - Rejected
Required: Yes (to move to Approved)
```

**Campo 9: Approved By**
```
Name: Approved By
Type: Person (auto-fill when approved)
```

**Campo 10: Rejection Reason**
```
Name: Rejection Reason
Type: Text
Shows: Only if CMO Approval = "Rejected"
```

**Campo 11: Versão**
```
Name: Versão
Type: Number
Default: 1
Auto-increment: +1 if rejected
```

**Campo 12: Status de Qualidade**
```
Name: Status de Qualidade
Type: Dropdown
Options:
  - Draft
  - Ready for CMO
  - Needs Revision
  - Approved
```

**Pronto?** ✓

---

### Step 2.3: Criar Template de Task (Copy)

Em Copy Queue:

1. Clique "+ Add Task"
2. Nome: **"[TEMPLATE] VSL Copy — {{Avatar}}"**
3. Preencha os campos que você criou
4. Clique "Save as Template"

Agora, sempre que criar uma task de copy, você clica "+ Add Task" → seleciona este template → preenche poucos campos e pronto.

**Pronto?** ✓

---

## PARTE 3: Criar Subtasks (30 min)

Em uma task de copy, você precisa de subtasks fixas.

### Step 3.1: Adicionar Subtasks à Task Template

1. Abra a task de copy
2. Vá para seção "Subtasks"
3. Clique "+ Add Subtask"

Crie estes 6 subtasks exatamente:

**Subtask 1:**
```
Name: 1. Avatar Analysis
Assignee: [seu nome]
Due: Today +4 hours
Description: Define 5 pillars (who, pain, desire, belief, objection)
```

**Subtask 2:**
```
Name: 2. Objection Research
Assignee: [seu nome]
Due: Today +6 hours
Description: Map 7+ main objections
```

**Subtask 3:**
```
Name: 3. Hook + Opening (60 sec)
Assignee: [seu nome]
Due: Tomorrow 10am
Description: First hook of VSL — must follow [Pattern] + [Disruption] + [Promise]
Custom approval: CMO review
```

**Subtask 4:**
```
Name: 4. Body + Objection Handlers
Assignee: [seu nome]
Due: Tomorrow 2pm
Description: Main content + handle objections with proof social
```

**Subtask 5:**
```
Name: 5. CTA + Encerramento
Assignee: [seu nome]
Due: Tomorrow 2pm
Description: Specific CTA (offer + price + deadline + risk-reversal)
```

**Subtask 6:**
```
Name: 6. CMO Final Approval
Assignee: [CMO name or "You"]
Due: Tomorrow 4pm
Description: CMO approves full copy before design
Custom field: "CMO Approval" must = "Approved"
```

**Pronto?** ✓

---

## PARTE 4: Automações ClickUp Nativas (30 min)

No ClickUp, automações nativas são **muito poderosas**. Vamos configurar 5.

### Step 4.1: Ir para Automations

1. Em Copy Production (Folder), clique ⚙️ **Settings**
2. Clique **"Automations"**
3. Clique **"Create Automation"**

---

### Automation 1: CMO Approval Gate

```
NAME: CMO Approval Gate

TRIGGER: Task created in "Copy Queue"

CONDITIONS:
- All of the following:
  * Custom field "CMO Approval" = "Pending"

ACTIONS:
- Assign task to: [CMO name]
- Change priority to: High
- Add comment: "@[CMO] Aguardando aprovação"

SAVE ✓
```

---

### Automation 2: Hook Checkbox Requirement

```
NAME: Hook Validated

TRIGGER: Subtask "Hook + Opening" marked complete

CONDITIONS:
- None (always run)

ACTIONS:
- Set custom field "Hook Identificado" → Checked

SAVE ✓
```

---

### Automation 3: CTA Checkbox Requirement

```
NAME: CTA Validated

TRIGGER: Subtask "CTA + Encerramento" marked complete

CONDITIONS:
- None

ACTIONS:
- Set custom field "CTA Definido" → Checked

SAVE ✓
```

---

### Automation 4: Block Approval Without Approval

```
NAME: Cannot Approve Without CMO

TRIGGER: Task moved to "Copy Approved" list

CONDITIONS:
- All of following:
  * Custom field "CMO Approval" ≠ "Approved"
  * OR custom field "Hook Identificado" = unchecked
  * OR custom field "CTA Definido" = unchecked

ACTIONS:
- Move task back to "Copy Review"
- Add comment: "⛔ Faltam validações antes de aprovar"
- Send notification to: [you]

SAVE ✓
```

---

### Automation 5: Version Increment on Rejection

```
NAME: Version Increment on Rejection

TRIGGER: Custom field "CMO Approval" changes to "Rejected"

CONDITIONS:
- None

ACTIONS:
- Increment custom field "Versão" by 1
- Set custom field "Status de Qualidade" → "Draft"
- Move task back to "Copy Queue"
- Add comment: "Revision round {{Versão}}"

SAVE ✓
```

**Pronto?** ✓

---

## PARTE 5: Test (30 min)

Agora vamos testar tudo junto.

### Step 5.1: Criar uma Task de Teste

1. Va para Copy Queue
2. Clique "+ Add Task"
3. Nome: **"[TEST] VSL Copy — male-entrepreneur-35-50"**
4. Preencha os campos:
   - Tipo: vsl-copy
   - Avatar: male-entrepreneur-35-50
   - Tema: high-ticket-closing
5. Clique "Create"

**Pronto?** ✓

### Step 5.2: Testar Subtasks + Automações

1. Abra a task
2. Clique no 1º subtask "Avatar Analysis"
3. Preencha rapidamente (fake data é OK):
   ```
   Who: Male 35-50, entrepreneur, >R$100k/mo
   Pain: Não consegue fechar deals de alto ticket
   Desire: Fechar +deals, ticket maior
   Belief: Precisa de método, não charisma
   Objection: "Isso só funciona para vendedor nato"
   ```
4. Marca done ✓
5. Vai para subtask 2 "Objection Research"
6. Lista 7+ objeções (fake):
   ```
   1. "Isso não funciona pra mim"
   2. "Já tentei vender em alto ticket, não consegui"
   3. ...
   ```
7. Marca done ✓

Veja a automação funcionar:
- O campo "Hook Identificado" apareceu?
- O CMO foi notificado?

**Pronto?** ✓

---

## PARTE 6: Documentação Rápida (15 min)

Crie um documento no ClickUp (ou nota) listando:

```
## Copy Production — Como Usar

Quando criar uma task de copy:
1. Copy Queue → + Add Task → Template
2. Preencha: Tipo, Avatar, Tema
3. Comece pelo subtask 1
4. Cada subtask tem veto específico
5. Quando todos completos, subtask 6 (CMO) aparece
6. CMO aprova? Task vai para "Copy Approved"
7. Automação cria task de Design

Alertas:
- ⚠️ Hook checkbox não marcado = não aprova
- ⚠️ CTA genérico = CMO rejeita
- ⚠️ Versão ≠ 1 = copy já foi revisada

KPIs to Track:
- % aprovadas de primeira
- Tempo avatar → aprovação final
- Número de revisões
```

**Pronto?** ✓

---

## CHECKLIST FINAL DIA 1

- [ ] ClickUp account criada
- [ ] Workspace "Infoproduto" criada
- [ ] Space "Marketing" criada
- [ ] Folder "Copy Production" criada
- [ ] 4 Lists criadas (Queue, In Progress, Review, Approved)
- [ ] 12 campos customizados criados
- [ ] 6 subtasks configurados
- [ ] 5 automações ativas
- [ ] 1 task de teste criada e testada
- [ ] Documentação rápida feita

**Tudo pronto?** ✅ **SIM → Avança para Dia 2**

---

## Dia 1: COMPLETO ✅

**Deliverable:** Copy Production workflow 100% operacional.

Próximo: Dia 2 — Paid Traffic Setup (3h)
