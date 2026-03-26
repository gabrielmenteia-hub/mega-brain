"""
Insight extraction: V4 Looking Ahead 2026 - Dia 1
Speakers: Dener Lippert, Rami Goldratt, Thiago Nigro, Andre Kliousoff
"""
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INSIGHTS_PATH = BASE_DIR / "processing" / "insights" / "INSIGHTS-STATE.json"
SOURCE_ID = "V4C001"
TODAY = "2026-03-07"

with open(INSIGHTS_PATH, encoding="utf-8") as f:
    state = json.load(f)

persons = state.setdefault("insights_state", {}).setdefault("persons", {})

# ─── DENER LIPPERT ────────────────────────────────────────────────────────────
DL_INSIGHTS = [
    {
        "id": "V4C001_DL_001",
        "insight": "[FILOSOFIA] Toda empresa e uma fabrica de receita — nao de produtos, servicos ou software. A receita nasce de um fluxo continuo: aquisicao, engajamento, monetizacao e retencao. Quando essas etapas nao evoluem juntas, o crescimento desacelera drasticamente.",
        "tags": ["filosofia", "receita", "crescimento", "fluxo"],
        "priority": "HIGH",
        "confidence": 0.95,
        "chunks": ["chunk_V4C001_001", "chunk_V4C001_002"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_DL_002",
        "insight": "[FILOSOFIA] Inercia nao e simplesmente parar — e nao evoluir. E manter a mesma velocidade quando o contexto exige mais. No mundo dos negocios, crescer nao e opcao, e questao de sobrevivencia.",
        "tags": ["inercia", "crescimento", "filosofia"],
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_V4C001_003"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_DL_003",
        "insight": "[MODELO-MENTAL] Empresas que crescem tornam-se transatlanticos — dificeis de virar, dificeis de parar. O Brasil e um mar revolto; empresas menores sao barcos a deriva. Escalar e a melhor defesa contra crises.",
        "tags": ["escala", "resiliencia", "brasil", "crescimento"],
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_V4C001_004"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_DL_004",
        "insight": "[HEURISTICA] Campanha Bilion Sellers: sistema de pontuacao por CANAIS (nao so midia paga). Canais: indicacao de cliente ativo, reativacao de ex-cliente, outbound, midia. Meta: R$1 bilhao. Estrutura: 4 sprints por quarter com premios em dinheiro.",
        "tags": ["vendas", "canais", "outbound", "indicacao", "campanha"],
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_V4C001_200", "chunk_V4C001_201"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_DL_005",
        "insight": "[HEURISTICA] Crescimento infinito por indicacao: se eu tenho mais clientes sendo indicados do que aquilo que perco, eu tenho um crescimento infinito. Nao importa o delta tempo — o que importa e ter o costume de trazer mais clientes do que perder.",
        "tags": ["indicacao", "retencao", "crescimento", "referral"],
        "priority": "HIGH",
        "confidence": 0.94,
        "chunks": ["chunk_V4C001_198"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_DL_006",
        "insight": "[FRAMEWORK] V4 Company: empresa de marketing com mais de 13 anos ajudando empresas a mapear restricoes e evoluir com responsabilidade. Produto: crescimento de receita via marketing digital com rastreabilidade total (dado, nao palpite).",
        "tags": ["v4", "marketing", "dados", "restricoes"],
        "priority": "MEDIUM",
        "confidence": 0.88,
        "chunks": ["chunk_V4C001_005"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_DL_007",
        "insight": "[METODOLOGIA] Sistema Marklab da V4: plataforma que conecta todos os dados de marketing. Quem atende ve o que importa. Toda acao registrada: quem fez, quando fez, o que gerou. Visivel para o cliente, gerenciado por dado.",
        "tags": ["crm", "dados", "tecnologia", "marketing", "rastreabilidade"],
        "priority": "MEDIUM",
        "confidence": 0.87,
        "chunks": ["chunk_V4C001_125"],
        "source_id": SOURCE_ID,
    },
]

# ─── RAMI GOLDRATT ────────────────────────────────────────────────────────────
RG_INSIGHTS = [
    {
        "id": "V4C001_RG_001",
        "insight": "[FRAMEWORK] 5 Passos do TOC (Theory of Constraints): 1. Identificar a restricao verdadeira — o que esta limitando o sistema agora. 2. Explorar — extrair o maximo dessa restricao. 3. Subordinar — alinhar toda a organizacao para extrair mais. 4. Elevar — investir para aumentar a capacidade da restricao. 5. Evitar inercia — a restricao pode mudar, preparar-se para a proxima.",
        "tags": ["TOC", "restricoes", "framework", "gestao", "Goldratt"],
        "priority": "HIGH",
        "confidence": 0.96,
        "chunks": ["chunk_V4C001_160", "chunk_V4C001_161"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_RG_002",
        "insight": "[HEURISTICA] 'Extrair o maximo do suco de um limao antes de comprar mais limoes.' Primeiro explorar a restricao existente ao maximo antes de investir em elevar (comprar mais recursos). Se fosse facil adicionar recursos, voce ja teria feito.",
        "tags": ["restricoes", "eficiencia", "recursos", "heuristica"],
        "priority": "HIGH",
        "confidence": 0.95,
        "chunks": ["chunk_V4C001_162"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_RG_003",
        "insight": "[FILOSOFIA] Inercia cognitiva: continuamos aplicando as mesmas taticas mesmo sabendo que precisamos mudar. Nao somos cegos — sabemos do problema. Mas acreditamos que e o melhor que podemos fazer, entao nunca tentamos algo diferente. Apenas uma crise nos forca a mudar.",
        "tags": ["inercia", "mudanca", "comportamento", "filosofia"],
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_V4C001_163"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_RG_004",
        "insight": "[MODELO-MENTAL] 'Bom senso infelizmente nao e tao comum.' — Mark Twain. O fator limitante e obvio mas raramente focamos nele. A maioria das melhorias sao feitas onde e mais facil ou conveniente, nao onde a restricao real esta.",
        "tags": ["bom-senso", "restricoes", "foco", "modelo-mental"],
        "priority": "MEDIUM",
        "confidence": 0.90,
        "chunks": ["chunk_V4C001_165"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_RG_005",
        "insight": "[METODOLOGIA] Case de empresa japonesa de casas pre-fabricadas: mercado encolhendo (populacao diminuindo), oceano vermelho. Solucao via TOC: identificar que a restricao nao era o mercado externo mas um processo interno. Ao elevar a restricao certa, cresceram enquanto concorrentes encolhiam.",
        "tags": ["case", "TOC", "oceano-vermelho", "restricoes", "japao"],
        "priority": "MEDIUM",
        "confidence": 0.88,
        "chunks": ["chunk_V4C001_168"],
        "source_id": SOURCE_ID,
    },
]

# ─── THIAGO NIGRO ─────────────────────────────────────────────────────────────
TN_INSIGHTS = [
    {
        "id": "V4C001_TN_001",
        "insight": "[FILOSOFIA] Acesso e a maior bencao que a fama trouxe. O acesso muda sua direcao, acelera seu processo, te da caminhos diferentes. Voce deveria brigar na sua vida para ter acesso. Nao compre ferramentas — compre acesso.",
        "tags": ["acesso", "mentoria", "networking", "filosofia"],
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_V4C001_060"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_TN_002",
        "insight": "[MODELO-MENTAL] A pergunta certa nao e 'como resolvo esse problema' ou 'o que faco para resolver'. A pergunta certa e 'quem pode resolver para mim?'. Essa e a cabeca que vai te levar pro proximo nivel.",
        "tags": ["delegacao", "lideranca", "modelo-mental", "outsourcing"],
        "priority": "HIGH",
        "confidence": 0.95,
        "chunks": ["chunk_V4C001_062"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_TN_003",
        "insight": "[HEURISTICA] Grit (garra) e o fator comum entre pessoas bem-sucedidas — Jorge Paulo Lemann. Grit nao esta no curriculo. E algo que voce ve em campo, em situacoes adversas. A selecao brasileira de volei, os grandes executivos — todos tem grit em comum.",
        "tags": ["grit", "garra", "contratacao", "lideranca", "Lemann"],
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_V4C001_065"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_TN_004",
        "insight": "[HEURISTICA] 1% do Brasil = 2.2 milhoes de pessoas — suficiente para ganhar muito dinheiro em qualquer nicho. Voce nao precisa agradar todo mundo. Faca o conteudo que voce mesmo gostaria de ver, pensado nos seus 1%.",
        "tags": ["nicho", "marketing", "conteudo", "audiencia"],
        "priority": "MEDIUM",
        "confidence": 0.89,
        "chunks": ["chunk_V4C001_070"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_TN_005",
        "insight": "[METODOLOGIA] Estrategia de guerrilha no marketing: explorar a ansia das pessoas de dar a noticia em primeiro lugar. Criar curiosidade, deixar vazar informacao estrategica. Case: sosia do Snoop Dog + camisa do Botafogo — viral mundial com baixo orcamento.",
        "tags": ["marketing", "viral", "guerrilha", "criatividade", "PR"],
        "priority": "MEDIUM",
        "confidence": 0.87,
        "chunks": ["chunk_V4C001_075"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_TN_006",
        "insight": "[FILOSOFIA] Internet e lotada de 'paleteiros mexicanos': o cara faz algo e todo mundo copia. O ultimo a copiar se pergunta 'por que nao funcionou?' — porque nao foi o primeiro. A ousadia de ser o primeiro e o que gera resultado.",
        "tags": ["originalidade", "ousadia", "diferenciacao", "marketing"],
        "priority": "MEDIUM",
        "confidence": 0.88,
        "chunks": ["chunk_V4C001_073"],
        "source_id": SOURCE_ID,
    },
]

# ─── ANDRE KLIOUSOFF ──────────────────────────────────────────────────────────
AK_INSIGHTS = [
    {
        "id": "V4C001_AK_001",
        "insight": "[FILOSOFIA] As coisas vao convergindo — nao tem receita de bolo. Jamais imaginaria onde estaria hoje. A formacao tecnica (sistemas de informacao) + analytics + marketing digital convergiu naturalmente para o papel de CMO do BTG.",
        "tags": ["carreira", "convergencia", "marketing", "tecnologia"],
        "priority": "MEDIUM",
        "confidence": 0.88,
        "chunks": ["chunk_V4C001_095"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_AK_002",
        "insight": "[HEURISTICA] O doutorado ensinou senso critico e humildade. 'Olhar pro numero e reconhecer que errou.' Varias vezes o orientador falou: 'Isso nao ta batendo, voce errou, volta.' Quem nao sabe reconhecer que errou nao evolui.",
        "tags": ["humildade", "dados", "aprendizagem", "senso-critico"],
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_V4C001_097"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_AK_003",
        "insight": "[MODELO-MENTAL] BTG transformation: de banco de atacado (R$10M minimo para abrir conta) para banco digital acessivel. Chave da transformacao: ter canal proprietario. Canal proprio = relacionamento direto com cliente = dados + controle da jornada.",
        "tags": ["BTG", "transformacao", "canal-proprio", "digital", "banco"],
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_V4C001_100"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_AK_004",
        "insight": "[FRAMEWORK] Marketing moderno = integracao de tecnologia + dados + criatividade. Os tres nao se substituem — se potencializam. Um CMO que nao entende de dados e cego. Um CMO que nao entende de criatividade e apenas engenheiro.",
        "tags": ["marketing", "dados", "criatividade", "tecnologia", "CMO"],
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_V4C001_105"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C001_AK_005",
        "insight": "[METODOLOGIA] BTG: asset management + investment banking + plataforma digital. Analogia: BTG cria o produto (fundos, ETFs), a plataforma distribui, o banco assessora. Tres camadas integradas que se retroalimentam.",
        "tags": ["BTG", "modelo-negocio", "financeiro", "plataforma"],
        "priority": "LOW",
        "confidence": 0.85,
        "chunks": ["chunk_V4C001_102"],
        "source_id": SOURCE_ID,
    },
]

# ─── SAVE TO INSIGHTS-STATE ───────────────────────────────────────────────────
SPEAKER_MAP = {
    "Dener Lippert": DL_INSIGHTS,
    "Rami Goldratt": RG_INSIGHTS,
    "Thiago Nigro": TN_INSIGHTS,
    "Andre Kliousoff": AK_INSIGHTS,
}

total_added = 0
for person_name, insight_list in SPEAKER_MAP.items():
    if person_name not in persons:
        persons[person_name] = {"insights": []}

    existing_ids = {ins.get("id") for ins in persons[person_name].get("insights", [])}
    new = [ins for ins in insight_list if ins["id"] not in existing_ids]

    persons[person_name].setdefault("insights", []).extend(new)
    total_added += len(new)
    print(f"  {person_name}: +{len(new)} insights")

# Update change log
state["insights_state"].setdefault("change_log", []).append({
    "timestamp": datetime.now().isoformat(),
    "source_id": SOURCE_ID,
    "action": "INSIGHT_EXTRACTION",
    "persons_updated": list(SPEAKER_MAP.keys()),
    "insights_added": total_added,
})

with open(INSIGHTS_PATH, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

total_in_state = sum(len(p.get("insights", [])) for p in persons.values())
print(f"\nTotal insights added: {total_added}")
print(f"Total insights in state: {total_in_state}")
