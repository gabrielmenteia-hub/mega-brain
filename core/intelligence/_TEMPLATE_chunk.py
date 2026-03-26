"""
TEMPLATE: chunk_XXXX_titulo.py
Substituir: SOURCE_ID, SOURCE_PERSON, SOURCE_TITLE, SOURCE_PATH
"""
from core.intelligence.pipeline_utils import chunk_file, save_chunks, register_source

SOURCE_ID     = "XXXX"
SOURCE_PERSON = "Nome Completo"
SOURCE_TITLE  = "Título do Livro"
SOURCE_PATH   = "inbox/PESSOA/BLUEPRINTS/arquivo.txt"

chunks = chunk_file(SOURCE_PATH, SOURCE_ID, SOURCE_PERSON, SOURCE_TITLE)
added  = save_chunks(chunks, SOURCE_ID)
# register_source() chamado depois do extract, com insights count
