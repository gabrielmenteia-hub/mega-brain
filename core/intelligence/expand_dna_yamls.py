"""
Expande os YAMLs individuais do DNA de Russell Brunson com itens de
RB54D (Traffic Secrets), RB2DF (Marketing Secrets BK) e RB11F (Lead Funnels).
Total: +75 itens novos (RB5D4 já estava nos YAMLs originais).
"""
import yaml
from pathlib import Path

DNA_DIR = Path("c:/Users/Gabriel/MEGABRAIN/knowledge/dna/persons/russell-brunson")

# ─── NOVOS ITENS POR CAMADA ───────────────────────────────────────────────

FILOSOFIAS_NOVAS = [
    {
        "id": "FIL-RB007",
        "titulo": "Plataformas São Temporárias — Estratégia é Permanente",
        "descricao": (
            "Redes sociais, algoritmos e plataformas mudam ou fecham. "
            "O que funciona sempre: atrair pessoas, construir lista, ascender na Value Ladder. "
            "Empreendedores que constroem estratégia sobre plataformas específicas são reféns "
            "de mudanças fora do seu controle. A estratégia (Dream 100, Hook/Story/Offer, "
            "lista própria) é independente de plataforma."
        ),
        "peso": 0.91,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_080", "chunk_RB54D_081"],
        "insight_origem": "INS-RB54D-016",
        "dominio": ["ESTRATÉGIA", "TRÁFEGO", "LONGO-PRAZO"]
    },
    {
        "id": "FIL-RB008",
        "titulo": "Digging Your Well Before You're Thirsty",
        "descricao": (
            "Relacionamentos com o Dream 100 devem ser construídos ANTES de precisar deles. "
            "Quem pede favor sem ter dado valor primeiro é rejeitado. O processo leva meses: "
            "comentar, promover, dar valor, se tornar conhecido. Quando o parceiro diz 'sim' "
            "ao endosso, é porque você já era parte do ecossistema dele."
        ),
        "peso": 0.90,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_055", "chunk_RB54D_056"],
        "insight_origem": "INS-RB54D-006",
        "dominio": ["RELACIONAMENTO", "DREAM-100", "LONGO-PRAZO"]
    },
    {
        "id": "FIL-RB009",
        "titulo": "Todo Negócio Precisa de Leads ou Clientes",
        "descricao": (
            "Toda empresa tem apenas dois problemas: falta de leads ou falta de clientes. "
            "Lead funnel resolve o primeiro. Se o negócio tem leads mas não clientes, "
            "o problema é o funil de conversão — não o lead magnet. "
            "Esta é a única divisão diagnóstica que importa para tomar a próxima ação."
        ),
        "peso": 0.92,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_001"],
        "insight_origem": "RB11F-001",
        "dominio": ["LEADS", "DIAGNÓSTICO", "FUNIL"]
    },
    {
        "id": "FIL-RB010",
        "titulo": "Lista Própria é o Único Ativo Incontrolável pelo Mercado",
        "descricao": (
            "Tráfego pago depende de plataformas. SEO depende de algoritmos. "
            "A lista de email é o único ativo que o empreendedor controla completamente — "
            "pode enviar uma mensagem para toda a lista a qualquer momento, "
            "independente de algoritmos, custos de anúncio ou mudanças de plataforma. "
            "Construir a lista é construir o negócio."
        ),
        "peso": 0.95,
        "fontes": ["RB11F", "RB5D4"],
        "chunks": ["chunk_RB11F_004"],
        "insight_origem": "RB11F-002",
        "dominio": ["LISTA", "EMAIL", "ATIVO-PRÓPRIO"]
    },
    {
        "id": "FIL-RB011",
        "titulo": "Vender É a Única Coisa que Importa",
        "descricao": (
            "Todo o marketing, conteúdo e branding serve apenas uma função: gerar vendas. "
            "Empreendedores que confundem 'criar conteúdo' com 'fazer negócio' ficam "
            "ocupados mas quebrados. Métricas de vaidade (views, likes, seguidores) "
            "não pagam boletos. A única métrica que importa é receita."
        ),
        "peso": 0.94,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_044"],
        "insight_origem": "RB2DF-002",
        "dominio": ["VENDAS", "FOCO", "RESULTADO"]
    },
    {
        "id": "FIL-RB012",
        "titulo": "Polaridade é Necessária para Liderança de Mercado",
        "descricao": (
            "Tentar agradar a todos é o caminho mais rápido para a invisibilidade. "
            "Líderes de mercado polarizam: têm fãs ardentes E críticos vocais. "
            "A neutralidade não gera movimento nem compras. "
            "Polarity não é ser controverso por ser — é ter posições claras e defendê-las "
            "mesmo diante de críticas."
        ),
        "peso": 0.91,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_063"],
        "insight_origem": "RB2DF-003",
        "dominio": ["POSICIONAMENTO", "LIDERANÇA", "MOVIMENTO"]
    },
    {
        "id": "FIL-RB013",
        "titulo": "Foco Composto — Um Negócio até Escalar",
        "descricao": (
            "95% dos empreendedores têm 3+ negócios simultaneamente. Isso é fatal. "
            "O foco em um único negócio cria efeito composto: cada lançamento, "
            "tráfego e oferta se acumula em um único ativo que cresce exponencialmente. "
            "Escalar três negócios mediocres é infinitamente inferior a dominar um."
        ),
        "peso": 0.93,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_133"],
        "insight_origem": "RB2DF-004",
        "dominio": ["FOCO", "ESCALA", "NEGÓCIO"]
    },
    {
        "id": "FIL-RB014",
        "titulo": "Sua Opinião Não Importa — O Mercado Decide",
        "descricao": (
            "A opinião do empreendedor sobre sua oferta, copy ou produto é irrelevante. "
            "Apenas o mercado tem autoridade para validar o que funciona. "
            "Testar e medir dados reais é a única forma de saber o que converte. "
            "Viés de confirmação é o maior inimigo de quem não testa."
        ),
        "peso": 0.92,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_010"],
        "insight_origem": "RB2DF-001",
        "dominio": ["TESTE", "DADOS", "MERCADO"]
    },
]

