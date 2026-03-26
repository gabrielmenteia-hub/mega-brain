"""
Extract insights from RK3B8 - O Principio 80/20 - Richard Koch
25 insights across 5 DNA layers
"""
import json
from pathlib import Path

INSIGHTS_PATH = Path('c:/Users/Gabriel/MEGABRAIN/processing/insights/INSIGHTS-STATE.json')

SOURCE_ID = 'RK3B8'
PERSON = 'Richard Koch'
TODAY = '2026-03-09'

insights = [
    # FILOSOFIAS (3)
    {
        'id': 'RK3B8_001',
        'tipo': '[FILOSOFIA]',
        'titulo': 'O Universo e Instavel: Desequilibrio e Auto-Organizacao',
        'insight': (
            'O universo nao e uma linha reta. Teoria do Caos e 80/20 se esclarecem mutuamente: '
            'ambas afirmam que o mundo e desequilibrado e nao-linear. Pequenas forcas energeticas '
            'tentam obter mais do que sua justa parcela. Feedback loops distorcem o equilibrio '
            'e criam a assimetria 80/20. Sem os feedback loops, a distribuicao seria 50/50.'
        ),
        'aplicacao': (
            'Aceitar que desequilibrio e a condicao natural, nao a excecao. '
            'Identificar os feedback loops positivos no proprio negocio e amplificalos.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.96,
        'chunks': ['chunk_RK3B8_009', 'chunk_RK3B8_010']
    },
    {
        'id': 'RK3B8_002',
        'tipo': '[FILOSOFIA]',
        'titulo': 'A Dialetica do 80/20: Eficiencia e Qualidade de Vida sao Opostos Complementares',
        'insight': (
            'O Principio 80/20 tem natureza dual — yin e yang. A eficiencia abre espaco para '
            'a melhoria da vida, enquanto uma vida melhor requer clareza sobre o que e realmente '
            'importante no trabalho e nas atividades. Sao opostos complementares, nao contradicoes.'
        ),
        'aplicacao': (
            'Nao tratar eficiencia e qualidade de vida como trade-off. Aplicar 80/20 em ambas '
            'as dimensoes simultaneamente: quais 20% do trabalho geram valor? Quais 20% da vida '
            'geram alegria?'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK3B8_001', 'chunk_RK3B8_002']
    },
    {
        'id': 'RK3B8_003',
        'tipo': '[FILOSOFIA]',
        'titulo': 'Os Poucos Vitais vs. Os Muitos Triviais: A Batalha Interna',
        'insight': (
            'Toda pessoa e organizacao e resultado de uma coalizada em guerra interna: '
            'os muitos triviais (inercia, ineficacia dominantes) vs. os poucos vitais '
            '(momentos de eficacia, brilho e bom desempenho). A maioria das atividades '
            'resulta em pouco valor. Poucas intervencoes tem impacto massivo.'
        ),
        'aplicacao': (
            'Mapear explicitamente a batalha interna. Identificar quais atividades pertencem '
            'aos poucos vitais e protege-las. Eliminar ou delegar os muitos triviais.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.95,
        'chunks': ['chunk_RK3B8_054', 'chunk_RK3B8_055']
    },
    # MODELOS MENTAIS (5)
    {
        'id': 'RK3B8_004',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'Feedback Loop: Pequenas Vantagens Criam Grandes Assimetrias',
        'insight': (
            'O rico se torna mais rico nao por habilidades superiores, mas porque riqueza gera '
            'riqueza. Peixinhos dourados: ligeiramente maiores capturam alimento desproporcional. '
            'Feedback loops positivos afetam apenas uma pequena minoria das causas — por isso '
            'essa minoria exerce influencia tao desproporcional.'
        ),
        'aplicacao': (
            'Identificar os proprios feedback loops positivos (vantagens que se auto-ampliam) '
            'e investir neles primeiro. Nao desperdicar energia onde nao ha feedback positivo.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.94,
        'chunks': ['chunk_RK3B8_010', 'chunk_RK3B8_011']
    },
    {
        'id': 'RK3B8_005',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'Tipping Point: Antes do Ponto de Virada, Muito Esforco / Pouco Resultado',
        'insight': (
            'Acima de determinado ponto, uma nova forca tem dificuldade para avançar — grande '
            'esforco, pouco resultado. Muitos pioneiros desistem aqui. Se a forca persiste e '
            'cruza a linha invisivel, pequeno esforco extra alcanca grandes resultados. '
            'O ponto de virada e o momento critico.'
        ),
        'aplicacao': (
            'Identificar em qual ponto do ciclo o negocio/produto esta. Se antes do tipping point: '
            'persistir mesmo com baixo retorno aparente. Reconhecer quando ja se cruzou o ponto '
            'e entao amplificar esforco.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK3B8_011', 'chunk_RK3B8_012']
    },
    {
        'id': 'RK3B8_006',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'Analise 80/20 vs. Pensamento 80/20: Dois Modos de Usar o Principio',
        'insight': (
            'Analise 80/20: metodo quantitativo para estabelecer relacao precisa entre '
            'causas e resultados. Coleta dados empiricamente. Pode revelar qualquer resultado '
            'de 50/50 a 99.9/0.1. Pensamento 80/20: reflexao profunda sobre o que importa, '
            'sem necessidade de dados. Mais rapido e acessivel, porem mais sujeito a erro.'
        ),
        'aplicacao': (
            'Usar Analise 80/20 para decisoes de alto impacto (investimentos, clientes, produtos). '
            'Usar Pensamento 80/20 para decisoes do dia-a-dia. Nao confundir os dois.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK3B8_018', 'chunk_RK3B8_019']
    },
    {
        'id': 'RK3B8_007',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'Arbitragem 80/20: Transferir Recursos de Atividades 80% para 20%',
        'insight': (
            'Lucro de arbitragem e enorme porque voce usa o que nao e muito valioso para '
            'produzir algo enormemente valioso, ganhando nas duas pontas. Dois meios: '
            'pessoas (mover 20% das pessoas das atividades 80% para as 20%) e dinheiro '
            '(mover capital das atividades 80% para as 20%).'
        ),
        'aplicacao': (
            'Mapiar explicitamente quais atividades sao 80% (baixo retorno) e quais sao 20% '
            '(alto retorno). Criar plano de realocacao gradual. Dinheiro dos outros em '
            'atividades 20% cria vencedores — em atividades 80% e vicio e risco.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.94,
        'chunks': ['chunk_RK3B8_078', 'chunk_RK3B8_079']
    },
    {
        'id': 'RK3B8_008',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'Complexidade Destroe Valor: Simplicidade e o Antidoto',
        'insight': (
            'Existe tendencia natural das empresas de se tornarem mais complexas. Todas as '
            'organizacoes sao inerentemente ineficientes. O desperdicio se desenvolve na '
            'complexidade; a eficacia exige simplicidade. Grandes melhorias sempre sao '
            'possiveis atuando de maneira diferente e realizando menos.'
        ),
        'aplicacao': (
            'Auditoria de complexidade: mapear todas as atividades e classificar por valor. '
            'Eliminar ou simplificar as de baixo valor antes de otimizar as de alto valor.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK3B8_055', 'chunk_RK3B8_056']
    },
    {
        'id': 'RK3B8_009',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'Concentrar Investimentos: Nao Diversifique, Concentre nos 20%',
        'insight': (
            'Sabedoria convencional: nao coloque todos os ovos na mesma cesta. '
            'Sabedoria 80/20: escolha a cesta cuidadosamente, coloque nela todos os ovos '
            'e tome conta dela como uma aguia. Koch: 3 investimentos (Filofax, Belgo, MSI) '
            '= 20% do patrimonio, mas 80%+ dos ganhos.'
        ),
        'aplicacao': (
            'Em investimentos e alocacao de capital: concentrar em 3-5 posicoes de maximo '
            'conviction. Nao diversificar por precaucao — diversificar oculta os 20% de ouro.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.95,
        'chunks': ['chunk_RK3B8_019', 'chunk_RK3B8_020']
    },
    # HEURISTICAS (9)
    {
        'id': 'RK3B8_010',
        'tipo': '[HEURISTICA]',
        'titulo': 'Os Poucos Clientes Vitais: 20% Geram 80% do Lucro',
        'insight': (
            'Alguns clientes sao essenciais. A maioria nao. Alguns esforcos de vendas sao '
            'maravilhosamente produtivos. A maioria e ineficiente. Canalizar marketing e '
            'vendas para a minoria de clientes potenciais onde voce pode oferecer algo '
            'exclusivo, melhor ou mais valioso.'
        ),
        'aplicacao': (
            'Fazer analise de rentabilidade por cliente. Identificar os 20% mais lucrativos. '
            'Concentrar atencao de vendas, CS e produto neles. Centralizar ou terceirizar '
            'os 80% restantes.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.95,
        'chunks': ['chunk_RK3B8_065', 'chunk_RK3B8_066']
    },
    {
        'id': 'RK3B8_011',
        'tipo': '[HEURISTICA]',
        'titulo': 'Ressuscitar Antigos Clientes: Tecnica Esquecida de Alta Conversao',
        'insight': (
            'Bill Bain voltou ao ultimo cliente que comprara uma biblia e vendeu mais uma. '
            'Nicholas Barsan (corretor de imoveis, $1M/ano em comissoes): 1/3 de vendas '
            'repetidas para o mesmo cliente. Um antigo cliente satisfeito tem alta '
            'probabilidade de voltar a comprar.'
        ),
        'aplicacao': (
            'Criar processo sistematico de reativacao de ex-clientes satisfeitos. '
            'Contato a cada 6-12 meses. Antigos clientes sao 20% com maior taxa de conversao '
            'e menor custo de aquisicao.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK3B8_067', 'chunk_RK3B8_068']
    },
    {
        'id': 'RK3B8_012',
        'tipo': '[HEURISTICA]',
        'titulo': '20% dos Funcionarios Geram 80% do Valor: Alocar Talentos Primeiro',
        'insight': (
            'Em todas as empresas, o excedente real gerado individualmente por funcionario '
            'tende a ser bastante desigual: 80% dos excedentes geralmente sao resultado '
            'do trabalho de 20% dos funcionarios. Dentro de um mesmo funcionario, '
            '80% do valor e criado durante apenas 20% do seu tempo.'
        ),
        'aplicacao': (
            'Identificar os 20% de funcionarios de maior impacto. Colocar 80% do tempo '
            'deles em atividades de alto valor. Nao desperdicar os 20% de superprodutores '
            'em reunioes e burocracia — seus 20% de tempo sao 80% do valor.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK3B8_033', 'chunk_RK3B8_034']
    },
    {
        'id': 'RK3B8_013',
        'tipo': '[HEURISTICA]',
        'titulo': 'Lei da Competicao 80/20: Em Todo Segmento, um Lider Domina',
        'insight': (
            'Em cada segmento de mercado, a lei da competicao 80/20 esta operando. '
            'O lider em cada segmento maximiza receita com minimo de custos e esforcos. '
            'Mercados tendem a se formar por mais segmentos ao longo do tempo. '
            '80% dos lucros resultam de 20% dos segmentos, 20% dos consumidores e 20% dos produtos.'
        ),
        'aplicacao': (
            'Escolher segmento onde se pode ser lider com vantagem defensavel. '
            'Nao tentar competir em todos os segmentos. Dominar um nicho primeiro, '
            'expandir depois.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK3B8_032', 'chunk_RK3B8_033']
    },
    {
        'id': 'RK3B8_014',
        'tipo': '[HEURISTICA]',
        'titulo': 'Alianças so com Pessoas 20%: Qualidade sobre Quantidade',
        'insight': (
            'Fazer alianças intensivamente, mas so com pessoas 20% e com aqueles que '
            'serao aliados poderosos. Depois, tentar aliar a propria alianca a outras '
            'pessoas e oportunidades 20%. Alianças com pessoas 80% ocupam espaco '
            'que deveria ser dos 20%.'
        ),
        'aplicacao': (
            'Avaliar cada parceria/colaboracao pelo criterio 80/20: esta pessoa e uma '
            'das 20% que amplificam resultados? Se nao, nao investir tempo e energia '
            'na relacao de negocios.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.91,
        'chunks': ['chunk_RK3B8_079']
    },
    {
        'id': 'RK3B8_015',
        'tipo': '[HEURISTICA]',
        'titulo': 'Cortar as Atividades 80% e Imperativo: Tempo 80% Expulsa o 20%',
        'insight': (
            'O tempo 80% expulsa o 20%. Os aliados 80% ocupam espaco dos 20%. '
            'Os ativos 80% prejudicam os resultados dos 20%. Estar em organizacoes '
            'e lugares 80% impede estar nos 20%. A energia mental gasta em atividades '
            '80% deixa de ser investida em projetos 20%.'
        ),
        'aplicacao': (
            'Cortar as 80% impiedosamente. Nao ha versao suavizada desta regra. '
            'Cada elemento 80% mantido por inercua, culpa ou convencao esta '
            'ativamente sabotando os 20%.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.94,
        'chunks': ['chunk_RK3B8_080']
    },
    {
        'id': 'RK3B8_016',
        'tipo': '[HEURISTICA]',
        'titulo': 'Roubar Ideias 20% de Outros Setores e Aplicar no Proprio Nicho',
        'insight': (
            'Inovar nas atividades 20% roubando ideias 20% de tudo que puder: outras '
            'pessoas, outros produtos, outros setores, outras esferas intelectuais, '
            'outros paises. Aplicar no proprio quintal 20%. '
            'A melhor inovacao e adaptacao cross-setor de pratica de alto impacto.'
        ),
        'aplicacao': (
            'Criar pratica de observacao sistematica de outros setores. '
            'Identificar quais praticas sao os 20% em outros dominios e testar '
            'adaptacao no proprio negocio.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.90,
        'chunks': ['chunk_RK3B8_080']
    },
    {
        'id': 'RK3B8_017',
        'tipo': '[HEURISTICA]',
        'titulo': 'Usar Alavancagem so em Atividades 20%: Nos 80% e Risco Puro',
        'insight': (
            'Dinheiro dos outros, usado para atividades 80%, e viciante, perigoso e '
            'muito arriscado. Ja o dinheiro dos outros, quando aplicado nas atividades '
            '20%, cria vencedores e, de forma justa, torna voce o maior deles. '
            'O risco de alavancar 20% e muito mais baixo do que o percebido.'
        ),
        'aplicacao': (
            'Regra de ouro: alavancagem apenas onde ha conviccao de estar nas atividades 20%. '
            'Nunca alavancar para compensar incerteza ou por pressao de retorno.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK3B8_079']
    },
    {
        'id': 'RK3B8_018',
        'tipo': '[HEURISTICA]',
        'titulo': 'Reducao de Custos pela Simplicidade: Tres Conceitos 80/20',
        'insight': (
            'Tecnicas eficazes de reducao de custos usam tres conceitos 80/20: '
            '(1) simplicidade, pela eliminacao das atividades nao lucrativas; '
            '(2) foco em poucos pontos-chave de melhoria (os 20%); '
            '(3) comparacao de desempenho. Nao enfrentar tudo com o mesmo esforco — '
            'reducao de custos e cara!'
        ),
        'aplicacao': (
            'Identificar as areas que sao os 20% do negocio com maior potencial de '
            'impacto. Concentrar a reducao de custos nessas areas. '
            'Ignorar os 80% restantes ou terceirizar.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.91,
        'chunks': ['chunk_RK3B8_055', 'chunk_RK3B8_056']
    },
    # FRAMEWORKS (4)
    {
        'id': 'RK3B8_019',
        'tipo': '[FRAMEWORK]',
        'titulo': 'Como Agir 80/20: 6 Principios de Acao',
        'insight': (
            'Framework de acao 80/20: (1) Identificar os 20% de melhor resultado; '
            '(2) Fazer alianças so com pessoas/oportunidades 20%; '
            '(3) Explorar a arbitragem — transferir recursos dos 80% para os 20%; '
            '(4) Inovar nas atividades 20% roubando ideias de outros setores; '
            '(5) Cortar impiedosamente as atividades 80%; '
            '(6) Usar alavancagem apenas nos 20%.'
        ),
        'aplicacao': (
            'Usar como roteiro de decisao estrategica trimestral. Cada acao de alto '
            'impacto deve mapiar para um desses 6 principios.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.95,
        'chunks': ['chunk_RK3B8_078', 'chunk_RK3B8_079', 'chunk_RK3B8_080']
    },
    {
        'id': 'RK3B8_020',
        'tipo': '[FRAMEWORK]',
        'titulo': 'Diagnostico de Segmentacao: Lei da Competicao 80/20',
        'insight': (
            'Framework para analise de mercado: (1) Identificar todos os segmentos '
            'de produto/cliente; (2) Calcular 80% dos lucros que vem de 20% dos '
            'segmentos; (3) Avaliar em quais segmentos a empresa e lider; '
            '(4) Concentrar recursos nos segmentos lucrativos + lideranca. '
            'Em cada segmento, o lider maximiza receita com minimo de custo.'
        ),
        'aplicacao': (
            'Mapear todos os segmentos produto x cliente. Calcular margem por segmento. '
            'Identificar os 20% de maior margem. Concentrar recursos de produto, vendas '
            'e marketing nos segmentos 20%.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK3B8_032', 'chunk_RK3B8_033']
    },
    {
        'id': 'RK3B8_021',
        'tipo': '[FRAMEWORK]',
        'titulo': 'Perguntas 80/20 para Auto-Descoberta de Talentos',
        'insight': (
            'Para identificar seus 20% superiores: (1) O que voce faz melhor do que 80% '
            'das pessoas em apenas 20% do tempo? (2) O que voce conquista em 20% do tempo '
            'que outros demoram 80%? (3) Se voce pudesse medir a alegria, o que aproveitaria '
            'mais do que 95% dos colegas? (4) O que voce faria melhor do que 95% das pessoas?'
        ),
        'aplicacao': (
            'Exercicio de auto-descoberta: responder cada pergunta considerando toda a '
            'trajetoria — profissional, academica, de hobbyista. As respostas existem, '
            'mesmo que nao sejam obvias.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK3B8_099', 'chunk_RK3B8_100']
    },
    {
        'id': 'RK3B8_022',
        'tipo': '[FRAMEWORK]',
        'titulo': 'Analise de Portfolio de Investimentos 80/20',
        'insight': (
            '80% do crescimento da maioria dos portfolios de longo prazo resulta de menos '
            'de 20% dos investimentos. E crucial identificar bem esses 20% e concentrar '
            'o maximo possivel de investimento neles. Koch: Filofax (5% dos papeis, '
            '80% do portfolio) multiplicou 18x em 3 anos.'
        ),
        'aplicacao': (
            'Revisar portfolio anualmente. Identificar quais investimentos pertencem '
            'ao 20% de ouro. Concentrar aportes neles. Reduzir ou eliminar os 80% '
            'de menor potencial.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.94,
        'chunks': ['chunk_RK3B8_019', 'chunk_RK3B8_020']
    },
    # METODOLOGIAS (4)
    {
        'id': 'RK3B8_023',
        'tipo': '[METODOLOGIA]',
        'titulo': 'Metodologia de Analise 80/20 para Empresas',
        'insight': (
            'Processo: (1) Formular hipotese 80/20 para o sistema analisado; '
            '(2) Coletar dados para revelar a verdadeira proporcao (pode ser qualquer '
            'resultado de 50/50 a 99.9/0.1); (3) Se desequilibrio notavel encontrado: '
            'multiplicar os 20% de alto impacto; (4) Multiplicar a eficacia do restante '
            'ou eliminar.'
        ),
        'aplicacao': (
            'Aplicar trimestralmente em: clientes, produtos, funcionarios, atividades. '
            'Documentar evolucao do desequilibrio ao longo do tempo. '
            'Desequilibrio crescente pode indicar vantagem competitiva em acumulacao.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK3B8_018', 'chunk_RK3B8_019']
    },
    {
        'id': 'RK3B8_024',
        'tipo': '[METODOLOGIA]',
        'titulo': 'Estrategia de Forca de Vendas 80/20',
        'insight': (
            'Para transformar vendedores mediocres em bons e bons em superestrelas: '
            '(1) Focar nos poucos clientes vitais com oferta exclusiva de valor; '
            '(2) Centralizar 80% das pequenas contas em telemarketing passivo; '
            '(3) Revisitar antigos clientes satisfeitos sistematicamente; '
            '(4) Medir e otimizar apenas os 20% de atividades de vendas mais produtivas.'
        ),
        'aplicacao': (
            'Criar playbook de vendas baseado em 80/20: '
            'quais 20% das atividades de vendas geram 80% das conversoes? '
            'Eliminar as demais ou automatizar.'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK3B8_065', 'chunk_RK3B8_066', 'chunk_RK3B8_067']
    },
    {
        'id': 'RK3B8_025',
        'tipo': '[METODOLOGIA]',
        'titulo': 'Libertar-se pelo Pensamento 80/20: 3 Alavancas Pessoais',
        'insight': (
            'Metodologia de transformacao pessoal via 80/20: '
            '(1) Trabalhar menos — identificar e manter apenas os 20% que geram resultado; '
            '(2) Ganhar mais — concentrar em atividades de alto retorno; '
            '(3) Divertir-se mais — aplicar 80/20 na felicidade pessoal. '
            'O unico preco: absorver, digerir e elaborar o principio para os proprios propositos.'
        ),
        'aplicacao': (
            'Aplicar as 3 perguntas semanalmente: O que estou fazendo que gera 80% do '
            'resultado? O que posso eliminar? O que gera mais alegria pelo menor esforco?'
        ),
        'prioridade': 'HIGH',
        'confianca': 0.91,
        'chunks': ['chunk_RK3B8_082', 'chunk_RK3B8_083']
    },
]

# Load state
with open(INSIGHTS_PATH, 'r', encoding='utf-8') as f:
    state = json.load(f)

persons = state.setdefault('insights_state', {}).setdefault('persons', {})

if PERSON not in persons:
    persons[PERSON] = []

existing_ids = {i['id'] for i in persons[PERSON]} if isinstance(persons[PERSON], list) else set()

added = 0
for ins in insights:
    if ins['id'] not in existing_ids:
        obj = {
            'id': ins['id'],
            'tipo': ins['tipo'],
            'titulo': ins['titulo'],
            'insight': ins['insight'],
            'aplicacao_pratica': ins['aplicacao'],
            'fonte': SOURCE_ID,
            'pessoa': PERSON,
            'prioridade': ins['prioridade'],
            'confianca': ins['confianca'],
            'chunks': ins['chunks'],
            'data': TODAY
        }
        persons[PERSON].append(obj)
        added += 1

state['insights_state'].setdefault('change_log', []).append({
    'data': TODAY,
    'operacao': 'EXTRACTION',
    'source_id': SOURCE_ID,
    'pessoa': PERSON,
    'insights_adicionados': added
})

with open(INSIGHTS_PATH, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

total = len(persons[PERSON])
print(f'Insights adicionados: {added}')
print(f'Total Richard Koch: {total}')

from collections import Counter
tipos = Counter(i['tipo'] for i in persons[PERSON])
for t, c in sorted(tipos.items()):
    print(f'  {t}: {c}')
