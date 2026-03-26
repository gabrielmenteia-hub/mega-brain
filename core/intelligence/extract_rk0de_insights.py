"""
Extract insights from RK0DE - A Revolucao 80-20 - Richard Koch
25 insights across 5 DNA layers
"""
import json
from pathlib import Path
from datetime import datetime

INSIGHTS_PATH = Path('c:/Users/Gabriel/MEGABRAIN/processing/insights/INSIGHTS-STATE.json')

SOURCE_ID = 'RK0DE'
PERSON = 'Richard Koch'
TODAY = '2026-03-09'

insights = [
    # FILOSOFIAS (3)
    {
        'id': 'RK0DE_001',
        'tipo': '[FILOSOFIA]',
        'titulo': 'O Principio 80/20: Desequilibrio e a Lei Universal',
        'insight': 'Uma pequena minoria de causas (20%) conduz a uma grande maioria de resultados (80%). Essa assimetria nao e excecao — e a regra universal que governa negocios, relacionamentos, riqueza, produtividade e qualquer sistema complexo.',
        'aplicacao': 'Identificar os 20% de ouro em qualquer area antes de agir. Parar de distribuir atencao igualmente entre todas as causas.',
        'prioridade': 'HIGH',
        'confianca': 0.97,
        'chunks': ['chunk_RK0DE_001', 'chunk_RK0DE_004']
    },
    {
        'id': 'RK0DE_002',
        'tipo': '[FILOSOFIA]',
        'titulo': 'Mais com Menos: O Motor do Progresso',
        'insight': 'Toda a historia humana e o progresso economico giram em torno de produzir mais com menos. Identificar e multiplicar os 20% mais produtivos e como ampliar resultados com menos recursos — terra, capital, trabalho e tempo.',
        'aplicacao': 'Questionar sempre: Como posso obter o mesmo resultado usando menos recursos? Eliminar o desperdicio antes de otimizar o esforco.',
        'prioridade': 'HIGH',
        'confianca': 0.95,
        'chunks': ['chunk_RK0DE_010', 'chunk_RK0DE_011']
    },
    {
        'id': 'RK0DE_003',
        'tipo': '[FILOSOFIA]',
        'titulo': 'A Vida Guia o Trabalho, Nao o Contrario',
        'insight': 'Richard Koch abandonou carreira convencional em 1990 para viver de acordo com seus valores primeiro. O trabalho deve ser configurado ao redor da vida desejada — nao adaptar a vida a demanda do trabalho.',
        'aplicacao': 'Definir primeiro como se quer viver, depois construir trabalho que caiba nessa vida. Nao o inverso.',
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK0DE_016']
    },
    # MODELOS MENTAIS (5)
    {
        'id': 'RK0DE_004',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'Grafico Mais com Menos: Alta Recompensa / Baixo Esforco',
        'insight': 'Para qualquer objetivo, sempre existe um caminho de alta recompensa com baixo esforco. Tracar mentalmente um grafico Esforco x Resultado e buscar o ponto onde o esforco e minimo e o retorno e maximo.',
        'aplicacao': 'Antes de agir, mapear as diferentes abordagens para o objetivo e selecionar a de maior retorno por unidade de esforco.',
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK0DE_013']
    },
    {
        'id': 'RK0DE_005',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'Distribuicao Assimet rica e Universal, Nao Excepcional',
        'insight': 'A proporcao 80/20 e apenas a generalizacao de relacoes desproporcionais. Os numeros nao somam necessariamente 100. Pode ser 70/20, 80/10, 90/10 ou 99/1. A realidade frequentemente e ainda mais extrema — 1% das pessoas produz 80%+ dos efeitos.',
        'aplicacao': 'Nao assumir normalidade. Buscar ativamente os extremos — quem/o que gera resultado desproporcional e focar energia ali.',
        'prioridade': 'HIGH',
        'confianca': 0.95,
        'chunks': ['chunk_RK0DE_006', 'chunk_RK0DE_007']
    },
    {
        'id': 'RK0DE_006',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'O Destino 80/20: Pequena Parte Central ao Ser',
        'insight': 'Cada pessoa tem um destino 80/20 — uma pequena parte de tudo disponivel que e central a sua personalidade e desejos mais profundos. Focar nesse destino cria vida com mais proposito do que se preocupar com multiplas questoes.',
        'aplicacao': 'Identificar os proprios 20% de picos: habilidades naturais + paixoes genuinas. Estruturar carreira e vida ao redor desses picos.',
        'prioridade': 'HIGH',
        'confianca': 0.91,
        'chunks': ['chunk_RK0DE_026', 'chunk_RK0DE_027']
    },
    {
        'id': 'RK0DE_007',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'Ocioso Produtivo vs. Hiperativo Ineficiente',
        'insight': 'Uma pessoa ociosa quer fazer o minimo, entao se concentra somente no essencial — e e mais produtiva. Quem trabalha demais esta muito ocupado para identificar o que verdadeiramente importa. Warren Buffett: "beira a letargia", toma pouquissimas decisoes, mas acerta.',
        'aplicacao': 'Criar espaco deliberado de ociosidade estrategica: tempo para pensar sem executar. Modelo Buffett — calmaria e reflexao como vantagem competitiva.',
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK0DE_036', 'chunk_RK0DE_037']
    },
    {
        'id': 'RK0DE_008',
        'tipo': '[MODELO-MENTAL]',
        'titulo': '6 Graus de Separacao: Conectores sao os 20% Cruciais',
        'insight': 'No experimento de Milgram, mais da metade dos pacotes chegou ao destino por apenas 3 pessoas muito bem relacionadas em Boston. Em qualquer rede, 20% dos nos (conectores) geram 80%+ da conectividade e dos resultados.',
        'aplicacao': 'Em networking e vendas: identificar e cultivar os conectores — nao distribuir energia igualmente entre todos os contatos.',
        'prioridade': 'MEDIUM',
        'confianca': 0.88,
        'chunks': ['chunk_RK0DE_007']
    },
    {
        'id': 'RK0DE_009',
        'tipo': '[MODELO-MENTAL]',
        'titulo': 'O Principio da Aceleracao Inversa: Tecnologia Comprime o Tempo',
        'insight': 'A tecnologia deveria liberar tempo mas faz o oposto: acelera a batida do coracao, comprime o tempo. O mundo moderno perdeu o controle da aceleracao. Nadar contra essa corrente e vantagem competitiva.',
        'aplicacao': 'Ser deliberadamente pouco convencional com o uso de tecnologia. Periodos offline programados. Reduzir notificacoes e canais de comunicacao.',
        'prioridade': 'MEDIUM',
        'confianca': 0.87,
        'chunks': ['chunk_RK0DE_022']
    },
    # HEURISTICAS (9)
    {
        'id': 'RK0DE_010',
        'tipo': '[HEURISTICA]',
        'titulo': 'Regra do Nao: Se Nao Envolve Seus 20%, Recuse',
        'insight': 'Regra simples de decisao: se e pedido algo que nao envolve a atividade central propria, a resposta e nao. Simplicidade radical na triagem de compromissos.',
        'aplicacao': 'Definir qual e o proprio "estimular entusiasmo" e usar como filtro unico para aceitar/recusar demandas.',
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK0DE_019']
    },
    {
        'id': 'RK0DE_011',
        'tipo': '[HEURISTICA]',
        'titulo': 'Nao Gerencie o Tempo — Revolucione-o',
        'insight': 'Gestao do tempo pede para ir mais rapido. Revolucao do tempo propoe o oposto: diminuir a velocidade, parar de se preocupar, reduzir atividades. Temos muito tempo — o problema e o desperdicio em atividades de baixo valor.',
        'aplicacao': 'Eliminar itens da agenda antes de otimiza-los. Desligar celular. Deixar reunioes que aborrecem. Conquistar tempo para o que importa.',
        'prioridade': 'HIGH',
        'confianca': 0.94,
        'chunks': ['chunk_RK0DE_020', 'chunk_RK0DE_021']
    },
    {
        'id': 'RK0DE_012',
        'tipo': '[HEURISTICA]',
        'titulo': 'Especializacao Estreita: 99% sobre 1% da Area',
        'insight': 'As estrelas de desempenho sabem muito sobre pouco. Concentrar energia em uma unica area estreita e tornar-se o especialista mais profundo possivel. Conhecer todos os experts do setor. Imitá-los.',
        'aplicacao': 'Definir nicho de especializacao cada vez mais estreito. Conhecer todos os experts. Imitar os que tem o tipo de vida desejada.',
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK0DE_038']
    },
    {
        'id': 'RK0DE_013',
        'tipo': '[HEURISTICA]',
        'titulo': 'O Equilibrio e Mediocre — Foque nos Pontos Fortes',
        'insight': 'Estrelas de desempenho nao sao balanceadas — tem muitos pontos fortes e muitas desvantagens. Os pontos fracos nao importam. O que gera resultados extraordinarios e concentrar nos pontos fortes ate padroes olimpicos.',
        'aplicacao': 'Parar de investir em melhorar fraquezas. Concentrar todo desenvolvimento nos 20% onde ja ha vantagem natural.',
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK0DE_039']
    },
    {
        'id': 'RK0DE_014',
        'tipo': '[HEURISTICA]',
        'titulo': '20% das Empresas Geram 80% do Crescimento e Promocoes',
        'insight': '80% do crescimento vem de 20% das empresas. 80% das promocoes ocorrem em 20% das organizacoes. Para quem voce trabalha pode ser mais importante do que o que voce faz. Colocar-se no fluxo de crescimento de uma estrela em ascensao.',
        'aplicacao': 'Avaliar regularmente: esta empresa esta crescendo? Meu chefe esta progredindo? Se a resposta for nao, mudar antes de otimizar.',
        'prioridade': 'HIGH',
        'confianca': 0.91,
        'chunks': ['chunk_RK0DE_030']
    },
    {
        'id': 'RK0DE_015',
        'tipo': '[HEURISTICA]',
        'titulo': 'Threshold de 14 Dias: Habito Inverte o Custo',
        'insight': 'Qualquer atividade e mais dificil na primeira vez e vai se tornando progressivamente mais facil ate ser mais facil faze-la do que deixar de fazer. Corpo e mente se acostumam a qualquer atividade depois de duas semanas de pratica diaria.',
        'aplicacao': 'Threshold: 14 dias de pratica diaria para automatizar qualquer comportamento desejado. Usar este periodo como compromisso minimo antes de avaliar resultados.',
        'prioridade': 'HIGH',
        'confianca': 0.90,
        'chunks': ['chunk_RK0DE_014']
    },
    {
        'id': 'RK0DE_016',
        'tipo': '[HEURISTICA]',
        'titulo': 'Vender e a Habilidade que Torna Tudo Mais Facil',
        'insight': 'Vender ensina a lidar com rejeicao, comunicar-se eficazmente e negociar. Quem aprende a vender aprende a se vender — habilidade que torna todo o restante da vida mais facil e mais bem-sucedida.',
        'aplicacao': 'Expor-se deliberadamente a situacoes de venda mesmo sem necessidade financeira imediata. Vender algo por alguns meses para desenvolver a habilidade.',
        'prioridade': 'MEDIUM',
        'confianca': 0.88,
        'chunks': ['chunk_RK0DE_041']
    },
    {
        'id': 'RK0DE_017',
        'tipo': '[HEURISTICA]',
        'titulo': 'Entusiasmo > Educacao para Empreendedores',
        'insight': 'Mais da metade dos empreendedores bem-sucedidos nao tem educacao universitaria. O entusiasmo — nao a formacao — e o motor do sucesso empreendedor. Quem ama o que faz naturalmente supera quem apenas se esforça.',
        'aplicacao': 'Avaliar: estou nessa area por entusiasmo genuino ou por obrigacao? Se for obrigacao, buscar o que genuinamente ama antes de investir mais tempo nessa direcao.',
        'prioridade': 'HIGH',
        'confianca': 0.90,
        'chunks': ['chunk_RK0DE_035']
    },
    {
        'id': 'RK0DE_018',
        'tipo': '[HEURISTICA]',
        'titulo': 'O Melhor da Vida e Gratuito ou Quase: Retorno Desproporcional',
        'insight': 'Em vidas privadas, sempre ha atividades que dao muito certo com pouco dinheiro e esforco. Gestos de afeto, observar a natureza, conexoes genuinas — retorno fantastico com custo minimo. A recompensa e desproporcional ao esforco.',
        'aplicacao': 'Mapear as atividades pessoais de maior alegria e menor custo. Aumentar frequencia antes de buscar prazer em consumo de alto custo.',
        'prioridade': 'MEDIUM',
        'confianca': 0.87,
        'chunks': ['chunk_RK0DE_013']
    },
    # FRAMEWORKS (4)
    {
        'id': 'RK0DE_019',
        'tipo': '[FRAMEWORK]',
        'titulo': 'Os 6 Atributos das Estrelas de Desempenho',
        'insight': 'Pessoas de alto desempenho compartilham 6 caracteristicas: (1) Sao ambiciosas, mas de forma natural/suave; (2) Amam o que fazem — entusiasmo, nao esforco; (3) Nao sao perfeitas/balanceadas; (4) Sabem muito sobre pouco; (5) Pensam e comunicam claramente; (6) Desenvolvem formula propria e inimitavel de sucesso.',
        'aplicacao': 'Usar como checklist de auto-avaliacao e criterio de recrutamento. Avaliar candidatos por paixao e clareza de pensamento, nao so por curriculo.',
        'prioridade': 'HIGH',
        'confianca': 0.94,
        'chunks': ['chunk_RK0DE_034', 'chunk_RK0DE_035']
    },
    {
        'id': 'RK0DE_020',
        'tipo': '[FRAMEWORK]',
        'titulo': 'Mapeamento dos 20% de Picos Pessoais (Figuras 5-8)',
        'insight': 'Ferramenta de auto-conhecimento: mapear em grafico (i) 20% de picos de habilidades e interesses e (ii) 20% de picos emocionais e pessoais. Identificar a convergencia. O destino 80/20 esta na interseccao de ambos.',
        'aplicacao': 'Exercicio: listar 10+ habilidades/interesses, pontuar cada, identificar os 20% mais altos. Repetir para qualidades emocionais. Buscar trabalho/negocio na interseccao.',
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK0DE_026', 'chunk_RK0DE_027']
    },
    {
        'id': 'RK0DE_021',
        'tipo': '[FRAMEWORK]',
        'titulo': 'Perguntas 80/20: Diagnostico por Questionamento',
        'insight': 'Para cada area da vida, aplicar perguntas 80/20 para identificar alavancas: Quais 20% das atividades geram 80% dos resultados? Quais 20% dos clientes geram 80% do lucro? Quais 20% das relacoes geram 80% da alegria? A pergunta certa revela o caminho de menor esforco.',
        'aplicacao': 'Criar banco de perguntas 80/20 para diagnostico trimestral de negocio, carreira e vida pessoal.',
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK0DE_019', 'chunk_RK0DE_020']
    },
    {
        'id': 'RK0DE_022',
        'tipo': '[FRAMEWORK]',
        'titulo': 'Analise 80/20 da Carreira: 4 Variaveis Criticas',
        'insight': 'Aplicacoes do 80/20 em carreira: 80% das promocoes vem de 20% dos chefes; 80% dos resultados derivam de 20% das atividades; 80% da experiencia util vem de 20% das organizacoes; 20% do que voce faz cria 80%+ do seu valor.',
        'aplicacao': 'Revisao trimestral: (a) Estou na empresa certa? (b) Trabalho para o chefe certo? (c) Faco as atividades de maior valor? Se nao, trocar antes de otimizar.',
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK0DE_030', 'chunk_RK0DE_031']
    },
    # METODOLOGIAS (4)
    {
        'id': 'RK0DE_023',
        'tipo': '[METODOLOGIA]',
        'titulo': 'Revolucao do Tempo: 5 Passos para Trabalhar Menos',
        'insight': 'Metodologia da Revolucao do Tempo: (1) Diminuir a velocidade; (2) Parar de se preocupar; (3) Reduzir atividades — eliminar agenda itens de baixo valor; (4) Agir menos, pensar mais; (5) Saborear a vida. Nadar contra a corrente da aceleracao.',
        'aplicacao': 'Auditoria semanal: listar todas as atividades, classificar por valor, eliminar as 80% de baixo valor. Repetir ate que apenas os 20% essenciais permanecam.',
        'prioridade': 'HIGH',
        'confianca': 0.92,
        'chunks': ['chunk_RK0DE_020', 'chunk_RK0DE_021', 'chunk_RK0DE_022']
    },
    {
        'id': 'RK0DE_024',
        'tipo': '[METODOLOGIA]',
        'titulo': 'Metodo do Empreendedor Preguicoso de Koch',
        'insight': 'Estrategia de Koch: (1) Criar negocios sem botar a mao no trabalho pesado; (2) Trabalhar apenas no que e atraente e estimulante; (3) Manter grandes porcoes de tempo para familia, amigos e prazer; (4) Reservar tempo em multiplos lugares. Resultado: ganhar mais em estilo relaxado do que em regime full-time.',
        'aplicacao': 'Definir quais partes do negocio o fundador deve tocar pessoalmente e delegar/automatizar o restante antes de escalar.',
        'prioridade': 'HIGH',
        'confianca': 0.91,
        'chunks': ['chunk_RK0DE_016', 'chunk_RK0DE_017']
    },
    {
        'id': 'RK0DE_025',
        'tipo': '[METODOLOGIA]',
        'titulo': 'Diagnostico 80/20 do Negocio: 4 Perguntas Fundamentais',
        'insight': 'Para qualquer negocio: (1) Quais 20% dos clientes geram 80% do lucro? (2) Quais 20% dos produtos/servicos geram 80% da receita? (3) Quais 20% das atividades geram 80% do resultado? (4) Quais 20% das pessoas geram 80% do valor? Eliminar ou terceirizar os 80% restantes.',
        'aplicacao': 'Aplicar trimestral/anualmente. Documentar evolucao dos 20% de ouro. Tomar decisoes de produto, equipe e foco baseadas nessa analise.',
        'prioridade': 'HIGH',
        'confianca': 0.93,
        'chunks': ['chunk_RK0DE_004', 'chunk_RK0DE_005']
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