MODELOS_MENTAIS_NOVOS = [
    {
        "id": "MM-RB009",
        "titulo": "Estratégia vs. Tática — Estratégia Funciona em Qualquer Plataforma",
        "descricao": (
            "Estratégia = princípio universal (Dream 100, Hook/Story/Offer, Value Ladder). "
            "Tática = implementação específica de plataforma (Reels, TikTok, Google Ads). "
            "Quem aprende só táticas fica obsoleto a cada mudança de algoritmo. "
            "Quem aprende estratégia adapta qualquer tática para qualquer plataforma."
        ),
        "peso": 0.92,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_043", "chunk_RB54D_044"],
        "insight_origem": "INS-RB54D-015",
        "dominio": ["ESTRATÉGIA", "TRÁFEGO", "MINDSET"]
    },
    {
        "id": "MM-RB010",
        "titulo": "Away from Pain vs. Toward Pleasure — Direção do Movimento",
        "descricao": (
            "Prospects se movem por dois motivadores: fugir da dor (Away from Pain) "
            "ou ir em direção ao prazer (Toward Pleasure). Away from Pain converte mais "
            "rapidamente (urgência imediata). Toward Pleasure cria aspiração mais duradoura. "
            "Copy eficaz usa os dois: começa com a dor, termina com a visão positiva."
        ),
        "peso": 0.91,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_018", "chunk_RB54D_019"],
        "insight_origem": "INS-RB54D-014",
        "dominio": ["COPY", "PSICOLOGIA", "MOTIVAÇÃO"]
    },
    {
        "id": "MM-RB011",
        "titulo": "Tráfego Quente Primeiro — Hierarquia de Validação",
        "descricao": (
            "Sequência correta para lançar: (1) Hot traffic (sua lista, seguidores existentes); "
            "(2) Warm traffic (audiência do Dream 100); (3) Cold traffic (anúncios pagos). "
            "Pular para cold traffic sem validar com hot/warm é desperdiçar dinheiro. "
            "Se não converte para quem já te conhece, não vai converter para estranhos."
        ),
        "peso": 0.93,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_069", "chunk_RB54D_070"],
        "insight_origem": "INS-RB54D-012",
        "dominio": ["TRÁFEGO", "VALIDAÇÃO", "LANÇAMENTO"]
    },
    {
        "id": "MM-RB012",
        "titulo": "Follow-up — O Dinheiro Está no Follow-up, Não na Frente",
        "descricao": (
            "A maioria dos prospectos não compra na primeira exposição. "
            "70-95% das vendas acontecem no follow-up: emails, retargeting, sequências. "
            "Funis sem follow-up estruturado desperdiçam 80% do tráfego pago. "
            "Follow-up funnels (sequências pós-opt-in e pós-compra) são onde o ROI real mora."
        ),
        "peso": 0.94,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_030", "chunk_RB54D_031"],
        "insight_origem": "INS-RB54D-005",
        "dominio": ["FOLLOW-UP", "EMAIL", "CONVERSÃO"]
    },
    {
        "id": "MM-RB013",
        "titulo": "Lead Magnet — Troca de Valor que Abre Relacionamento",
        "descricao": (
            "Lead magnet não é isca gratuita — é a primeira troca de valor real. "
            "O lead dá o email; o empreendedor entrega algo que resolve uma dor específica "
            "de forma imediata. Quanto mais específico o lead magnet para um problema real "
            "de uma pessoa real, maior a taxa de opt-in e maior a qualidade do lead."
        ),
        "peso": 0.93,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_010"],
        "insight_origem": "RB11F-003",
        "dominio": ["LEAD-MAGNET", "OPT-IN", "VALOR"]
    },
    {
        "id": "MM-RB014",
        "titulo": "Thank You Page como Primeiro Momento de Compra",
        "descricao": (
            "A página de obrigado após opt-in é o momento de maior receptividade: "
            "o lead acabou de dizer 'sim' pela primeira vez. Uma OTO (One-Time Offer) "
            "na thank you page converte 5-15% dos leads imediatamente, recuperando "
            "custo de aquisição antes de qualquer email ser enviado."
        ),
        "peso": 0.92,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_018"],
        "insight_origem": "RB11F-005",
        "dominio": ["THANK-YOU-PAGE", "SLO", "CONVERSÃO"]
    },
    {
        "id": "MM-RB015",
        "titulo": "Frame — Tudo em Vendas Começa com o Frame",
        "descricao": (
            "O frame (enquadramento) determina como o prospect interpreta toda comunicação. "
            "Um professor apresentado como 'caloroso' vs 'frio' recebe avaliações opostas "
            "pela mesma aula. Quem controla o frame controla a percepção e a venda. "
            "Antes de apresentar qualquer oferta, estabelecer o frame correto."
        ),
        "peso": 0.93,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_119"],
        "insight_origem": "RB2DF-006",
        "dominio": ["FRAME", "COPY", "PERCEPÇÃO"]
    },
    {
        "id": "MM-RB016",
        "titulo": "Reciprocidade — Psicologia do Lead Magnet",
        "descricao": (
            "O lead magnet ativa reciprocidade (Cialdini): ao receber algo valioso de graça, "
            "o prospect se sente psicologicamente inclinado a retribuir. "
            "A retribuição inicial é o email. A retribuição maior é a compra. "
            "Quanto mais valiosa é a entrega gratuita, maior é a pressão de reciprocidade."
        ),
        "peso": 0.90,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_010"],
        "insight_origem": "RB11F-025",
        "dominio": ["PSICOLOGIA", "RECIPROCIDADE", "LEAD-MAGNET"]
    },
    {
        "id": "MM-RB017",
        "titulo": "Custo por Lead como Métrica Central de Escala",
        "descricao": (
            "O negócio que sabe exatamente quanto paga por lead (CPL) e quanto cada lead "
            "vale (LTV) pode escalar ilimitadamente. Brunson: '$1-$3 por lead em nosso mercado.' "
            "Sem essa clareza, anunciar é apostar. Com ela, é investimento com retorno calculável. "
            "CPL + SLO + LTV = os três números que definem se o negócio escala."
        ),
        "peso": 0.91,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_046"],
        "insight_origem": "RB11F-006",
        "dominio": ["CPL", "MÉTRICAS", "ESCALA"]
    },
    {
        "id": "MM-RB018",
        "titulo": "Proteção de Prateleira — Ocupar Posição Mental Antes do Concorrente",
        "descricao": (
            "Em toda categoria há espaço limitado de 'prateleira mental' nos clientes. "
            "O primeiro a ocupar uma posição específica torna-se a referência padrão. "
            "Demorar a agir é ceder prateleira ao concorrente. "
            "Uma vez estabelecido, o desafiante precisa de 3-5x mais investimento para deslocar."
        ),
        "peso": 0.90,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_060"],
        "insight_origem": "RB2DF-005",
        "dominio": ["POSICIONAMENTO", "CATEGORIA", "PRATELEIRA"]
    },
]

