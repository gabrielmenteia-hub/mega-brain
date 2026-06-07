import json, os
from datetime import datetime

source_id = 'AN013'
today = datetime.now().isoformat()

insights = [
  {
    "id": f"{source_id}_INS001",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "IA-aplicada-negocios",
    "priority": "HIGH",
    "tag": "[FRAMEWORK]",
    "titulo": "Claude Code + AIOX: De zero a sistema completo em 1 mes",
    "insight": "Um criativo sem experiencia em programacao (Joao/Big) construiu CRM completo, site, automacoes WhatsApp, email marketing e sistema de governanca em ~1 mes usando Claude Code apos fazer imersao AIOX. Substituiu RD Station + Hubspot (~R$6.000/mes) por sistema proprio.",
    "confidence": 0.97,
    "chunks": [f"chunk_{source_id}_001", f"chunk_{source_id}_002", f"chunk_{source_id}_015"]
  },
  {
    "id": f"{source_id}_INS002",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "UGC-games-monetizacao",
    "priority": "HIGH",
    "tag": "[FRAMEWORK]",
    "titulo": "Modelo Publisher UGC no Fortnite: 40% do faturamento liquido distribuido por audiencia",
    "insight": "Fortnite distribui 40% do faturamento liquido proporcional a audiencia dos criadores. Uma experiencia pode gerar 600k+ em 1-2 meses com pico de 21.751 jogadores simultaneos. Level 8 estruturou-se como publisher (nao estudio) para escalar com 11 estudios parceiros.",
    "confidence": 0.95,
    "chunks": [f"chunk_{source_id}_025", f"chunk_{source_id}_026"]
  },
  {
    "id": f"{source_id}_INS003",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "IA-aplicada-negocios",
    "priority": "HIGH",
    "tag": "[HEURISTICA]",
    "titulo": "Identificar o ativo principal antes de escalar",
    "insight": "Joao identificou que o ativo real da Hero Base nao era o desenvolvimento de mapas, mas sim a midia e audiencia (Flakes + distribuicao). Isso levou a pivotagem de estudio para publisher. Regra: antes de escalar, entender qual e o ativo que atrai negocio.",
    "confidence": 0.92,
    "chunks": [f"chunk_{source_id}_028", f"chunk_{source_id}_029"]
  },
  {
    "id": f"{source_id}_INS004",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "automacao-IA",
    "priority": "HIGH",
    "tag": "[METODOLOGIA]",
    "titulo": "Stack de automacao com IA: CRM + WhatsApp + Email + Agendamento integrados",
    "insight": "Sistema construido inclui: CRM (substituto Hubspot/RD 6k/mes), integracao WhatsApp Business com roteamento inteligente por tipo de ticket, email marketing com IA, geracao de convites com IA, agendamento, governanca de acesso, orcamentos com margem, resumo de conversa via IA. Tudo em plataforma propria construida em 1 mes.",
    "confidence": 0.96,
    "chunks": [f"chunk_{source_id}_050", f"chunk_{source_id}_051"]
  },
  {
    "id": f"{source_id}_INS005",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "IA-aplicada-negocios",
    "priority": "HIGH",
    "tag": "[FILOSOFIA]",
    "titulo": "IA como tangibilizador: criativo executa o que antes precisava de dev",
    "insight": "Alan destaca que muitos tem acesso as ferramentas de IA mas ficam perdidos no como fazer. Joao exemplifica alguem que tangibilizou: usou Claude Code para criar coisas reais mesmo sem background tecnico. A imersao AIOX foi o desbloqueador. Nunca tinha criado site ou desenvolvido nada.",
    "confidence": 0.94,
    "chunks": [f"chunk_{source_id}_002", f"chunk_{source_id}_003"]
  },
  {
    "id": f"{source_id}_INS006",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "games-business",
    "priority": "MEDIUM",
    "tag": "[MODELO-MENTAL]",
    "titulo": "Modelo publisher vs estudio: escalar atraves de outros criadores",
    "insight": "Em vez de um estudio (publica mapa proprio), Level 8 tornou-se publisher: trouxe 11 microestudios com contratos de exclusividade ou sociedade (aporte + 50% da empresa). Multiplica capacidade de producao sem multiplicar custo fixo proporcionalmente.",
    "confidence": 0.91,
    "chunks": [f"chunk_{source_id}_030", f"chunk_{source_id}_031"]
  },
  {
    "id": f"{source_id}_INS007",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "automacao-IA",
    "priority": "MEDIUM",
    "tag": "[HEURISTICA]",
    "titulo": "WhatsApp comercial centralizado com roteamento inteligente",
    "insight": "Numero unico WhatsApp com roteamento por tipo de atendimento (high ticket vs tickets menores) elimina confusao de multiplos numeros. Sistema inclui: silencio automatico em horarios definidos (anti-ban), transferencia de conversa com contexto e resumo por IA.",
    "confidence": 0.93,
    "chunks": [f"chunk_{source_id}_055", f"chunk_{source_id}_056"]
  },
  {
    "id": f"{source_id}_INS008",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "games-business",
    "priority": "MEDIUM",
    "tag": "[FRAMEWORK]",
    "titulo": "Go Garden (Roblox): 598M minutos jogados e 600k+ em receita",
    "insight": "Experiencia no Roblox: 598 milhoes de minutos jogados, 500k+ favoritos, 600k+ em receita. Demonstra que modelo UGC funciona em multiplas plataformas alem do Fortnite.",
    "confidence": 0.90,
    "chunks": [f"chunk_{source_id}_032", f"chunk_{source_id}_033"]
  },
  {
    "id": f"{source_id}_INS009",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "games-business",
    "priority": "LOW",
    "tag": "[CONTEXTO]",
    "titulo": "Perfil Joao/Big: 10 anos em games, fundador Hero Base com Flakes",
    "insight": "Joao (Big/El Bigodon) tem ~10 anos em games, foi editor do Flakes (maior influenciador Fortnite da America Latina) antes de virar socio. Ajudou canais do zero: Tony Cat (3M), Manteiga (7M de 30k). Fundou Hero Base focada em Fortnite.",
    "confidence": 0.98,
    "chunks": [f"chunk_{source_id}_005", f"chunk_{source_id}_006"]
  },
  {
    "id": f"{source_id}_INS010",
    "source_id": source_id,
    "pessoa": "Alan Nicolas",
    "tema": "AIOX",
    "priority": "LOW",
    "tag": "[CONTEXTO]",
    "titulo": "AIOX como desbloqueador: Joao nao tinha Claude Code antes do evento",
    "insight": "Joao afirma que nao havia instalado Claude Code antes de ir ao AIOX. Apos a imersao, mudou completamente de abordagem. Contextualiza o impacto da imersao AIOX para iniciantes sem background tecnico.",
    "confidence": 0.95,
    "chunks": [f"chunk_{source_id}_003", f"chunk_{source_id}_004"]
  },
]

