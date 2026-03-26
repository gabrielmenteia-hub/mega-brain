"""Update narrative and dossier for Richard Koch - RK3B8"""
import json
from pathlib import Path

NAR_PATH = Path('c:/Users/Gabriel/MEGABRAIN/processing/narratives/NARRATIVES-STATE.json')

with open(NAR_PATH, 'r', encoding='utf-8') as f:
    state = json.load(f)

persons = state['narratives_state']['persons']
person = persons['Richard Koch']

update = (
    "\n\n--- Atualizacao 2026-03-09 via RK3B8 ---\n\n"
    "'O Principio 80/20' (livro original, mais tecnico) expande a teoria com fundacao "
    "cientifica: a Teoria do Caos esclarece o 80/20. O universo e instavel por design — "
    "feedback loops distorcem o equilibrio e criam assimetria. Sem feedback loops, a "
    "distribuicao seria 50/50. Com eles, chegamos ao 80/20 ou mais extremo.\n\n"
    "Koch introduz dois modos de usar o principio: Analise 80/20 (quantitativa, empirica) "
    "e Pensamento 80/20 (reflexivo, qualitativo). Sao complementares — um para decisoes de "
    "alto impacto, outro para o cotidiano.\n\n"
    "Aplicacoes em negocios: lei da competicao 80/20 (em cada segmento, um lider domina); "
    "20% dos clientes geram 80% do lucro; 20% dos funcionarios geram 80% do valor; "
    "arbitragem 80/20 (transferir recursos de atividades de baixo para alto retorno).\n\n"
    "Insight sobre investimentos: concentrar nos melhores, nao diversificar. Koch prova "
    "com Filofax: 5% dos papeis, 80% do portfolio, multiplicou 18x em 3 anos. "
    "Dinheiro dos outros em atividades 20% cria vencedores. Em atividades 80% e risco puro.\n\n"
    "Conceito central de Tipping Point: antes do ponto de virada, muito esforco / pouco "
    "resultado. Muitos desistem aqui. Quem persiste e cruza a linha invisivel: pouco "
    "esforco extra alcanca resultados enormes.\n\n"
    "Tecnica de vendas esquecida: ressuscitar antigos clientes satisfeitos. Bill Bain "
    "vendendo biblias voltou ao ultimo cliente — e vendeu mais uma. Nicholas Barsan "
    "($1M/ano em comissoes): 1/3 de vendas repetidas para o mesmo cliente."
)

person['narrative'] += update
if 'RK3B8' not in person.get('sources', []):
    person['sources'].append('RK3B8')
person['last_updated'] = '2026-03-09'

# Add new insights_included
new_chunks = [f'chunk_RK3B8_{i:03d}' for i in range(1, 26)]
person['insights_included'].extend(new_chunks)

# Add new patterns
person['patterns_identified'].extend([
    {'pattern': 'Fundacao Cientifica', 'frequency': 'Alta',
     'evidence': 'Conecta 80/20 com Teoria do Caos e feedback loops'},
    {'pattern': 'Concentracao vs Diversificacao', 'frequency': 'Alta',
     'evidence': 'Filofax: 5% dos papeis, 80% do portfolio, 18x em 3 anos'},
    {'pattern': 'Tecnica de Antigos Clientes', 'frequency': 'Media',
     'evidence': 'Barsan e Bain: clientes antigos = maior taxa de conversao'}
])

# Add new open loops
person['open_loops'].append({
    'question': 'Como identificar o Tipping Point ANTES de cruzar a linha invisivel?',
    'why_it_matters': 'Quem desiste antes do tipping point perde tudo; quem persiste ganha tudo'
})

with open(NAR_PATH, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print('Narrative atualizada: Richard Koch + RK3B8')
print(f'Fontes: {person["sources"]}')
print(f'Patterns total: {len(person["patterns_identified"])}')
print(f'Open loops total: {len(person["open_loops"])}')