HEURISTICAS_NOVAS = [
    # RB54D
    {
        "id": "HEU-RB017",
        "titulo": "Dream 100 — Work Your Way In e Buy Your Way In (Duplo Obrigatório)",
        "descricao": "Work Your Way In (construir relacionamento → endosso gratuito, demorado) e Buy Your Way In (anunciar nos canais do Dream 100, pago, imediato) são ambos obrigatórios. Usar só um = empresa frágil. A combinação dos dois cria crescimento sustentável.",
        "threshold": "Mínimo 2 canais de cada tipo (earned + paid) no Dream 100 para empresa resiliente.",
        "peso": 0.93,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_036", "chunk_RB54D_037"],
        "insight_origem": "INS-RB54D-004",
        "dominio": ["DREAM-100", "TRÁFEGO", "PARCERIA"]
    },
    {
        "id": "HEU-RB018",
        "titulo": "Hook — Único Trabalho é Fazer Parar e Clicar",
        "descricao": "O hook de um anúncio tem apenas um trabalho: fazer o prospect parar de scrollar e clicar. Não explicar o produto. Não vender. Apenas interromper. Se o hook não interrompe, a história e a oferta nunca serão vistas. Testar 3-5 hooks por anúncio.",
        "threshold": "CTR < 1% = hook quebrado. Testar novo hook antes de qualquer outra otimização.",
        "peso": 0.95,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_022", "chunk_RB54D_023"],
        "insight_origem": "INS-RB54D-011",
        "dominio": ["HOOK", "ANÚNCIO", "CTR"]
    },
    {
        "id": "HEU-RB019",
        "titulo": "Publicar Diariamente por 1 Ano Antes de Esperar Resultado",
        "descricao": "Criadores de conteúdo que publicam diariamente por 12-24 meses constroem audiência de forma cumulativa. Antes dos 12 meses, o algoritmo ainda está 'calibrando'. Expectativa de resultado antes de 6 meses de publicação diária é prematura.",
        "threshold": "Mínimo 365 dias de publicação consistente antes de julgar se o canal funciona.",
        "peso": 0.90,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_075", "chunk_RB54D_076"],
        "insight_origem": "INS-RB54D-013",
        "dominio": ["CONTEÚDO", "CONSISTÊNCIA", "ALGORITMO"]
    },
    {
        "id": "HEU-RB020",
        "titulo": "Cold Traffic Só Após Funil Convertendo com Hot/Warm",
        "descricao": "Nunca escalar com cold traffic antes de o funil converter com hot/warm. Se não converte para sua lista e seguidores, não vai converter para estranhos. Gastar em cold traffic antes de validar é desperdiçar o orçamento de anúncio.",
        "threshold": "Opt-in > 30% com warm traffic antes de ativar cold traffic paid.",
        "peso": 0.92,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_069"],
        "insight_origem": "INS-RB54D-021",
        "dominio": ["COLD-TRAFFIC", "VALIDAÇÃO", "ANÚNCIO"]
    },
    {
        "id": "HEU-RB021",
        "titulo": "Documentar a Jornada — Conteúdo com Menos Pressão",
        "descricao": "Documentar a própria jornada (o que está aprendendo e fazendo) é mais sustentável do que ensinar (o que exige autoridade estabelecida). Documentação cria identificação com o processo. Ensino exige resultados já provados. Iniciantes devem documentar; experientes ensinam.",
        "threshold": "Se tem menos de 1 ano de expertise no tema, documentar > ensinar.",
        "peso": 0.88,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_091"],
        "insight_origem": "INS-RB54D-023",
        "dominio": ["CONTEÚDO", "DOCUMENTAÇÃO", "AUTORIDADE"]
    },
    {
        "id": "HEU-RB022",
        "titulo": "Tempestades de Plataforma São Previsíveis — Preparar-se Antecipadamente",
        "descricao": "Toda plataforma passa por 'tempestades' (mudanças de algoritmo, banimentos, novos concorrentes). Empreendedores que têm lista própria + múltiplos canais sobrevivem. Quem está em uma só plataforma é destruído. Diversificar antes da tempestade, não durante.",
        "threshold": "Mínimo 3 canais ativos + lista própria de email antes de depender de tráfego pago em 1 canal.",
        "peso": 0.91,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_098"],
        "insight_origem": "INS-RB54D-025",
        "dominio": ["PLATAFORMA", "RISCO", "DIVERSIFICAÇÃO"]
    },
    # RB2DF
    {
        "id": "HEU-RB023",
        "titulo": "Urgência + Escassez — Obrigatório para Fechar",
        "descricao": "Sem urgência ou escassez genuína, qualquer apresentação vira conteúdo educativo. A escassez artificial (fechar carrinho) consistentemente aumenta conversões. Sem deadline, o prospect adia a decisão indefinidamente.",
        "threshold": "Urgência obrigatória. Sem ela, conversão cai 60%+ em relação ao benchmark com deadline.",
        "peso": 0.95,
        "fontes": ["RB2DF", "RB2AE"],
        "chunks": ["chunk_RB2DF_073"],
        "insight_origem": "RB2DF-011",
        "dominio": ["URGÊNCIA", "ESCASSEZ", "FECHAMENTO"]
    },
    {
        "id": "HEU-RB024",
        "titulo": "Decoy Pricing — 3 Opções com Âncora",
        "descricao": "Oferecer 3 opções de preço onde a do meio é o alvo. A opção cara (chamariz) faz a do meio parecer razoável. A opção básica serve de âncora baixa. Sem chamariz, clientes comparam com a cara e sentem resistência.",
        "threshold": "3 opções convertem 30-40% mais que 1 opção única. A opção alvo deve ser ~40-60% do preço premium.",
        "peso": 0.92,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_165"],
        "insight_origem": "RB2DF-012",
        "dominio": ["PRICING", "ANCORAGEM", "CONVERSÃO"]
    },
    {
        "id": "HEU-RB025",
        "titulo": "Empilhar Não Trocar — Nova Oportunidade Sempre",
        "descricao": "Quando uma oferta para de funcionar, a solução nunca é melhorar o produto atual — é apresentar uma nova oportunidade. Melhoria implica que o cliente errou antes. Nova oportunidade dá permissão para recomeçar. Empilhar > Trocar.",
        "threshold": "Nova oportunidade aumenta conversão vs melhoria do mesmo produto em 2-3x na maioria dos mercados.",
        "peso": 0.91,
        "fontes": ["RB2DF", "RB2AE"],
        "chunks": ["chunk_RB2DF_142"],
        "insight_origem": "RB2DF-013",
        "dominio": ["NOVA-OPORTUNIDADE", "OFERTA", "POSICIONAMENTO"]
    },
    {
        "id": "HEU-RB026",
        "titulo": "O Que Você Mede Cresce — KPI Semanal Obrigatório",
        "descricao": "Peter Drucker: o que não é medido não é gerenciado. Métricas rastreadas semanalmente melhoram automaticamente. Os 4 KPIs de funil: Tráfego → Assinantes → Vendas → Membros Ativos. Monitorar em quadro visível no escritório.",
        "threshold": "Revisar KPIs 1x por semana mínimo. Sem revisão semanal, as métricas não melhoram por falta de atenção.",
        "peso": 0.90,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_017"],
        "insight_origem": "RB2DF-014",
        "dominio": ["KPI", "MÉTRICAS", "GESTÃO"]
    },
    {
        "id": "HEU-RB027",
        "titulo": "Guru na Montanha — Distância Estratégica Cria Valor",
        "descricao": "Quanto mais acessível você é, menos é percebido como autoridade (Dan Kennedy). O modelo: criar distância do público faz pessoas pagarem mais para se aproximar. Cada degrau da Value Ladder aproxima um pouco mais. Acessibilidade irrestrita reduz percepção de valor.",
        "threshold": "Acessibilidade irrestrita reduz percepção de valor em 40-60% vs modelo de acesso limitado.",
        "peso": 0.89,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_033"],
        "insight_origem": "RB2DF-016",
        "dominio": ["AUTORIDADE", "DISTÂNCIA", "VALUE-LADDER"]
    },
    # RB11F
    {
        "id": "HEU-RB028",
        "titulo": "SLO — Self-Liquidating Offer: Break-even do Funil",
        "descricao": "SLO ideal ($7-$47) na thank you page. Se 10% dos leads compram o SLO a $27 e CPL é $2: receita por lead = $2.70 > CPL = funil self-liquidating. Tráfego pago torna-se gratuito. Leads que compram SLO têm 5-7x mais chance de comprar o core offer.",
        "threshold": "SLO ideal: $7-$47. Conversão alvo: 5-15%. Break-even: SLO_price × conv_rate ≥ CPL.",
        "peso": 0.94,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_050"],
        "insight_origem": "RB11F-011",
        "dominio": ["SLO", "CPL", "FUNIL"]
    },
    {
        "id": "HEU-RB029",
        "titulo": "Custo por Lead Benchmark — $1-$3 para Info-Produto",
        "descricao": "Em mercados de info-produto e coaching, CPL saudável: $1-$3. Acima de $5 sem SLO que recupera o custo = funil quebrado. Abaixo de $1 = audiência superqualificada ou nicho muito específico. O objetivo do SLO é zerar o custo de aquisição.",
        "threshold": "CPL saudável: $1-$3. Acima de $5 sem SLO = revisar hook/lead magnet imediatamente.",
        "peso": 0.93,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_046"],
        "insight_origem": "RB11F-007",
        "dominio": ["CPL", "BENCHMARK", "ANÚNCIO"]
    },
    {
        "id": "HEU-RB030",
        "titulo": "Opt-in Rate Benchmark — 30-60% para Squeeze Page",
        "descricao": "Squeeze page saudável converte 30-60% dos visitantes em leads. Abaixo de 20% = problema no hook/headline. Acima de 60% = lead magnet altamente específico para audiência qualificada. Testar headline é a maior alavanca de otimização.",
        "threshold": "Opt-in rate alvo: 30-60%. Abaixo de 20% = revisar hook antes de escalar tráfego.",
        "peso": 0.91,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_015"],
        "insight_origem": "RB11F-008",
        "dominio": ["OPT-IN", "SQUEEZE-PAGE", "BENCHMARK"]
    },
    {
        "id": "HEU-RB031",
        "titulo": "Squeeze Page Sem Distrações — Zero Links, Zero Menu",
        "descricao": "Uma squeeze page efetiva tem ZERO distrações: sem menu de navegação, sem links externos, sem múltiplas CTAs. Apenas: headline + imagem do lead magnet + campo de email + botão. Cada elemento adicional reduz opt-in rate.",
        "threshold": "Squeeze page com menu reduz opt-in rate em 30-50% vs página sem distrações.",
        "peso": 0.92,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_016"],
        "insight_origem": "RB11F-022",
        "dominio": ["SQUEEZE-PAGE", "OPT-IN", "FOCO"]
    },
    {
        "id": "HEU-RB032",
        "titulo": "Lista de Email — $1/Mês por Assinante como Benchmark",
        "descricao": "Lista de email bem gerenciada gera $1/mês por assinante. Com 10.000 leads → $10.000/mês esperados. Abaixo disso = sequência fraca ou lead magnet errado (lista não qualificada). Esse benchmark serve para diagnosticar onde está o problema de monetização.",
        "threshold": "$1/mês/assinante. Abaixo de $0.50 = revisar sequência de email ou qualidade dos leads.",
        "peso": 0.93,
        "fontes": ["RB11F", "RB5D4"],
        "chunks": ["chunk_RB11F_048"],
        "insight_origem": "RB11F-023",
        "dominio": ["EMAIL", "LISTA", "MONETIZAÇÃO"]
    },
]