path = r'processing\insights\INSIGHTS-STATE.json'
os.makedirs(os.path.dirname(path), exist_ok=True)
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        state = json.load(f)
else:
    state = {"insights_state": {"persons": {}, "themes": {}, "version": "v1", "change_log": []}}

person_key = "Alan Nicolas"
if person_key not in state["insights_state"]["persons"]:
    state["insights_state"]["persons"][person_key] = []

state["insights_state"]["persons"][person_key] = [
    i for i in state["insights_state"]["persons"][person_key]
    if i.get("source_id") != source_id
]
state["insights_state"]["persons"][person_key].extend(insights)

for ins in insights:
    t = ins["tema"]
    if t not in state["insights_state"]["themes"]:
        state["insights_state"]["themes"][t] = []
    state["insights_state"]["themes"][t] = [
        i for i in state["insights_state"]["themes"][t]
        if not (i.get("source_id") == source_id and i.get("id") == ins["id"])
    ]
    state["insights_state"]["themes"][t].append(ins)

state["insights_state"]["change_log"].append({
    "date": today,
    "source_id": source_id,
    "action": "INSERT",
    "count": len(insights)
})

with open(path, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

high = sum(1 for i in insights if i["priority"] == "HIGH")
med = sum(1 for i in insights if i["priority"] == "MEDIUM")
low = sum(1 for i in insights if i["priority"] == "LOW")
print(f"Insights salvos: {len(insights)} | {high} HIGH | {med} MEDIUM | {low} LOW")
