"""Insight extraction for Traffic Secrets (RB54D) — Russell Brunson"""
import json, datetime
from pathlib import Path
from collections import Counter

SOURCE_ID = "RB54D"
SOURCE_PERSON = "Russell Brunson"
SOURCE_TITLE = "Traffic Secrets"

ROOT = Path("c:/Users/Gabriel/MEGABRAIN")
INSIGHTS_PATH = ROOT / "processing/insights/INSIGHTS-STATE.json"

insights = [
    # FRAMEWORKS
    {
        "id": "INS-RB54D-001",
        "titulo": "Dream 100 — Estratégia Central de Todo Tráfego",
        "insight": "O Dream 100 não é uma tática — é a estratégia de tráfego de todo negócio que escala. Mapear os 100 canais (blogs, podcasts, influenciadores, newsletters, grupos) onde o avatar ideal já está concentrado. Brunson: 100.648 clientes ativos no ClickFunnels vieram majoritariamente dos seguidores dos 736 Dream 100 identificados. Dois modos de acesso: (1) Work your way in — conquistar parceria/endosso; (2) Buy your way in — anunciar nos canais do Dream 100.",
        "priority": "HIGH", "confidence": 0.98,
        "tags": ["[FRAMEWORK]", "tráfego", "Dream100", "distribuição"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB54D_035", "chunk_RB54D_036", "chunk_RB54D_037"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["TRÁFEGO", "ESTRATÉGIA", "PARCERIA"]
    },
    {
        "id": "INS-RB54D-002",
        "titulo": "3 Core Markets — Saúde, Riqueza, Relacionamentos",
        "insight": "Todos os produtos/serviços se encaixam em um dos 3 mercados principais: Saúde, Riqueza ou Relacionamentos. Dentro de cada mercado, o prospect está se movendo em uma de duas direções: Away from Pain (fuga da dor) ou Toward Pleasure (busca do prazer). Identificar o Core Market e a direção do movimento antes de criar qualquer copy ou funil. Copy que não reconhece a direção do movimento do prospect não ressoa.",
        "priority": "HIGH", "confidence": 0.95,
        "tags": ["[FRAMEWORK]", "avatar", "copy", "mercado"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB54D_018", "chunk_RB54D_019", "chunk_RB54D_020"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["AVATAR", "COPY", "MERCADO"]
    },
    {
        "id": "INS-RB54D-003",
        "titulo": "Hook, Story, Offer — A Estrutura de Todo Anúncio e Funil",
        "insight": "Todo anúncio, email e funil tem 3 elementos em sequência: (1) HOOK — o único trabalho do hook é fazer o prospect parar de rolar e clicar; (2) STORY — uma história que cria crença e conexão emocional; (3) OFFER — a oferta apresentada depois que a crença foi instalada. Anúncio sem hook forte não é visto. Oferta sem story não converte. A maioria das empresas foca só na oferta e ignora hook e story.",
        "priority": "HIGH", "confidence": 0.97,
        "tags": ["[FRAMEWORK]", "copy", "anúncio", "funil"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB54D_022", "chunk_RB54D_023"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["COPY", "ANÚNCIO", "FUNIL"]
    },
    {
        "id": "INS-RB54D-004",
        "titulo": "Work Your Way In vs. Buy Your Way In — Earned vs. Paid",
        "insight": "Dois modos de acessar audiências do Dream 100: (1) BUY (pago) — comprar anúncios nos canais do Dream 100; acesso imediato, com custo, dependente de orçamento; (2) WORK (ganhar) — construir relacionamento, criar valor, conseguir endosso orgânico; acesso gratuito, mas demorado. Ambos são essenciais. Apenas paid = vulnerável a slaps. Apenas earned = dependente de terceiros. A combinação dos dois constrói empresa resiliente.",
        "priority": "HIGH", "confidence": 0.95,
        "tags": ["[FRAMEWORK]", "tráfego", "pago", "orgânico"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB54D_048", "chunk_RB54D_049"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["TRÁFEGO", "ESTRATÉGIA", "MÍDIA"]
    },
    {
        "id": "INS-RB54D-005",
        "titulo": "Follow-up Funnels — O Dinheiro Está no Follow-up",
        "insight": "Follow-up funnels são a segunda fase de todo funil: o que acontece com prospects que não compraram na primeira visita. Estrutura: Soap Opera Sequence (onboarding de subscribers) → Daily Seinfeld Broadcasts (manutenção de lista). O objetivo é criar relacionamento suficiente para converter no próximo toque. Brunson: a lista é o ativo mais valioso — o follow-up é o que a monetiza.",
        "priority": "HIGH", "confidence": 0.94,
        "tags": ["[FRAMEWORK]", "email", "follow-up", "lista"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB54D_060", "chunk_RB54D_061"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["EMAIL", "FUNIL", "LISTA"]
    },
    # METODOLOGIAS
    {
        "id": "INS-RB54D-006",
        "titulo": "Digging Your Well Before You're Thirsty — Relacionamento Antes da Necessidade",
        "insight": "Metodologia para construir relacionamento com o Dream 100 antes de precisar deles: (1) Seguir e consumir o conteúdo de todos os Dream 100; (2) Engajar genuinamente (comentários, compartilhamentos, mensagens); (3) Oferecer valor antes de pedir qualquer coisa; (4) Colaborar (entrevistar no show próprio); (5) Pedir o endosso apenas após relacionamento estabelecido. Quem pede parceria sem construir relacionamento primeiro obtém 'não' quase sempre.",
        "priority": "HIGH", "confidence": 0.94,
        "tags": ["[METODOLOGIA]", "Dream100", "parceria", "relacionamento"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB54D_040", "chunk_RB54D_041"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["PARCERIA", "ESTRATÉGIA", "RELACIONAMENTO"]
    },
    {
        "id": "INS-RB54D-007",
        "titulo": "Conversation Domination — Publicar em Todos os Canais Simultaneamente",
        "insight": "Metodologia de distribuição de conteúdo: criar um show principal (podcast, blog ou vídeo — baseado em preferência pessoal) e distribuir em todos os canais secundários. Publicar diariamente por 1 ano antes de esperar retorno orgânico significativo. O show serve 3 funções: (1) construir audiência; (2) testar material e encontrar a voz; (3) dar plataforma ao Dream 100 via entrevistas — abrindo portas para parceria.",
        "priority": "HIGH", "confidence": 0.93,
        "tags": ["[METODOLOGIA]", "conteúdo", "distribuição", "show"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB54D_075", "chunk_RB54D_076"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["CONTEÚDO", "DISTRIBUIÇÃO", "ORGÂNICO"]
    },
    {
        "id": "INS-RB54D-008",
        "titulo": "Integration Marketing — Inserir na Pipeline do Dream 100",
        "insight": "Metodologia de Mark Joyner aplicada por Brunson: em vez de comprar um anúncio pontual para a lista de parceiro, integrar o email/oferta diretamente no funil de follow-up do parceiro. Exemplo: seu email é enviado automaticamente no dia 3 para todo novo lead do parceiro. Configurar uma vez = benefício diário sem esforço adicional. Integration > Ad buy. Um acordo de integração vale mais que 100 anúncios avulsos.",
        "priority": "HIGH", "confidence": 0.93,
        "tags": ["[METODOLOGIA]", "parceria", "integração", "distribuição"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB54D_158", "chunk_RB54D_159"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["PARCERIA", "TRÁFEGO", "AUTOMAÇÃO"]
    },
    {
        "id": "INS-RB54D-009",
        "titulo": "Funnel Hub — Central de Tráfego da Marca",
        "insight": "O Funnel Hub é um site minimalista que serve como hub de navegação para todos os funis da marca — não é um website tradicional, é uma central de destinos. Estrutura: página principal com a história da marca + links para todos os funis, produtos, show, livros, e call-to-action principal. Objetivo: qualquer visitante pode encontrar o funil certo para ele. Diferente de um website (muitas opções) e de um funil (uma opção) — é o mapa da jornada.",
        "priority": "HIGH", "confidence": 0.90,
        "tags": ["[METODOLOGIA]", "funil", "website", "hub"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB54D_108", "chunk_RB54D_109"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "WEBSITE", "MARCA"]
    },
    {
        "id": "INS-RB54D-010",
        "titulo": "Affiliate Army — Exército de Afiliados como Canal de Tráfego",
        "insight": "Afiliados são o canal de tráfego com o melhor ROI: pagam-se apenas após a venda (performance-based). Metodologia: (1) ter produto convertendo via tráfego pago antes de recrutar afiliados; (2) criar materiais de promoção prontos; (3) pagar comissão imediata (não após 30 dias); (4) ter concurso de afiliados com ranking público. Afiliados mais ativos são clientes que compraram e adoraram — transformar compradores em promotores é a forma mais eficiente de recrutamento.",
        "priority": "HIGH", "confidence": 0.91,
        "tags": ["[METODOLOGIA]", "afiliados", "tráfego", "parceria"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB54D_130", "chunk_RB54D_131"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["AFILIADOS", "TRÁFEGO", "PARCERIA"]
    },
    # HEURÍSTICAS
    {
        "id": "INS-RB54D-011",
        "titulo": "Hook é o Único Trabalho do Primeiro Toque",
        "insight": "O único objetivo do hook (headline, thumbnail, abertura de email, primeiro segundo de vídeo) é fazer o prospect parar e continuar lendo/assistindo. Nada mais importa até que o hook funcione. Brunson testa dezenas de hooks antes de escalar qualquer anúncio. Um hook que não para o scroll = zero cliques = zero conversões, independente da qualidade da story ou da oferta.",
        "priority": "HIGH", "confidence": 0.96,
        "tags": ["[HEURISTICA]", "hook", "copy", "anúncio"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Hook fraco = zero conversões, independente de story ou oferta",
        "chunks": ["chunk_RB54D_022", "chunk_RB54D_023"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["COPY", "ANÚNCIO", "CONVERSÃO"]
    },
    {
        "id": "INS-RB54D-012",
        "titulo": "Tráfego Quente Primeiro — Não Pular para Cold Traffic",
        "insight": "Sequência obrigatória de tráfego: (1) Quente (lista própria e seguidores) → (2) Morno (Dream 100 e audiências similares) → (3) Frio (cold ads para desconhecidos). A maioria dos empreendedores vai direto para cold traffic e falha. Brunson: 'há uma enorme pilha de dinheiro à sua frente — não pule sobre ela para buscar pilhas menores mais distantes.' Hot e warm traffic primeiro, cold traffic só após dominar as outras duas.",
        "priority": "HIGH", "confidence": 0.95,
        "tags": ["[HEURISTICA]", "tráfego", "sequência", "escala"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Cold traffic só após dominar hot e warm. Sequência quente → morno → frio",
        "chunks": ["chunk_RB54D_170", "chunk_RB54D_171"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["TRÁFEGO", "ESCALA", "SEQUÊNCIA"]
    },
    {
        "id": "INS-RB54D-013",
        "titulo": "Publicar Diariamente por 1 Ano — Comprometimento Antes de Retorno",
        "insight": "Construção de audiência orgânica exige publicação consistente por 12-24 meses antes de retorno significativo. Não existe atalho para audiência orgânica. O show diário serve como laboratório: testar material, encontrar a voz, documentar a jornada. Quem para antes de 12 meses nunca sabe se teria funcionado. Regra: escolher o formato (texto, vídeo, áudio) baseado na preferência pessoal — não na tendência do mercado.",
        "priority": "HIGH", "confidence": 0.92,
        "tags": ["[HEURISTICA]", "conteúdo", "consistência", "orgânico"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "12-24 meses de publicação consistente antes de retorno orgânico significativo",
        "chunks": ["chunk_RB54D_074", "chunk_RB54D_075"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["CONTEÚDO", "AUDIÊNCIA", "LONGO-PRAZO"]
    },
    {
        "id": "INS-RB54D-014",
        "titulo": "Away From Pain vs. Toward Pleasure — Direção do Movimento",
        "insight": "Todo prospect está se movendo em uma de duas direções: Away from Pain (fuga de dor atual — motivação mais forte) ou Toward Pleasure (busca de prazer futuro — motivação mais fraca porém mais aspiracional). Copy que apela para Away from Pain converte mais rapidamente. Copy que apela para Toward Pleasure constrói aspiração mais forte de longo prazo. Identificar a direção do prospect antes de escrever qualquer linha de copy.",
        "priority": "HIGH", "confidence": 0.94,
        "tags": ["[MODELO-MENTAL]", "copy", "motivação", "psicologia"],
        "dna_tag": "[MODELO-MENTAL]",
        "chunks": ["chunk_RB54D_019", "chunk_RB54D_020"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["COPY", "PSICOLOGIA", "AVATAR"]
    },
    {
        "id": "INS-RB54D-015",
        "titulo": "Estratégia vs. Tática — Estratégia Funciona em Qualquer Plataforma",
        "insight": "A maioria dos empreendedores aprende táticas (como rodar Facebook Ads) mas não aprende a estratégia subjacente. Quando a plataforma muda (Google Slap, Facebook Snap, mudança de algoritmo), perdem tudo. Estratégia — Dream 100, Hook/Story/Offer, traffic que você possui — funciona em qualquer plataforma, passada, presente ou futura. Táticas são temporárias; estratégia é permanente. Aprender o 'por quê' antes do 'como'.",
        "priority": "HIGH", "confidence": 0.95,
        "tags": ["[FILOSOFIA]", "estratégia", "tática", "resiliência"],
        "dna_tag": "[FILOSOFIA]",
        "chunks": ["chunk_RB54D_008", "chunk_RB54D_009"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["ESTRATÉGIA", "TRÁFEGO", "RESILIÊNCIA"]
    },
    {
        "id": "INS-RB54D-016",
        "titulo": "Plataformas São Temporárias — Lista É Permanente",
        "insight": "Redes sociais e plataformas de anúncios mudam suas regras, algorit­mos e políticas constantemente (Google Slap, Facebook Snap, morte do reach orgânico). A única defesa é construir tráfego próprio (lista de email) que nenhuma plataforma pode remover. Toda ação de marketing deve ter como objetivo secundário a captura de email. Construir audiência em plataforma de terceiros sem capturar email é construir sobre areia.",
        "priority": "HIGH", "confidence": 0.96,
        "tags": ["[FILOSOFIA]", "lista", "resiliência", "plataforma"],
        "dna_tag": "[FILOSOFIA]",
        "chunks": ["chunk_RB54D_047", "chunk_RB54D_048"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["LISTA", "EMAIL", "RESILIÊNCIA"]
    },
    {
        "id": "INS-RB54D-017",
        "titulo": "Instagram — Profil Página como Landing Page",
        "insight": "No Instagram, a bio é a única área com link clicável — deve apontar para opt-in ou funil principal. O perfil funciona como landing page: foto profissional, bio que explica quem você ajuda e como, link para o funil. Stories para engajamento diário; Feed para autoridade; Reels para alcance. Regra de publicação: conteúdo que agrega valor primeiro, pitch depois (razão 80/20).",
        "priority": "HIGH", "confidence": 0.89,
        "tags": ["[HEURISTICA]", "Instagram", "social media", "tráfego"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Bio do Instagram = landing page. Link único deve ir para opt-in ou funil principal",
        "chunks": ["chunk_RB54D_090", "chunk_RB54D_091"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["INSTAGRAM", "SOCIAL", "TRÁFEGO"]
    },
    {
        "id": "INS-RB54D-018",
        "titulo": "Facebook — Perfil Pessoal como Canal de Relacionamento",
        "insight": "O perfil pessoal do Facebook funciona como canal de relacionamento (não venda direta). Habilitar a opção de 'seguir' permite seguidores ilimitados além dos 5.000 amigos. Cover photo como billboard de marca. Status updates diários = presença de mente. Grupos do Facebook como comunidade de nicho = tráfego altamente engajado. Fan pages para amplificação via ads; perfil pessoal para autenticidade e conexão.",
        "priority": "HIGH", "confidence": 0.88,
        "tags": ["[HEURISTICA]", "Facebook", "social media", "tráfego"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Perfil pessoal: relacionamento. Fan page: anúncios. Grupos: comunidade e tráfego orgânico",
        "chunks": ["chunk_RB54D_107", "chunk_RB54D_108"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["FACEBOOK", "SOCIAL", "TRÁFEGO"]
    },
    {
        "id": "INS-RB54D-019",
        "titulo": "YouTube — Canal de Busca + Comunidade Permanente",
        "insight": "YouTube é a única plataforma social onde o conteúdo é encontrado via busca ativa (como Google) — não apenas via feed passivo. Vídeo que performa bem no YouTube tem vida longa (diferente de Instagram/Facebook que morre em 48h). Estratégia: criar conteúdo evergreen que responde às perguntas que o avatar está buscando no YouTube. SEO de YouTube = tráfego orgânico qualificado e gratuito de longo prazo.",
        "priority": "HIGH", "confidence": 0.91,
        "tags": ["[MODELO-MENTAL]", "YouTube", "SEO", "tráfego orgânico"],
        "dna_tag": "[MODELO-MENTAL]",
        "chunks": ["chunk_RB54D_145", "chunk_RB54D_146"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["YOUTUBE", "ORGÂNICO", "SEO"]
    },
    {
        "id": "INS-RB54D-020",
        "titulo": "Google Traffic — SEO via Linkable Assets",
        "insight": "SEO do Google funciona por link equity: conteúdo que outros sites naturalmente linkam (linkable assets). Tipos de linkable assets: pesquisas originais, listas definitivas ('205 recursos'), guias completos, ferramentas gratuitas. Google rastreia tempo no site, scroll depth, e cliques — conteúdo que retém o visitante sobe no ranking. Estratégia: criar o recurso mais completo sobre o tema do avatar.",
        "priority": "HIGH", "confidence": 0.88,
        "tags": ["[METODOLOGIA]", "SEO", "Google", "conteúdo"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB54D_124", "chunk_RB54D_125"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["SEO", "GOOGLE", "CONTEÚDO"]
    },
    {
        "id": "INS-RB54D-021",
        "titulo": "Cold Traffic — Só Após Funil Convertendo com Hot/Warm",
        "insight": "Cold traffic (anúncios para audiências frias) só é viável quando o funil já converte com hot e warm traffic. Para escalar a 9 dígitos+, cold traffic é obrigatório — mas a maioria das empresas não está pronta. Regra: provar que o funil converte com tráfego morno antes de investir em cold. Cold traffic exige pre-frame mais longo, copy mais educativo e budget maior para testar — é o tráfego mais caro por conversão.",
        "priority": "HIGH", "confidence": 0.91,
        "tags": ["[HEURISTICA]", "cold traffic", "escala", "funil"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Cold traffic só após funil comprovado com hot/warm. Escala a 9 dígitos exige cold",
        "chunks": ["chunk_RB54D_170", "chunk_RB54D_171"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["TRÁFEGO", "ESCALA", "ANÚNCIO"]
    },
    {
        "id": "INS-RB54D-022",
        "titulo": "Podcast — Canal de Relacionamento Profundo",
        "insight": "Podcast é o canal de conteúdo com maior profundidade de relacionamento: o ouvinte passa 30-90 min com a voz do host enquanto dirige, faz exercício, lava louça. Alcance menor que vídeo/texto, mas engajamento muito maior. Estratégia: entrevistar o Dream 100 no podcast para construir relacionamento e dar plataforma. Ouvinte médio assina 6 shows — crescimento via recomendação pessoal, não algoritmo.",
        "priority": "HIGH", "confidence": 0.89,
        "tags": ["[MODELO-MENTAL]", "podcast", "conteúdo", "relacionamento"],
        "dna_tag": "[MODELO-MENTAL]",
        "chunks": ["chunk_RB54D_140", "chunk_RB54D_141"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["PODCAST", "CONTEÚDO", "RELACIONAMENTO"]
    },
    {
        "id": "INS-RB54D-023",
        "titulo": "Documentar a Jornada — Show Como Laboratório de Material",
        "insight": "O show não precisa ser de expert — pode documentar a jornada de alguém que está tentando alcançar o mesmo resultado que o avatar. Documentar > Ensinar no início: menos pressão de ser autoridade, mais identificação do avatar. O processo de documentação serve como laboratório: descobre-se o que a audiência responde antes de criar produto. Só criar produto depois de validar qual conteúdo ressoa.",
        "priority": "HIGH", "confidence": 0.90,
        "tags": ["[FILOSOFIA]", "conteúdo", "show", "validação"],
        "dna_tag": "[FILOSOFIA]",
        "chunks": ["chunk_RB54D_073", "chunk_RB54D_074"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["CONTEÚDO", "VALIDAÇÃO", "SHOW"]
    },
    {
        "id": "INS-RB54D-024",
        "titulo": "Outros Canais de Distribuição — Explorar Distribuição do Dream 100",
        "insight": "Além de anúncios e parcerias de endosso, explorar os canais de distribuição existentes do Dream 100: newsletters de terceiros (solo ads), grupos de Facebook de nicho, fóruns específicos, comunidades Discord/Slack, eventos e masterminds. Qualquer canal onde o Dream 100 tem audiência é um canal potencial. Guerilla marketing: encontrar distribuição onde os concorrentes não estão olhando.",
        "priority": "HIGH", "confidence": 0.88,
        "tags": ["[MODELO-MENTAL]", "distribuição", "tráfego", "canais"],
        "dna_tag": "[MODELO-MENTAL]",
        "chunks": ["chunk_RB54D_155", "chunk_RB54D_156"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["DISTRIBUIÇÃO", "TRÁFEGO", "CANAIS"]
    },
    {
        "id": "INS-RB54D-025",
        "titulo": "Tempestades de Plataforma São Previsíveis — Preparação É a Resposta",
        "insight": "Slaps e snaps de plataformas (Google Slap 2003, Facebook Snap, mudanças de algoritmo) são certos — não é questão de se, mas quando. Empresas que sobrevivem têm: (1) funnels que multiplicam o valor por visitante; (2) estratégia (não só tática) de tráfego que funciona em qualquer plataforma; (3) lista própria que não depende de plataforma. A preparação para a próxima tempestade começa antes dela chegar.",
        "priority": "HIGH", "confidence": 0.94,
        "tags": ["[FILOSOFIA]", "resiliência", "plataforma", "estratégia"],
        "dna_tag": "[FILOSOFIA]",
        "chunks": ["chunk_RB54D_008", "chunk_RB54D_009"],
        "fonte": SOURCE_ID, "source_title": SOURCE_TITLE,
        "dominio": ["ESTRATÉGIA", "RESILIÊNCIA", "TRÁFEGO"]
    },
]

with open(INSIGHTS_PATH, "r", encoding="utf-8") as f:
    state = json.load(f)

if "persons" not in state["insights_state"]:
    state["insights_state"]["persons"] = {}

person_key = SOURCE_PERSON
if person_key not in state["insights_state"]["persons"]:
    state["insights_state"]["persons"][person_key] = []

person_data = state["insights_state"]["persons"][person_key]
existing_list = person_data if isinstance(person_data, list) else person_data.get("insights", [])
existing_ids = {i["id"] for i in existing_list}

new_count = 0
for insight in insights:
    if insight["id"] not in existing_ids:
        insight["source_id"] = SOURCE_ID
        insight["source_person"] = SOURCE_PERSON
        insight["timestamp"] = datetime.datetime.now().isoformat()
        existing_list.append(insight)
        new_count += 1

if isinstance(state["insights_state"]["persons"][person_key], list):
    state["insights_state"]["persons"][person_key] = existing_list
else:
    state["insights_state"]["persons"][person_key]["insights"] = existing_list

state["insights_state"].setdefault("change_log", []).append({
    "date": "2026-03-09", "source_id": SOURCE_ID, "action": "added",
    "count": new_count, "person": SOURCE_PERSON
})

with open(INSIGHTS_PATH, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

tags = Counter(i.get("dna_tag", "NONE") for i in insights)
high = sum(1 for i in insights if i["priority"] == "HIGH")
print(f"Source: {SOURCE_PERSON} ({SOURCE_ID}) — {SOURCE_TITLE}")
print(f"Insights added: {new_count}/{len(insights)} | HIGH={high}")
print("DNA distribution:")
for tag, count in sorted(tags.items()):
    print(f"  {tag}: {count}")