FRAMEWORKS_NOVOS = [
    {
        "id": "FW-RB011",
        "titulo": "Dream 100 Framework — Estratégia Completa de Aquisição de Audiência",
        "descricao": (
            "Identificar as 100 pessoas/marcas onde seu cliente ideal já está concentrado. "
            "Abordagem dual: (1) Work Your Way In — construir relacionamento, ser entrevistado, "
            "obter endosso orgânico (lento mas gratuito); (2) Buy Your Way In — anunciar "
            "para a audiência dessas pessoas (pago mas imediato). "
            "100.648 clientes ClickFunnels vieram dos seguidores dos 736 do Dream 100 de Brunson."
        ),
        "peso": 0.97,
        "fontes": ["RB54D", "RB5D4"],
        "chunks": ["chunk_RB54D_035", "chunk_RB54D_036"],
        "insight_origem": "INS-RB54D-001",
        "dominio": ["TRÁFEGO", "PARCERIA", "DREAM-100"]
    },
    {
        "id": "FW-RB012",
        "titulo": "Hook, Story, Offer — Estrutura Universal de Todo Anúncio e Funil",
        "descricao": (
            "Todo anúncio, email e apresentação tem 3 partes:\n"
            "HOOK → único trabalho: fazer o prospect parar e clicar\n"
            "STORY → criar crença e conexão emocional com o problema/solução\n"
            "OFFER → apresentar depois que a crença foi instalada\n"
            "Anúncio sem hook = invisível. Oferta sem story = não converte. "
            "Story sem offer = apenas entretenimento."
        ),
        "peso": 0.96,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_022", "chunk_RB54D_023"],
        "insight_origem": "INS-RB54D-003",
        "dominio": ["COPY", "ANÚNCIO", "FUNIL"]
    },
    {
        "id": "FW-RB013",
        "titulo": "Conversation Domination — Show Principal + Distribuição Multi-Canal",
        "descricao": (
            "Criar um show principal (formato à escolha: texto/vídeo/áudio) e distribuir "
            "simultaneamente em todos os canais. Publicar diariamente por 12-24 meses. "
            "O show serve como: (1) laboratório de material para testar o que ressoa; "
            "(2) porta de entrada para o Dream 100 via entrevistas; "
            "(3) construção de audiência própria independente de plataforma."
        ),
        "peso": 0.92,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_075", "chunk_RB54D_076"],
        "insight_origem": "INS-RB54D-007",
        "dominio": ["CONTEÚDO", "MULTI-CANAL", "AUDIÊNCIA"]
    },
    {
        "id": "FW-RB014",
        "titulo": "Funnel Hub — Central de Tráfego da Marca",
        "descricao": (
            "O Funnel Hub é a página central que conecta todos os funis da marca: "
            "bio page para redes sociais, hub de todas as ofertas e opt-ins. "
            "Funciona como a 'sede digital' — não um website genérico, mas um hub "
            "estratégico que direciona cada visitante para o funil correto baseado "
            "no nível de consciência e interesse."
        ),
        "peso": 0.88,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_095"],
        "insight_origem": "INS-RB54D-009",
        "dominio": ["FUNIL", "TRÁFEGO", "MARCA"]
    },
    {
        "id": "FW-RB015",
        "titulo": "Attractive Character — 4 Elementos da Persona do Fundador",
        "descricao": (
            "4 componentes do Attractive Character:\n"
            "(1) Backstory — a jornada de origem que o público reconhece\n"
            "(2) Parabolismo — ensinar com histórias, não dados secos\n"
            "(3) Falhas/Fraquezas — humanizar para criar identificação\n"
            "(4) Polaridade — ter posições claras e defendê-las\n"
            "Sem AC, o negócio é commodity sem rosto. O fundador IS the brand."
        ),
        "peso": 0.95,
        "fontes": ["RB2DF", "RB5D4"],
        "chunks": ["chunk_RB2DF_077"],
        "insight_origem": "RB2DF-017",
        "dominio": ["ATTRACTIVE-CHARACTER", "PERSONA", "STORYTELLING"]
    },
    {
        "id": "FW-RB016",
        "titulo": "As Duas Jornadas do Herói — Externa + Interna",
        "descricao": (
            "Todo cliente vive duas jornadas simultâneas:\n"
            "EXTERNA: O problema visível (perder peso, ganhar dinheiro, encontrar parceiro)\n"
            "INTERNA: A identidade que quer construir (quem quer SE TORNAR)\n"
            "Produtos que entregam apenas a jornada externa não criam lealdade. "
            "A jornada interna é o que gera evangelistas: o produto os tornou quem queriam ser."
        ),
        "peso": 0.93,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_080"],
        "insight_origem": "RB2DF-018",
        "dominio": ["JORNADA", "IDENTIDADE", "STORYTELLING"]
    },
    {
        "id": "FW-RB017",
        "titulo": "Posicionamento Mortal — 3 Crimes",
        "descricao": (
            "3 crimes de posicionamento que matam negócios:\n"
            "(1) 'Igual ao concorrente mas melhor' → commodity (sem diferenciação real)\n"
            "(2) Sem posicionamento específico → invisível (não ocupa espaço mental)\n"
            "(3) Mudar posicionamento com frequência → confunde o mercado\n"
            "Posicionamento claro, consistente e polarizante = autoridade de mercado."
        ),
        "peso": 0.91,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_089"],
        "insight_origem": "RB2DF-020",
        "dominio": ["POSICIONAMENTO", "DIFERENCIAÇÃO", "AUTORIDADE"]
    },
    {
        "id": "FW-RB018",
        "titulo": "Anatomia do Lead Funnel — 4 Componentes",
        "descricao": (
            "Todo lead funnel tem 4 partes sequenciais:\n"
            "(1) Lead Magnet — a isca de valor específica\n"
            "(2) Squeeze Page — página de captura com hook (30-60% opt-in)\n"
            "(3) Thank You Page — entrega + OTO/SLO imediato (5-15% conversão)\n"
            "(4) Follow-up Sequence — Soap Opera 5 emails para converter\n"
            "Sem qualquer um dos 4 componentes, o funil perde eficiência estrutural."
        ),
        "peso": 0.95,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_008"],
        "insight_origem": "RB11F-012",
        "dominio": ["LEAD-FUNNEL", "SQUEEZE-PAGE", "FOLLOW-UP"]
    },
    {
        "id": "FW-RB019",
        "titulo": "Value Ladder no Contexto de Lead Funnels",
        "descricao": (
            "O lead funnel é o degrau ZERO da Value Ladder:\n"
            "Grátis (lead magnet) → SLO ($7-47) → Core Offer ($97-$997) → High-ticket ($2k+) → Continuidade\n"
            "Cada degrau serve o cliente E apresenta o próximo. "
            "Sem o degrau zero, a escada não tem entrada. "
            "Leads que compram SLO têm 5-7x mais chance de comprar o core offer."
        ),
        "peso": 0.95,
        "fontes": ["RB11F", "RB5D4"],
        "chunks": ["chunk_RB11F_055"],
        "insight_origem": "RB11F-014",
        "dominio": ["VALUE-LADDER", "LEAD-FUNNEL", "UPSELL"]
    },
]

