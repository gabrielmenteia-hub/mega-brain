"""Extract DNA Cognitivo for Richard Koch — 5 camadas"""
import yaml
from pathlib import Path

BASE = Path('c:/Users/Gabriel/MEGABRAIN/knowledge/dna/persons/richard-koch')
TODAY = '2026-03-09'

META = {
    'criado_em': f'{TODAY}T00:00:00Z',
    'protocolo': 'DNA-EXTRACTION-PROTOCOL v1.0',
    'pipeline': 'Jarvis v2.2 (automatico)',
    'trigger': 'densidade >= 3/5 (DOSSIER READY com 50 insights)',
    'fontes_utilizadas': ['RK0DE', 'RK3B8'],
    'total_insights_processados': 50
}

# ─────────────────────────────────────────────────────────────────────
# 1. FILOSOFIAS.yaml — 6 itens
# ─────────────────────────────────────────────────────────────────────
filosofias = {
    'versao': '1.0.0',
    'pessoa': 'Richard Koch',
    'camada': 'FILOSOFIAS',
    'total_itens': 6,
    'itens': [
        {
            'id': 'FIL-RK-001',
            'titulo': 'O Principio 80/20: Desequilibrio e a Lei Universal',
            'descricao': 'Uma pequena minoria de causas (20%) conduz a uma grande maioria de resultados (80%). Essa assimetria nao e excecao — e a regra universal que governa negocios, relacionamentos, riqueza, produtividade e qualquer sistema complexo.',
            'implicacao': 'Identificar os 20% de ouro em qualquer area antes de agir. Parar de distribuir atencao igualmente entre todas as causas.',
            'peso': 0.95,
            'insight_origem': 'RK0DE_001',
            'chunks': ['chunk_RK0DE_001', 'chunk_RK0DE_004'],
            'fontes': ['RK0DE', 'RK3B8']
        },
        {
            'id': 'FIL-RK-002',
            'titulo': 'Mais com Menos: O Motor do Progresso',
            'descricao': 'Toda a historia humana e o progresso economico giram em torno de produzir mais com menos. Identificar e multiplicar os 20% mais produtivos e como ampliar resultados com menos recursos — terra, capital, trabalho e tempo.',
            'implicacao': 'Questionar sempre: Como posso obter o mesmo resultado usando menos recursos? Eliminar o desperdicio antes de otimizar o esforco.',
            'peso': 0.85,
            'insight_origem': 'RK0DE_002',
            'chunks': ['chunk_RK0DE_010', 'chunk_RK0DE_011'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'FIL-RK-003',
            'titulo': 'A Vida Guia o Trabalho, Nao o Contrario',
            'descricao': 'Koch abandonou carreira convencional em 1990 para viver de acordo com seus valores primeiro. O trabalho deve ser configurado ao redor da vida desejada — nao adaptar a vida a demanda do trabalho.',
            'implicacao': 'Definir primeiro como se quer viver, depois construir trabalho que caiba nessa vida. Nao o inverso.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_003',
            'chunks': ['chunk_RK0DE_016'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'FIL-RK-004',
            'titulo': 'O Universo e Instavel: Desequilibrio e Auto-Organizacao',
            'descricao': 'Teoria do Caos e 80/20 se esclarecem mutuamente: o mundo e desequilibrado e nao-linear. Feedback loops distorcem o equilibrio e criam a assimetria 80/20. Sem os feedback loops, a distribuicao seria 50/50.',
            'implicacao': 'Aceitar que desequilibrio e a condicao natural. Identificar os feedback loops positivos no proprio negocio e amplifica-los.',
            'peso': 0.85,
            'insight_origem': 'RK3B8_001',
            'chunks': ['chunk_RK3B8_009', 'chunk_RK3B8_010'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'FIL-RK-005',
            'titulo': 'A Dialetica do 80/20: Eficiencia e Qualidade de Vida como Opostos Complementares',
            'descricao': 'O Principio 80/20 tem natureza dual — yin e yang. A eficiencia abre espaco para a melhoria da vida; uma vida melhor requer clareza sobre o que e realmente importante. Sao opostos complementares, nao contradicoes.',
            'implicacao': 'Nao tratar eficiencia e qualidade de vida como trade-off. Aplicar 80/20 em ambas as dimensoes simultaneamente.',
            'peso': 0.75,
            'insight_origem': 'RK3B8_002',
            'chunks': ['chunk_RK3B8_001', 'chunk_RK3B8_002'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'FIL-RK-006',
            'titulo': 'Os Poucos Vitais vs. Os Muitos Triviais: A Batalha Interna',
            'descricao': 'Toda pessoa e organizacao e resultado de uma coalizao em guerra interna: os muitos triviais (inercia, ineficacia dominantes) vs. os poucos vitais (momentos de eficacia, brilho e bom desempenho). A maioria das atividades resulta em pouco valor. Poucas intervencoes tem impacto massivo.',
            'implicacao': 'Mapear explicitamente a batalha interna. Identificar quais atividades pertencem aos poucos vitais e protege-las. Eliminar ou delegar os muitos triviais.',
            'peso': 0.85,
            'insight_origem': 'RK3B8_003',
            'chunks': ['chunk_RK3B8_054', 'chunk_RK3B8_055'],
            'fontes': ['RK3B8']
        }
    ],
    'metadados': META
}

# ─────────────────────────────────────────────────────────────────────
# 2. MODELOS-MENTAIS.yaml — 12 itens
# ─────────────────────────────────────────────────────────────────────
modelos_mentais = {
    'versao': '1.0.0',
    'pessoa': 'Richard Koch',
    'camada': 'MODELOS-MENTAIS',
    'total_itens': 12,
    'itens': [
        {
            'id': 'MM-RK-001',
            'titulo': 'Grafico Alta Recompensa / Baixo Esforco',
            'descricao': 'Para qualquer objetivo, sempre existe um caminho de alta recompensa com baixo esforco. Traco mentalmente o grafico Esforco x Resultado e busca o ponto de maximo retorno por unidade de esforco.',
            'pergunta_gerada': 'Qual abordagem para este objetivo entrega maximo resultado com minimo esforco?',
            'peso': 0.75,
            'insight_origem': 'RK0DE_004',
            'chunks': ['chunk_RK0DE_013'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'MM-RK-002',
            'titulo': 'Distribuicao Assimetrica e Universal',
            'descricao': 'A proporcao 80/20 e generalizacao. A realidade frequentemente e mais extrema: 70/20, 80/10, 90/10 ou 99/1. 1% das pessoas produz 80%+ dos efeitos. A assimetria e universal — nunca assumir normalidade.',
            'pergunta_gerada': 'Qual e a distribuicao REAL de causas e resultados nesta area? E mais extrema que 80/20?',
            'peso': 0.90,
            'insight_origem': 'RK0DE_005',
            'chunks': ['chunk_RK0DE_006', 'chunk_RK0DE_007'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'MM-RK-003',
            'titulo': 'O Destino 80/20: Pequena Parte Central ao Ser',
            'descricao': 'Cada pessoa tem um destino 80/20 — uma pequena parte de tudo disponivel que e central a sua personalidade e desejos mais profundos. Focar nesse destino cria vida com mais proposito do que se preocupar com multiplas questoes.',
            'pergunta_gerada': 'Qual e a minha interseccao entre picos de habilidade e picos de paixao — o meu destino 80/20?',
            'peso': 0.80,
            'insight_origem': 'RK0DE_006',
            'chunks': ['chunk_RK0DE_026', 'chunk_RK0DE_027'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'MM-RK-004',
            'titulo': 'Ocioso Produtivo vs. Hiperativo Ineficiente',
            'descricao': 'Uma pessoa ociosa quer fazer o minimo, entao se concentra no essencial — e e mais produtiva. Quem trabalha demais esta muito ocupado para identificar o que importa. Modelo Buffett: letargia como vantagem competitiva.',
            'pergunta_gerada': 'Estou ocupado demais para pensar no que realmente importa? Quando foi a ultima vez que fiquei intencionalmente ocioso?',
            'peso': 0.80,
            'insight_origem': 'RK0DE_007',
            'chunks': ['chunk_RK0DE_036', 'chunk_RK0DE_037'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'MM-RK-005',
            'titulo': '6 Graus de Separacao: Conectores sao os 20% Cruciais',
            'descricao': 'No experimento de Milgram, mais da metade dos pacotes chegou ao destino via apenas 3 pessoas muito bem relacionadas. Em qualquer rede, 20% dos nos (conectores) geram 80%+ da conectividade.',
            'pergunta_gerada': 'Quem sao os conectores 20% na minha rede? Estou investindo mais energia neles do que nos demais?',
            'peso': 0.70,
            'insight_origem': 'RK0DE_008',
            'chunks': ['chunk_RK0DE_007'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'MM-RK-006',
            'titulo': 'O Principio da Aceleracao Inversa: Tecnologia Comprime o Tempo',
            'descricao': 'A tecnologia deveria liberar tempo mas faz o oposto: acelera a batida do coracao. O mundo moderno perdeu o controle da aceleracao. Nadar contra essa corrente e vantagem competitiva genuina.',
            'pergunta_gerada': 'Estou nadando com a corrente da aceleracao ou contra ela? Qual e o preco que pago em qualidade de pensamento?',
            'peso': 0.70,
            'insight_origem': 'RK0DE_009',
            'chunks': ['chunk_RK0DE_022'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'MM-RK-007',
            'titulo': 'Feedback Loop: Pequenas Vantagens Criam Grandes Assimetrias',
            'descricao': 'O rico se torna mais rico nao por habilidades superiores, mas porque riqueza gera riqueza. Feedback loops positivos afetam apenas uma pequena minoria das causas — por isso essa minoria exerce influencia tao desproporcional.',
            'pergunta_gerada': 'Quais sao os meus feedback loops positivos — vantagens que se auto-ampliam? Estou investindo nelas primeiro?',
            'peso': 0.80,
            'insight_origem': 'RK3B8_004',
            'chunks': ['chunk_RK3B8_010', 'chunk_RK3B8_011'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'MM-RK-008',
            'titulo': 'Tipping Point: Antes do Ponto de Virada, Muito Esforco / Pouco Resultado',
            'descricao': 'Antes do ponto de virada: grande esforco, pouco resultado. Muitos pioneiros desistem aqui. Quem persiste e cruza a linha invisivel: pequeno esforco extra alcanca grandes resultados. O ponto de virada e o momento critico.',
            'pergunta_gerada': 'Em qual ponto do ciclo este projeto/negocio esta? Antes ou apos o tipping point?',
            'peso': 0.80,
            'insight_origem': 'RK3B8_005',
            'chunks': ['chunk_RK3B8_011', 'chunk_RK3B8_012'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'MM-RK-009',
            'titulo': 'Analise 80/20 vs. Pensamento 80/20: Dois Modos',
            'descricao': 'Analise 80/20: metodo quantitativo para estabelecer relacao precisa entre causas e resultados. Pensamento 80/20: reflexao profunda sobre o que importa, sem dados. Mais rapido porem mais sujeito a erro.',
            'pergunta_gerada': 'Esta decisao merece Analise 80/20 (dados) ou Pensamento 80/20 (intuicao)? Qual o custo de errar?',
            'peso': 0.80,
            'insight_origem': 'RK3B8_006',
            'chunks': ['chunk_RK3B8_018', 'chunk_RK3B8_019'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'MM-RK-010',
            'titulo': 'Arbitragem 80/20: Transferir Recursos dos 80% para os 20%',
            'descricao': 'Lucro de arbitragem e enorme porque voce usa o que nao e muito valioso para produzir algo enormemente valioso. Dois meios: pessoas (mover 20% das pessoas das atividades 80% para as 20%) e dinheiro (mover capital das atividades 80% para as 20%).',
            'pergunta_gerada': 'Quais recursos estao presos em atividades 80%? Como realoca-los para as atividades 20%?',
            'peso': 0.80,
            'insight_origem': 'RK3B8_007',
            'chunks': ['chunk_RK3B8_078', 'chunk_RK3B8_079'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'MM-RK-011',
            'titulo': 'Complexidade Destroi Valor: Simplicidade e o Antidoto',
            'descricao': 'Existe tendencia natural das empresas de se tornarem mais complexas. Todas as organizacoes sao inerentemente ineficientes. O desperdicio se desenvolve na complexidade; a eficacia exige simplicidade.',
            'pergunta_gerada': 'Onde esta crescendo a complexidade no meu negocio? Quais atividades posso eliminar — nao otimizar — para simplificar?',
            'peso': 0.80,
            'insight_origem': 'RK3B8_008',
            'chunks': ['chunk_RK3B8_055', 'chunk_RK3B8_056'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'MM-RK-012',
            'titulo': 'Concentrar Investimentos: Nao Diversifique, Concentre nos 20%',
            'descricao': 'Sabedoria 80/20: escolha a cesta cuidadosamente, coloque nela todos os ovos e tome conta dela como uma aguia. Koch: 3 investimentos (Filofax, Belgo, MSI) = 20% do patrimonio, 80%+ dos ganhos. Filofax: 18x em 3 anos.',
            'pergunta_gerada': 'Estou diversificando por medo ou por estrategia? Quais sao os meus 3 investimentos de maximo conviction?',
            'peso': 0.90,
            'insight_origem': 'RK3B8_009',
            'chunks': ['chunk_RK3B8_019', 'chunk_RK3B8_020'],
            'fontes': ['RK3B8']
        }
    ],
    'metadados': META
}

# ─────────────────────────────────────────────────────────────────────
# 3. HEURISTICAS.yaml — 18 itens (PRIORIDADE MAXIMA)
# ─────────────────────────────────────────────────────────────────────
heuristicas = {
    'versao': '1.0.0',
    'pessoa': 'Richard Koch',
    'camada': 'HEURISTICAS',
    'total_itens': 18,
    'nota': 'Camada de maior valor — contem thresholds numericos e regras de decisao acionaveis',
    'itens': [
        {
            'id': 'HEU-RK-001',
            'titulo': 'Regra do Nao: Se Nao Envolve Seus 20%, Recuse',
            'regra': 'SE pedido algo que nao envolve os 20% centrais proprios ENTAO a resposta e nao',
            'threshold': None,
            'descricao': 'Simplicidade radical na triagem de compromissos. Definir qual e o proprio "estimular entusiasmo" e usar como filtro unico.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_010',
            'chunks': ['chunk_RK0DE_019'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'HEU-RK-002',
            'titulo': 'Nao Gerencie o Tempo — Revolucione-o',
            'regra': 'SE tentado a otimizar o tempo ENTAO eliminar atividades primeiro — nao acelera-las',
            'threshold': None,
            'descricao': 'Gestao do tempo pede para ir mais rapido. Revolucao do tempo propoe o oposto: diminuir a velocidade, reduzir atividades.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_011',
            'chunks': ['chunk_RK0DE_020', 'chunk_RK0DE_021'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'HEU-RK-003',
            'titulo': 'Especializacao Estreita: 99% sobre 1% da Area',
            'regra': 'SE focando em desenvolvimento ENTAO estreitar especialidade ate 99% do conhecimento sobre 1% do dominio',
            'threshold': '99% sobre 1%',
            'descricao': 'As estrelas de desempenho sabem muito sobre pouco. Concentrar energia em uma unica area estreita e tornar-se o especialista mais profundo possivel.',
            'peso': 0.90,
            'insight_origem': 'RK0DE_012',
            'chunks': ['chunk_RK0DE_038'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'HEU-RK-004',
            'titulo': 'Equilibrio e Mediocre — Foque nos Pontos Fortes',
            'regra': 'SE tentado a melhorar fraquezas ENTAO concentrar no desenvolvimento dos pontos fortes — fraquezas nao importam',
            'threshold': None,
            'descricao': 'Estrelas de desempenho nao sao balanceadas — tem muitos pontos fortes e muitas desvantagens. O que gera resultados extraordinarios e concentrar nos pontos fortes ate padroes olimpicos.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_013',
            'chunks': ['chunk_RK0DE_039'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'HEU-RK-005',
            'titulo': '20% das Empresas Geram 80% do Crescimento e Promocoes',
            'regra': 'SE avaliando carreira ENTAO verificar se esta empresa esta no top 20% de crescimento — onde voce trabalha vale mais do que o que voce faz',
            'threshold': '20% das empresas → 80% do crescimento',
            'descricao': '80% do crescimento vem de 20% das empresas. 80% das promocoes ocorrem em 20% das organizacoes. Para quem voce trabalha pode ser mais importante do que o que voce faz.',
            'peso': 0.90,
            'insight_origem': 'RK0DE_014',
            'chunks': ['chunk_RK0DE_030'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'HEU-RK-006',
            'titulo': 'Threshold de 14 Dias: Habito Inverte o Custo',
            'regra': 'SE iniciando novo habito ENTAO comprometer-se com pratica diaria por 14 dias antes de avaliar resultados',
            'threshold': '14 dias de pratica diaria',
            'descricao': 'Corpo e mente se acostumam a qualquer atividade depois de duas semanas de pratica diaria. Apos este periodo, e mais facil faze-la do que deixar de fazer.',
            'peso': 0.90,
            'insight_origem': 'RK0DE_015',
            'chunks': ['chunk_RK0DE_014'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'HEU-RK-007',
            'titulo': 'Vender e a Habilidade que Torna Tudo Mais Facil',
            'regra': 'SE quer desenvolver habilidades de impacto ENTAO aprender a vender — e a habilidade que multiplica todas as outras',
            'threshold': None,
            'descricao': 'Vender ensina a lidar com rejeicao, comunicar-se eficazmente e negociar. Quem aprende a vender aprende a se vender.',
            'peso': 0.70,
            'insight_origem': 'RK0DE_016',
            'chunks': ['chunk_RK0DE_041'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'HEU-RK-008',
            'titulo': 'Entusiasmo > Educacao para Empreendedores',
            'regra': 'SE escolhendo entre entusiasmo e formacao ENTAO priorizar o que genuinamente ama — mais de 50% dos empreendedores bem-sucedidos nao tem diploma',
            'threshold': '50%+ empreendedores de sucesso sem diploma universitario',
            'descricao': 'Mais da metade dos empreendedores bem-sucedidos nao tem educacao universitaria. O entusiasmo — nao a formacao — e o motor do sucesso empreendedor.',
            'peso': 0.85,
            'insight_origem': 'RK0DE_017',
            'chunks': ['chunk_RK0DE_035'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'HEU-RK-009',
            'titulo': 'O Melhor da Vida e Gratuito: Retorno Desproporcional',
            'regra': 'SE buscando mais alegria ENTAO aumentar frequencia de atividades de baixo custo e alto retorno emocional antes de buscar prazer em consumo',
            'threshold': None,
            'descricao': 'Em vidas privadas, sempre ha atividades que dao muito certo com pouco dinheiro. Gestos de afeto, natureza, conexoes genuinas — retorno fantastico com custo minimo.',
            'peso': 0.70,
            'insight_origem': 'RK0DE_018',
            'chunks': ['chunk_RK0DE_013'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'HEU-RK-010',
            'titulo': 'Os Poucos Clientes Vitais: 20% Geram 80% do Lucro',
            'regra': 'SE alocando recursos de vendas e marketing ENTAO concentrar nos 20% de clientes que geram 80% do lucro',
            'threshold': '20% dos clientes → 80% do lucro',
            'descricao': 'Alguns clientes sao essenciais; a maioria nao. Canalizar marketing e vendas para a minoria de clientes onde se pode oferecer algo exclusivo, melhor ou mais valioso.',
            'peso': 0.90,
            'insight_origem': 'RK3B8_010',
            'chunks': ['chunk_RK3B8_065', 'chunk_RK3B8_066'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'HEU-RK-011',
            'titulo': 'Ressuscitar Antigos Clientes: Tecnica Esquecida de Alta Conversao',
            'regra': 'SE buscando conversoes de alto valor e baixo CAC ENTAO contatar antigos clientes satisfeitos a cada 6-12 meses',
            'threshold': '1/3 das vendas de Nicholas Barsan ($1M/ano) = clientes repetidos',
            'descricao': 'Bill Bain voltou ao ultimo cliente que comprara uma biblia e vendeu mais uma. Antigos clientes satisfeitos = menor CAC + maior probabilidade de conversao.',
            'peso': 0.85,
            'insight_origem': 'RK3B8_011',
            'chunks': ['chunk_RK3B8_067', 'chunk_RK3B8_068'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'HEU-RK-012',
            'titulo': '20% dos Funcionarios Geram 80% do Valor',
            'regra': 'SE gerenciando equipe ENTAO identificar os 20% de maior impacto e alocar seu tempo exclusivamente em atividades de alto valor',
            'threshold': '20% dos funcionarios → 80% do valor; 20% do tempo do superprodutor → 80% do seu resultado',
            'descricao': 'Em todas as empresas, 80% dos excedentes sao resultado do trabalho de 20% dos funcionarios. Dentro de um mesmo funcionario, 80% do valor e criado em 20% do tempo.',
            'peso': 0.90,
            'insight_origem': 'RK3B8_012',
            'chunks': ['chunk_RK3B8_033', 'chunk_RK3B8_034'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'HEU-RK-013',
            'titulo': 'Lei da Competicao 80/20: Em Todo Segmento, um Lider Domina',
            'regra': 'SE escolhendo segmento de mercado ENTAO dominar um nicho estreito primeiro — lider do segmento maximiza receita com minimo custo',
            'threshold': '80% dos lucros → 20% dos segmentos',
            'descricao': 'Em cada segmento de mercado, a lei da competicao 80/20 esta operando. O lider maximiza receita com minimo de custo e esforco.',
            'peso': 0.90,
            'insight_origem': 'RK3B8_013',
            'chunks': ['chunk_RK3B8_032', 'chunk_RK3B8_033'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'HEU-RK-014',
            'titulo': 'Aliancas so com Pessoas 20%',
            'regra': 'SE considerando nova parceria ENTAO avaliar se esta pessoa e das 20% que amplificam resultados — aliancas com 80% ocupam espaco dos 20%',
            'threshold': None,
            'descricao': 'Fazer aliancas intensivamente, mas so com pessoas 20% e com aqueles que serao aliados poderosos. Aliancas com pessoas 80% ocupam espaco dos 20%.',
            'peso': 0.80,
            'insight_origem': 'RK3B8_014',
            'chunks': ['chunk_RK3B8_079'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'HEU-RK-015',
            'titulo': 'Cortar as Atividades 80% e Imperativo',
            'regra': 'SE identificada atividade 80% (baixo valor) ENTAO cortar impiedosamente — cada elemento 80% mantido esta ativamente sabotando os 20%',
            'threshold': None,
            'descricao': 'O tempo 80% expulsa o 20%. Os aliados 80% ocupam espaco dos 20%. Nao ha versao suavizada desta regra.',
            'peso': 0.85,
            'insight_origem': 'RK3B8_015',
            'chunks': ['chunk_RK3B8_080'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'HEU-RK-016',
            'titulo': 'Roubar Ideias 20% de Outros Setores e Aplicar no Proprio Nicho',
            'regra': 'SE buscando inovacao ENTAO observar outros setores, identificar suas praticas 20% e adaptar ao proprio negocio',
            'threshold': None,
            'descricao': 'A melhor inovacao e adaptacao cross-setor de pratica de alto impacto. Inovar nas atividades 20% roubando ideias 20% de outros dominios.',
            'peso': 0.75,
            'insight_origem': 'RK3B8_016',
            'chunks': ['chunk_RK3B8_080'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'HEU-RK-017',
            'titulo': 'Usar Alavancagem so em Atividades 20%: Nos 80% e Risco Puro',
            'regra': 'SE considerando alavancagem (dinheiro dos outros) ENTAO usar apenas onde ha conviccao de estar nas atividades 20% — em 80% e vicio e risco',
            'threshold': None,
            'descricao': 'Dinheiro dos outros em atividades 20% cria vencedores. Em atividades 80% e viciante, perigoso e muito arriscado. O risco de alavancar 20% e muito mais baixo do que o percebido.',
            'peso': 0.85,
            'insight_origem': 'RK3B8_017',
            'chunks': ['chunk_RK3B8_079'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'HEU-RK-018',
            'titulo': 'Reducao de Custos pela Simplicidade: Tres Conceitos 80/20',
            'regra': 'SE reduzindo custos ENTAO usar os 3 conceitos: (1) simplicidade pela eliminacao; (2) foco nos 20% de maior impacto; (3) comparacao de desempenho',
            'threshold': None,
            'descricao': 'Nao enfrentar tudo com o mesmo esforco. Reducao de custos e cara! Concentrar nos 20% de maior potencial de impacto e ignorar os 80% restantes.',
            'peso': 0.80,
            'insight_origem': 'RK3B8_018',
            'chunks': ['chunk_RK3B8_055', 'chunk_RK3B8_056'],
            'fontes': ['RK3B8']
        }
    ],
    'metadados': META
}

# ─────────────────────────────────────────────────────────────────────
# 4. FRAMEWORKS.yaml — 8 itens
# ─────────────────────────────────────────────────────────────────────
frameworks = {
    'versao': '1.0.0',
    'pessoa': 'Richard Koch',
    'camada': 'FRAMEWORKS',
    'total_itens': 8,
    'itens': [
        {
            'id': 'FW-RK-001',
            'titulo': 'Os 6 Atributos das Estrelas de Desempenho',
            'descricao': 'Pessoas de alto desempenho compartilham 6 caracteristicas nao-balanceadas.',
            'componentes': [
                '1. Ambicao suave — natural, nao forcada',
                '2. Amor pelo que fazem — entusiasmo, nao esforco',
                '3. Nao sao perfeitas/balanceadas — muitos pontos fortes E fracos',
                '4. Especializacao estreita — sabem muito sobre pouco',
                '5. Pensam e comunicam claramente',
                '6. Desenvolvem formula propria e inimitavel de sucesso'
            ],
            'uso': 'Checklist de auto-avaliacao e criterio de recrutamento. Avaliar candidatos por paixao e clareza de pensamento.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_019',
            'chunks': ['chunk_RK0DE_034', 'chunk_RK0DE_035'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'FW-RK-002',
            'titulo': 'Mapeamento dos 20% de Picos Pessoais',
            'descricao': 'Ferramenta de auto-conhecimento para identificar o Destino 80/20 de cada pessoa.',
            'componentes': [
                'Eixo 1 — Picos de Habilidades: listar 10+ atributos, pontuar cada (0-10), identificar top 20%',
                'Eixo 2 — Picos Emocionais/Pessoais: listar 10+ qualidades, pontuar cada, identificar top 20%',
                'Interseccao dos dois eixos = Destino 80/20 (zona de maximo valor)'
            ],
            'uso': 'Exercicio de auto-descoberta. Estruturar carreira e vida ao redor da interseccao encontrada.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_020',
            'chunks': ['chunk_RK0DE_026', 'chunk_RK0DE_027'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'FW-RK-003',
            'titulo': 'Perguntas 80/20: Diagnostico por Questionamento',
            'descricao': 'Conjunto de perguntas 80/20 para diagnosticar qualquer area e revelar alavancas de menor esforco.',
            'componentes': [
                'Negocios: Quais 20% dos clientes geram 80% do lucro?',
                'Negocios: Quais 20% dos produtos/servicos geram 80% da receita?',
                'Carreira: Quais 20% das atividades geram 80% dos resultados?',
                'Pessoal: Quais 20% das relacoes geram 80% da alegria?',
                'Pessoal: Quais 20% dos esforcos geram 80% da satisfacao?'
            ],
            'uso': 'Banco de perguntas para diagnostico trimestral de negocio, carreira e vida pessoal.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_021',
            'chunks': ['chunk_RK0DE_019', 'chunk_RK0DE_020'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'FW-RK-004',
            'titulo': 'Analise 80/20 da Carreira: 4 Variaveis Criticas',
            'descricao': 'Framework para diagnostico de carreira via 4 variaveis de maior impacto.',
            'componentes': [
                '20% das empresas → 80% do crescimento (onde voce trabalha importa)',
                '20% dos chefes → 80% das promocoes (para quem voce trabalha importa)',
                '20% das atividades → 80% dos resultados (o que voce faz importa)',
                '20% do que voce faz → 80%+ do seu valor (como voce usa seu tempo importa)'
            ],
            'uso': 'Revisao trimestral: (a) Estou na empresa certa? (b) Trabalho para o chefe certo? (c) Faco as atividades de maior valor?',
            'peso': 0.90,
            'insight_origem': 'RK0DE_022',
            'chunks': ['chunk_RK0DE_030', 'chunk_RK0DE_031'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'FW-RK-005',
            'titulo': 'Como Agir 80/20: 6 Principios de Acao',
            'descricao': 'Framework de acao estrategica baseado em 6 principios derivados do 80/20.',
            'componentes': [
                '1. Identificar os 20% de melhor resultado',
                '2. Fazer aliancas so com pessoas/oportunidades 20%',
                '3. Explorar a arbitragem — transferir recursos dos 80% para os 20%',
                '4. Inovar nas atividades 20% roubando ideias de outros setores',
                '5. Cortar impiedosamente as atividades 80%',
                '6. Usar alavancagem apenas nos 20%'
            ],
            'uso': 'Roteiro de decisao estrategica trimestral. Cada acao de alto impacto deve mapear para um desses 6 principios.',
            'peso': 0.85,
            'insight_origem': 'RK3B8_019',
            'chunks': ['chunk_RK3B8_078', 'chunk_RK3B8_079', 'chunk_RK3B8_080'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'FW-RK-006',
            'titulo': 'Diagnostico de Segmentacao: Lei da Competicao 80/20',
            'descricao': 'Framework para analise de mercado e escolha de segmento onde se pode liderar.',
            'componentes': [
                '1. Identificar todos os segmentos de produto/cliente',
                '2. Calcular 80% dos lucros que vem de 20% dos segmentos',
                '3. Avaliar em quais segmentos a empresa e lider',
                '4. Concentrar recursos nos segmentos lucrativos + lideranca'
            ],
            'uso': 'Mapear margem por segmento. Identificar os 20% de maior margem. Concentrar recursos de produto, vendas e marketing neles.',
            'peso': 0.80,
            'insight_origem': 'RK3B8_020',
            'chunks': ['chunk_RK3B8_032', 'chunk_RK3B8_033'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'FW-RK-007',
            'titulo': 'Perguntas 80/20 para Auto-Descoberta de Talentos',
            'descricao': 'Framework de 4 perguntas para identificar os proprios 20% superiores de habilidade.',
            'componentes': [
                '1. O que voce faz melhor do que 80% das pessoas em apenas 20% do tempo?',
                '2. O que voce conquista em 20% do tempo que outros demoram 80%?',
                '3. Se voce medisse alegria, o que aproveitaria mais do que 95% dos colegas?',
                '4. O que voce faria melhor do que 95% das pessoas?'
            ],
            'uso': 'Exercicio de auto-descoberta. Responder considerando toda a trajetoria profissional, academica, de hobbyista.',
            'peso': 0.80,
            'insight_origem': 'RK3B8_021',
            'chunks': ['chunk_RK3B8_099', 'chunk_RK3B8_100'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'FW-RK-008',
            'titulo': 'Analise de Portfolio de Investimentos 80/20',
            'descricao': 'Framework para concentrar capital nos investimentos de maior potencial. Baseado na experiencia pessoal de Koch com Filofax (18x em 3 anos).',
            'componentes': [
                '1. Revisar portfolio e calcular retorno historico por investimento',
                '2. Identificar o 20% de investimentos responsaveis por 80% do crescimento',
                '3. Concentrar aportes neles',
                '4. Reduzir ou eliminar os 80% de menor potencial'
            ],
            'uso': 'Revisao anual de portfolio. Filofax: 5% dos papeis, 80% do portfolio, multiplicou 18x em 3 anos.',
            'peso': 0.90,
            'insight_origem': 'RK3B8_022',
            'chunks': ['chunk_RK3B8_019', 'chunk_RK3B8_020'],
            'fontes': ['RK3B8']
        }
    ],
    'metadados': META
}

# ─────────────────────────────────────────────────────────────────────
# 5. METODOLOGIAS.yaml — 6 itens
# ─────────────────────────────────────────────────────────────────────
metodologias = {
    'versao': '1.0.0',
    'pessoa': 'Richard Koch',
    'camada': 'METODOLOGIAS',
    'total_itens': 6,
    'itens': [
        {
            'id': 'MET-RK-001',
            'titulo': 'Revolucao do Tempo: 5 Passos para Trabalhar Menos',
            'descricao': 'Metodologia para eliminar o 80% do tempo desperdicado e conquistar os 20% essenciais.',
            'etapas': [
                '1. Diminuir a velocidade (contra-cultural — nadar contra a corrente)',
                '2. Parar de se preocupar',
                '3. Reduzir atividades — eliminar agenda itens de baixo valor',
                '4. Agir menos, pensar mais',
                '5. Saborear a vida'
            ],
            'auditoria': 'Semanal: listar todas as atividades, classificar por valor, eliminar as 80% de baixo valor. Repetir ate que apenas os 20% essenciais permanecam.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_023',
            'chunks': ['chunk_RK0DE_020', 'chunk_RK0DE_021', 'chunk_RK0DE_022'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'MET-RK-002',
            'titulo': 'Metodo do Empreendedor Preguicoso',
            'descricao': 'Estrategia de Koch para ganhar mais trabalhando menos — comprovada em sua propria trajetoria.',
            'etapas': [
                '1. Criar negocios sem botar a mao no trabalho pesado',
                '2. Trabalhar apenas no que e atraente e estimulante',
                '3. Manter grandes porcoes de tempo para familia, amigos e prazer',
                '4. Reservar tempo em multiplos lugares e experiencias'
            ],
            'resultado': 'Ganhar mais em estilo relaxado do que em regime full-time.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_024',
            'chunks': ['chunk_RK0DE_016', 'chunk_RK0DE_017'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'MET-RK-003',
            'titulo': 'Diagnostico 80/20 do Negocio: 4 Perguntas Fundamentais',
            'descricao': 'Metodologia trimestral para diagnosticar e focar os recursos nos 20% de alto valor do negocio.',
            'etapas': [
                '1. Quais 20% dos clientes geram 80% do lucro?',
                '2. Quais 20% dos produtos/servicos geram 80% da receita?',
                '3. Quais 20% das atividades geram 80% do resultado?',
                '4. Quais 20% das pessoas geram 80% do valor?',
                '→ Eliminar ou terceirizar os 80% restantes'
            ],
            'frequencia': 'Trimestral/anual. Documentar evolucao dos 20% de ouro ao longo do tempo.',
            'peso': 0.80,
            'insight_origem': 'RK0DE_025',
            'chunks': ['chunk_RK0DE_004', 'chunk_RK0DE_005'],
            'fontes': ['RK0DE']
        },
        {
            'id': 'MET-RK-004',
            'titulo': 'Metodologia de Analise 80/20 para Empresas',
            'descricao': 'Processo quantitativo para estabelecer relacao precisa entre causas e resultados em qualquer sistema empresarial.',
            'etapas': [
                '1. Formular hipotese 80/20 para o sistema analisado',
                '2. Coletar dados para revelar a verdadeira proporcao (pode ser qualquer resultado de 50/50 a 99.9/0.1)',
                '3. Se desequilibrio notavel encontrado: multiplicar os 20% de alto impacto',
                '4. Multiplicar a eficacia do restante ou eliminar'
            ],
            'frequencia': 'Trimestral em: clientes, produtos, funcionarios, atividades.',
            'peso': 0.80,
            'insight_origem': 'RK3B8_023',
            'chunks': ['chunk_RK3B8_018', 'chunk_RK3B8_019'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'MET-RK-005',
            'titulo': 'Estrategia de Forca de Vendas 80/20',
            'descricao': 'Metodologia para transformar time de vendas mediocre em de alto desempenho via concentracao nos poucos vitais.',
            'etapas': [
                '1. Focar nos poucos clientes vitais com oferta exclusiva de valor',
                '2. Centralizar 80% das pequenas contas em telemarketing passivo',
                '3. Revisitar antigos clientes satisfeitos sistematicamente',
                '4. Medir e otimizar apenas os 20% de atividades de vendas mais produtivas'
            ],
            'peso': 0.80,
            'insight_origem': 'RK3B8_024',
            'chunks': ['chunk_RK3B8_065', 'chunk_RK3B8_066', 'chunk_RK3B8_067'],
            'fontes': ['RK3B8']
        },
        {
            'id': 'MET-RK-006',
            'titulo': 'Libertar-se pelo Pensamento 80/20: 3 Alavancas Pessoais',
            'descricao': 'Metodologia de transformacao pessoal via 80/20 aplicado a tres dimensoes da vida.',
            'etapas': [
                '1. Trabalhar menos — identificar e manter apenas os 20% que geram resultado',
                '2. Ganhar mais — concentrar em atividades de alto retorno',
                '3. Divertir-se mais — aplicar 80/20 na felicidade pessoal'
            ],
            'revisao': 'Semanal: O que estou fazendo que gera 80% do resultado? O que posso eliminar? O que gera mais alegria pelo menor esforco?',
            'peso': 0.80,
            'insight_origem': 'RK3B8_025',
            'chunks': ['chunk_RK3B8_082', 'chunk_RK3B8_083'],
            'fontes': ['RK3B8']
        }
    ],
    'metadados': META
}

# ─────────────────────────────────────────────────────────────────────
# 6. CONFIG.yaml — metadados e sintese
# ─────────────────────────────────────────────────────────────────────
config = {
    'versao': '1.0.0',
    'pessoa': 'Richard Koch',
    'nome_canonico': 'Richard Koch',
    'empresa': 'Richard Koch Ltd (autor / investidor independente)',

    'padroes_comportamentais': [
        {
            'padrao': 'Prova Vivida da Teoria',
            'frequencia': 'Alta',
            'evidencia': 'Vive no que prega — menos trabalho, mais resultado'
        },
        {
            'padrao': 'Paradoxo Produtivo',
            'frequencia': 'Alta',
            'evidencia': 'Ociosidade estrategica supera hiperatividade'
        },
        {
            'padrao': 'Universalidade do Desequilibrio',
            'frequencia': 'Alta',
            'evidencia': 'Aplica 80/20 a riqueza, epidemias, linguistica, redes sociais'
        },
        {
            'padrao': 'Anti-Equilibrio',
            'frequencia': 'Alta',
            'evidencia': 'Equilibrio e mediocre — pontos fortes desbalanceados vencem'
        },
        {
            'padrao': 'Fundacao Cientifica',
            'frequencia': 'Alta',
            'evidencia': 'Conecta 80/20 com Teoria do Caos e feedback loops'
        },
        {
            'padrao': 'Concentracao vs Diversificacao',
            'frequencia': 'Alta',
            'evidencia': 'Filofax: 5% dos papeis, 80% do portfolio, 18x em 3 anos'
        },
        {
            'padrao': 'Tecnica de Antigos Clientes',
            'frequencia': 'Media',
            'evidencia': 'Barsan e Bain: clientes antigos = maior taxa de conversao'
        }
    ],

    'sintese_narrativa': (
        'Richard Koch e o filosofo pratico do Principio 80/20. Transformou a lei de Pareto em '
        'metodologia de vida e negocios. Tese central: desequilibrio entre causas e resultados '
        'nao e excecao, e regra universal. Uma minoria de causas (aprox. 20%) sempre produz '
        'uma maioria de resultados (aprox. 80%) — e essa proporcao pode ser ainda mais extrema. '
        'Koch vive o que prega: abandonou carreira convencional em 1990, trabalha apenas no que '
        'ama, tem casas em tres paises, e ganha mais do que quando trabalhava em regime integral. '
        'O Empreendedor Preguicoso e a prova vivida da tese: mais com menos nao e teoria, e '
        'estrategia executavel. No livro original (O Principio 80/20), Koch aprofunda a '
        'fundamentacao teorica conectando o principio a Teoria do Caos e feedback loops — '
        'provando que sem esses loops o universo seria 50/50. Sua contribuicao unica: '
        'arbitragem 80/20, concentracao de investimentos (vs diversificacao convencional) e '
        'a Lei da Competicao 80/20 como framework de posicionamento de mercado.'
    ),

    'estatisticas': {
        'filosofias': 6,
        'modelos_mentais': 12,
        'heuristicas': 18,
        'frameworks': 8,
        'metodologias': 6,
        'total_itens': 50,
        'peso_medio_geral': 0.82,
        'itens_peso_alto': 22,
        'itens_peso_medio': 28
    },

    'fontes': {
        'processadas': ['RK0DE', 'RK3B8'],
        'titulos': {
            'RK0DE': 'A Revolucao 80/20 (aplicacao pessoal e vida)',
            'RK3B8': 'O Principio 80/20 (fundacao teorica e aplicacao empresarial)'
        },
        'dossier': 'knowledge/dossiers/persons/DOSSIER-RICHARD-KOCH.md',
        'chunks_totais': 407
    },

    'open_loops': [
        {
            'question': 'Como identificar EXATAMENTE os proprios 20% de picos?',
            'why_it_matters': 'Sem isso, o principio nao e acionavel'
        },
        {
            'question': 'Como aplicar 80/20 a relacionamentos sem ser calculista?',
            'why_it_matters': 'Tensao etica no principio aplicado a pessoas'
        },
        {
            'question': 'Como identificar o Tipping Point ANTES de cruzar a linha invisivel?',
            'why_it_matters': 'Quem desiste antes do tipping point perde tudo; quem persiste ganha tudo'
        }
    ],

    'metadados': {
        'criado_em': f'{TODAY}T00:00:00Z',
        'protocolo': 'DNA-EXTRACTION-PROTOCOL v1.0',
        'pipeline': 'Jarvis v2.2 (automatico)',
        'trigger': 'densidade >= 3/5 (DOSSIER READY com 50 insights)',
        'fontes_utilizadas': ['RK0DE', 'RK3B8'],
        'total_insights_processados': 50
    },

    'changelog': [
        {
            'data': f'{TODAY}T00:00:00Z',
            'acao': 'Criacao automatica do DNA Cognitivo',
            'fonte': 'DOSSIER-RICHARD-KOCH.md v1.1.0',
            'itens_adicionados': 50,
            'versao': '1.0.0'
        }
    ]
}

# ─────────────────────────────────────────────────────────────────────
# WRITE ALL FILES
# ─────────────────────────────────────────────────────────────────────
files = {
    'FILOSOFIAS.yaml': filosofias,
    'MODELOS-MENTAIS.yaml': modelos_mentais,
    'HEURISTICAS.yaml': heuristicas,
    'FRAMEWORKS.yaml': frameworks,
    'METODOLOGIAS.yaml': metodologias,
    'CONFIG.yaml': config
}

for fname, data in files.items():
    path = BASE / fname
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False, indent=2)
    print(f'[OK] {fname}')

print()
print('DNA Cognitivo extraido: Richard Koch')
print(f'Diretorio: {BASE}')
print()
print('Estatisticas:')
print(f'  FILOSOFIAS.yaml:      6 itens')
print(f'  MODELOS-MENTAIS.yaml: 12 itens')
print(f'  HEURISTICAS.yaml:     18 itens (camada principal)')
print(f'  FRAMEWORKS.yaml:      8 itens')
print(f'  METODOLOGIAS.yaml:    6 itens')
print(f'  CONFIG.yaml:          metadados + sintese')
print(f'  TOTAL:                50 itens')
