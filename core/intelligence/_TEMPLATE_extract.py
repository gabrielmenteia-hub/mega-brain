"""
TEMPLATE: extract_XXXX_insights.py
Substituir: SOURCE_ID, SOURCE_PERSON, SOURCE_TITLE, SOURCE_PATH, CHUNKS_ADDED, insights list
"""
from core.intelligence.pipeline_utils import save_insights, register_source, print_distribution

SOURCE_ID     = "XXXX"
SOURCE_PERSON = "Nome Completo"
SOURCE_TITLE  = "Título do Livro"
SOURCE_PATH   = "inbox/PESSOA/BLUEPRINTS/arquivo.txt"
CHUNKS_ADDED  = 0  # preencher após rodar o chunk script

insights = [
    {
        "id": "XXXX-001",
        "tipo": "[FILOSOFIA]",           # [FILOSOFIA] [MODELO-MENTAL] [HEURISTICA] [FRAMEWORK] [METODOLOGIA]
        "titulo": "Título do Insight",
        "insight": "Descrição detalhada do insight extraído do material.",
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_XXXX_010"],
        "tags": ["tag1", "tag2"]
    },
    # ... mais 24 insights
]

added = save_insights(SOURCE_PERSON, insights, SOURCE_ID, SOURCE_TITLE)
register_source(SOURCE_PATH, SOURCE_ID, SOURCE_PERSON, SOURCE_TITLE, CHUNKS_ADDED, added)
print_distribution(insights)