METODOLOGIAS_NOVAS = [
    {
        "id": "MET-RB011",
        "titulo": "Integration Marketing — Inserir na Pipeline do Dream 100",
        "descricao": (
            "Inserir email/oferta diretamente no funil de follow-up do parceiro: "
            "configurar uma vez = benefício diário automático. "
            "Superior ao ad buy pontual porque: (1) é mensagem contextualizada; "
            "(2) vem com credibilidade do parceiro; (3) escala sem custo adicional. "
            "Requer acordo com o Dream 100 partner antes."
        ),
        "peso": 0.90,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_158"],
        "insight_origem": "INS-RB54D-008",
        "dominio": ["DREAM-100", "PARCERIA", "EMAIL"]
    },
    {
        "id": "MET-RB012",
        "titulo": "Affiliate Army — Criar Exército de Afiliados",
        "descricao": (
            "Converter os clientes mais engajados em afiliados: "
            "(1) identificar clientes com resultados; (2) oferecer comissão; "
            "(3) prover materiais de marketing prontos; (4) gamificar com ranking e prêmios. "
            "Cada afiliado é um Dream 100 micro: tem audiência própria que confia nele. "
            "Custo: apenas comissão paga após venda realizada."
        ),
        "peso": 0.88,
        "fontes": ["RB54D"],
        "chunks": ["chunk_RB54D_110"],
        "insight_origem": "INS-RB54D-010",
        "dominio": ["AFILIADOS", "TRÁFEGO", "ESCALA"]
    },
    {
        "id": "MET-RB013",
        "titulo": "Implementar Lead Funnel em Menos de 1 Hora",
        "descricao": (
            "Com swipe file e funil de referência:\n"
            "(1) Criar headline adaptada para seu mercado: 10 min\n"
            "(2) Criar/adaptar lead magnet (iPhone + 12 erros): 20-30 min\n"
            "(3) Montar squeeze page no ClickFunnels: 10 min\n"
            "(4) Configurar thank you page com OTO: 10 min\n"
            "Total: < 1 hora para funil funcional e testável."
        ),
        "peso": 0.88,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_003"],
        "insight_origem": "RB11F-016",
        "dominio": ["LEAD-FUNNEL", "IMPLEMENTAÇÃO", "VELOCIDADE"]
    },
    {
        "id": "MET-RB014",
        "titulo": "Criar Lead Magnet em 30 Minutos (Método Myron Golden)",
        "descricao": (
            "Processo:\n"
            "(1) Listar 12 erros/dores mais comuns do público: 5 min\n"
            "(2) Gravar vídeo no iPhone ensinando os erros: 20 min\n"
            "(3) Transcrever e converter em PDF: 5 min\n"
            "Resultado: lead magnet percebido como valioso sem produção cara. "
            "Título: 'Os (N) Maiores Erros que (Público) Comete'. "
            "Velocidade de criação supera perfeição."
        ),
        "peso": 0.90,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_026"],
        "insight_origem": "RB11F-017",
        "dominio": ["LEAD-MAGNET", "VELOCIDADE", "CRIAÇÃO"]
    },
    {
        "id": "MET-RB015",
        "titulo": "Calcular Break-Even do Funil (Recoup Ad Cost)",
        "descricao": (
            "Para validar se um funil é escalável:\n"
            "(1) Calcular CPL (custo por lead)\n"
            "(2) Calcular receita média por lead nos primeiros 30 dias (LTV-30)\n"
            "(3) Se LTV-30 > CPL → funil escala\n"
            "(4) Se SLO na thank you page gera receita ≥ CPL → tráfego pago é gratuito\n"
            "Fórmula: Break-even rate = CPL / SLO_price\n"
            "Esse cálculo deve ser feito antes de qualquer escala."
        ),
        "peso": 0.93,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_050"],
        "insight_origem": "RB11F-019",
        "dominio": ["CPL", "LTV", "ROI", "ESCALA"]
    },
    {
        "id": "MET-RB016",
        "titulo": "Modelar Funil Existente — 4 Passos",
        "descricao": (
            "Para modelar qualquer lead funnel do swipe file:\n"
            "(1) Escolher funil do mesmo nicho ou com mesmo público-alvo\n"
            "(2) Opt-in e entrar no funil para observar a experiência completa\n"
            "(3) Capturar screenshots da squeeze page, thank you page e emails\n"
            "(4) Adaptar hook e lead magnet para seu mercado\n"
            "Não copiar — modelar. Modelagem é legal e mais eficiente que criar do zero."
        ),
        "peso": 0.88,
        "fontes": ["RB11F"],
        "chunks": ["chunk_RB11F_005"],
        "insight_origem": "RB11F-020",
        "dominio": ["MODELAGEM", "SWIPE-FILE", "FUNIL"]
    },
    {
        "id": "MET-RB017",
        "titulo": "Tornar-se Comprador para Tornar-se Melhor Vendedor",
        "descricao": (
            "Para dominar qualquer mercado: comprar os produtos dos concorrentes, "
            "entrar nos funis deles, observar a experiência completa como cliente. "
            "Só assim é possível modelar e superar. "
            "Brunson faz isso sistematicamente: opt-in em todos os concorrentes, "
            "mapear cada email, cada upsell, cada sequência."
        ),
        "peso": 0.89,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_024"],
        "insight_origem": "RB2DF-022",
        "dominio": ["PESQUISA", "MODELAGEM", "COMPETIÇÃO"]
    },
    {
        "id": "MET-RB018",
        "titulo": "Validar com Pré-Venda Antes de Criar",
        "descricao": (
            "Antes de criar qualquer produto: vender a ideia antes de existir. "
            "Se não vende como ideia, não vai vender como produto pronto. "
            "Processo: criar a oferta → apresentar para lista ou audiência quente → "
            "medir intenção de compra → só então criar. "
            "Elimina risco de criar algo que ninguém quer."
        ),
        "peso": 0.92,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_027"],
        "insight_origem": "RB2DF-024",
        "dominio": ["VALIDAÇÃO", "PRÉ-VENDA", "PRODUTO"]
    },
    {
        "id": "MET-RB019",
        "titulo": "Controle de Estado Antes de Vender",
        "descricao": (
            "O estado emocional do vendedor/apresentador contamina o estado do público. "
            "Antes de qualquer apresentação ou lançamento: gerenciar estado (energia, foco, crença). "
            "Tony Robbins: estado precede resultado. "
            "Técnicas: ancoragem de estado, movimento físico, revisão de resultados de clientes, "
            "respiração controlada. Um apresentador em estado baixo converte menos mesmo com copy excelente."
        ),
        "peso": 0.87,
        "fontes": ["RB2DF"],
        "chunks": ["chunk_RB2DF_120"],
        "insight_origem": "RB2DF-025",
        "dominio": ["ESTADO", "VENDAS", "APRESENTAÇÃO"]
    },
    {
        "id": "MET-RB020",
        "titulo": "Soap Opera Sequence Pós Opt-in — 5 Emails",
        "descricao": (
            "Sequência de 5 emails após opt-in:\n"
            "Email 1: Open loop + confirmação/entrega do lead magnet\n"
            "Email 2: Backstory + vilão (o problema real)\n"
            "Email 3: Epifania + virada (como você descobriu a solução)\n"
            "Email 4: Benefício oculto + prova social\n"
            "Email 5: CTA urgente + bônus com prazo\n"
            "Converte leads antes de esfriarem. Enviar nos primeiros 5 dias após opt-in."
        ),
        "peso": 0.94,
        "fontes": ["RB11F", "RB5D4"],
        "chunks": ["chunk_RB11F_060"],
        "insight_origem": "RB11F-018",
        "dominio": ["SOAP-OPERA", "EMAIL", "SEQUÊNCIA"]
    },
]


