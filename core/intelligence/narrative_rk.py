"""Save narrative for Richard Koch - RK0DE phase"""
import json
from pathlib import Path

NAR_PATH = Path('c:/Users/Gabriel/MEGABRAIN/processing/narratives/NARRATIVES-STATE.json')

if NAR_PATH.exists():
    with open(NAR_PATH, 'r', encoding='utf-8') as f:
        state = json.load(f)
else:
    state = {'narratives_state': {'persons': {}, 'themes': {}, 'version': 'v1'}}

persons = state.setdefault('narratives_state', {}).setdefault('persons', {})

narrative_text = (
    "Richard Koch e o filosofo pratico do Principio 80/20 - autor que transformou a lei de Pareto "
    "em metodologia de vida e negocios. Sua tese central: desequilibrio entre causas e resultados "
    "nao e excecao, e regra universal. Uma minoria de causas (aprox. 20%) sempre produz uma "
    "maioria de resultados (aprox. 80%) - e essa proporcao pode ser ainda mais extrema "
    "(1% gerando 80%).\n\n"
    "Koch vive o que prega: abandonou carreira convencional em 1990, trabalha apenas no que ama "
    "(estimular entusiasmo), tem casas em tres paises, e ganha mais do que quando trabalhava em "
    "regime integral. Seu modelo - o Empreendedor Preguicoso - e a prova vivida da tese: "
    "mais com menos nao e teoria, e estrategia executavel.\n\n"
    "Filosofia central de Koch e dupla: (a) identificar os 20% de ouro - pessoas, atividades, "
    "clientes, metodos - e concentrar ali toda a energia; (b) eliminar os 80% restantes sem culpa. "
    "Nao e sobre fazer mais, e sobre fazer menos, mas melhor e com mais intencao.\n\n"
    "Diferente de gurus de produtividade que pregam gestao de tempo, Koch diz: nao gerencie o "
    "tempo - revolucione-o. Diminua a velocidade. Pense mais, aja menos. O mundo moderno perdeu "
    "o controle da aceleracao e isso e a origem da ineficiencia.\n\n"
    "Nas estrelas de alto desempenho, Koch identifica 6 atributos: ambicao suave, amor pelo que "
    "fazem, desequilibrio nos pontos fortes, especializacao estreita (99% sobre 1%), comunicacao "
    "clara e formula propria. Equilibrio e mediocidade. Pontos fracos nao importam.\n\n"
    "--- Atualizacao 2026-03-09 via RK0DE ---\n\n"
    "Livro 'A Revolucao 80/20' e a versao mais pratica e pessoal do Principio - voltada para "
    "aplicacao na vida cotidiana. Koch expande o conceito para: carreira (20% das empresas geram "
    "80% do crescimento), relacionamentos, uso do tempo, e felicidade pessoal.\n\n"
    "Insight crucial: o melhor da vida e gratuito ou quase. A recompensa de gestos simples - "
    "afeto, natureza, conexao genuina - e desproporcional ao esforco investido. 80/20 aplicado "
    "a felicidade.\n\n"
    "Metodologia da Revolucao do Tempo: diminuir velocidade, eliminar agenda, agir menos pensar "
    "mais, saborear a vida. Contra-intuitivo mas comprovado por Koch na propria trajetoria."
)

if 'Richard Koch' not in persons:
    persons['Richard Koch'] = {
        'narrative': narrative_text,
        'last_updated': '2026-03-09',
        'scope': 'personal',
        'corpus': 'richard_koch',
        'insights_included': [f'chunk_RK0DE_{i:03d}' for i in range(1, 26)],
        'patterns_identified': [
            {'pattern': 'Prova Vivida da Teoria', 'frequency': 'Alta',
             'evidence': 'Vive no que prega - menos trabalho, mais resultado'},
            {'pattern': 'Paradoxo Produtivo', 'frequency': 'Alta',
             'evidence': 'Ociosidade estrategica supera hiperatividade'},
            {'pattern': 'Universalidade do Desequilibrio', 'frequency': 'Alta',
             'evidence': 'Aplica 80/20 a riqueza, epidemias, linguistica, redes sociais'},
            {'pattern': 'Anti-Equilibrio', 'frequency': 'Alta',
             'evidence': 'Equilibrio e mediocre - pontos fortes desbalanceados vencem'}
        ],
        'open_loops': [
            {'question': 'Como identificar EXATAMENTE os proprios 20% de picos?',
             'why_it_matters': 'Sem isso, o principio nao e acionavel'},
            {'question': 'Como aplicar 80/20 a relacionamentos sem ser calculista?',
             'why_it_matters': 'Tensao etica no principio aplicado a pessoas'}
        ],
        'tensions': [
            {'point_a': 'Trabalhar menos para ganhar mais',
             'point_b': 'Exige entusiasmo e especializacao - nao qualquer trabalhador pode aplicar',
             'evidence': 'Koch tem 20+ anos de carreira antes de largar emprego'}
        ],
        'next_questions': [
            'Como escalar o modelo Empreendedor Preguicoso?',
            'Qual e o 80/20 especifico de vendas online?',
            'Como combinar 80/20 com disciplina de execucao?'
        ],
        'sources': ['RK0DE']
    }
else:
    existing = persons['Richard Koch']
    existing['narrative'] += '\n\n--- Atualizacao 2026-03-09 via RK0DE ---\n\n' + narrative_text
    if 'RK0DE' not in existing.get('sources', []):
        existing.setdefault('sources', []).append('RK0DE')
    existing['last_updated'] = '2026-03-09'

with open(NAR_PATH, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print('Narrative salva: Richard Koch')
print(f'Fontes: {persons["Richard Koch"]["sources"]}')
print(f'Patterns: {len(persons["Richard Koch"]["patterns_identified"])}')