# ── FUNÇÃO PARA ADICIONAR ITENS A UM YAML ────────────────────────────────

def expand_yaml(filename: str, new_items: list[dict], camada: str, new_total: int):
    path = DNA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    existing_ids = {item["id"] for item in data.get("itens", [])}
    added = 0
    for item in new_items:
        if item["id"] not in existing_ids:
            data["itens"].append(item)
            added += 1

    data["total_itens"] = len(data["itens"])
    data["metadados"]["total_insights_processados"] = 125
    data["metadados"]["fontes_utilizadas"] = ["RB2AE", "RB5D4", "RB54D", "RB2DF", "RB11F"]

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False,
                  default_style=None, sort_keys=False, width=120)

    print(f"✓ {filename}: +{added} itens novos → total {len(data['itens'])}")


# ── EXECUTAR ──────────────────────────────────────────────────────────────

expand_yaml("FILOSOFIAS.yaml",    FILOSOFIAS_NOVAS,    "FILOSOFIAS",    16)
expand_yaml("MODELOS-MENTAIS.yaml", MODELOS_MENTAIS_NOVOS, "MODELOS-MENTAIS", 18)
expand_yaml("HEURISTICAS.yaml",   HEURISTICAS_NOVAS,   "HEURISTICAS",   32)
expand_yaml("FRAMEWORKS.yaml",    FRAMEWORKS_NOVOS,    "FRAMEWORKS",    19)
expand_yaml("METODOLOGIAS.yaml",  METODOLOGIAS_NOVAS,  "METODOLOGIAS",  20)

print("\nDNA YAMLs expandidos com sucesso.")
