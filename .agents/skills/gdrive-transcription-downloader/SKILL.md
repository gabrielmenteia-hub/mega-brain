# GDRIVE TRANSCRIPTION DOWNLOADER SKILL

---
name: gdrive-download
description: Baixa transcrições .docx do Google Drive via OAuth e converte para .txt
version: 2.0.0
author: JARVIS
created: 2026-01-08
updated: 2026-01-08
triggers:
  - baixar transcrições
  - download drive
  - extrair transcrições
  - baixar docx
  - gdrive download
---

## PROPÓSITO

Esta skill automatiza o download de transcrições .docx do Google Drive, extração de texto e salvamento como .txt no INBOX do Mega Brain.

---

## ⚠️ REGRA CRÍTICA: EVITAR DUPLICATAS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HIERARQUIA DE TRANSCRIÇÕES - BAIXAR APENAS UMA POR VÍDEO                   │
│                                                                             │
│  Quando uma pasta no Drive tem estrutura com subpastas:                     │
│                                                                             │
│  📂 Pasta Principal/                                                        │
│  ├── 📄 video1.docx          ← Transcrição SIMPLES (só áudio)              │
│  ├── 📄 video2.docx                                                         │
│  └── 📂 Transcrição Visual + Verbal/                                        │
│      ├── 📄 video1.docx      ← Transcrição COMPLETA (áudio + tela)         │
│      └── 📄 video2.docx                                                     │
│                                                                             │
│  REGRA: Priorizar Visual+Verbal, ignorar simples se ambas existem          │
│                                                                             │
│  ALGORITMO:                                                                 │
│  1. Listar TODOS os arquivos (raiz + subpastas)                            │
│  2. Identificar duplicatas pelo nome base do vídeo                         │
│  3. Se duplicata existe:                                                   │
│     - Manter apenas o da pasta "Visual + Verbal"                           │
│     - Descartar o da raiz                                                  │
│  4. Se não há duplicata: baixar normalmente                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Por que isso importa:
- **151 vídeos** podem virar **302 arquivos** se baixar ambas versões
- Isso **infla artificialmente** os números
- A versão Visual+Verbal é **superior** (captura slides, texto na tela)
- Duplicatas poluem o INBOX e confundem o Pipeline

## QUANDO USAR

1. **Fase 1 - Download:** Quando precisar baixar transcrições faltantes
2. **Novos materiais:** Quando novas transcrições forem adicionadas ao Drive
3. **Retry de falhas:** Quando downloads anteriores falharam
4. **Atualização de inventário:** Após adicionar novos cursos/fontes

## ARQUITETURA

```
┌─────────────────────────────────────────────────────────────────┐
│                    GDRIVE DOWNLOADER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INVENTÁRIO                SCRIPT                   INBOX       │
│  ┌─────────┐              ┌─────────┐             ┌─────────┐  │
│  │ JSON    │─────────────▶│ OAuth   │────────────▶│ .txt    │  │
│  │ fileIDs │              │ python  │             │ files   │  │
│  └─────────┘              └─────────┘             └─────────┘  │
│                                                                 │
│  system/               scripts/                 inbox/    │
│  DRIVE-TRANS...          download_all...          [FONTE]/      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## COMPONENTES

### 1. Inventário de Transcrições
**Localização:** `system/DRIVE-TRANSCRIPTIONS-INVENTORY.json`

```json
{
  "courses": {
    "COURSE_KEY": {
      "folder": "DESTINATION/PATH",
      "count": N,
      "files": [
        {"id": "GOOGLE_DRIVE_FILE_ID", "name": "filename.docx"}
      ]
    }
  }
}
```

### 2. Script de Download
**Localização:** `scripts/download_all_transcriptions.py`

**Dependências:**
- python-docx (`pip install python-docx`)
- google-api-python-client (via gdrive_manager)

**Autenticação:**
- OAuth2 via `scripts/gdrive_manager.py`
- Token salvo em `~/.config/moga-brain-gdrive/token.json`

### 3. Sistema de Checkpoint
**Localização:** `.Codex/mission-control/DOWNLOAD-CHECKPOINT.json`

Persiste:
- IDs de arquivos completados
- Arquivos que falharam (para retry)
- Último curso processado

## COMANDOS

### Listar cursos disponíveis
```bash
# From the project root
python3 scripts/download_all_transcriptions.py --list
```

### Baixar todos os cursos
```bash
python3 scripts/download_all_transcriptions.py --all
```

### Baixar curso específico
```bash
python3 scripts/download_all_transcriptions.py --course COURSE_KEY
```

### Continuar de onde parou (resume)
```bash
python3 scripts/download_all_transcriptions.py --all --resume
```

## CURSOS MAPEADOS

| Course Key | Destino | Count |
|------------|---------|-------|
| SALES_TRAINING_BR | COLE GORDON/COURSES | 59 |
| JEREMY_HAYNES_SALES_TRAINING | JEREMY HAYNES/COURSES | 14 |
| JEREMY_MINER_7TH_LEVEL | JEREMY MINER/COURSES | 40 |
| ALEX_HORMOZI | ALEX HORMOZI/MARKETING | 2 |
| JEREMY_HAYNES_PROGRAM | JEREMY HAYNES PROGRAM/COURSES | 2 |
| COLE_GORDON_EXTRAS | COLE GORDON/MASTERMINDS | 6 |

## FLUXO DE EXECUÇÃO

```
┌─────────────────────────────────────────────────────────────────┐
│  1. VERIFICAR INVENTÁRIO                                        │
│     └─ Ler system/DRIVE-TRANSCRIPTIONS-INVENTORY.json        │
├─────────────────────────────────────────────────────────────────┤
│  2. CARREGAR CHECKPOINT                                         │
│     └─ Verificar .Codex/mission-control/DOWNLOAD-CHECKPOINT    │
├─────────────────────────────────────────────────────────────────┤
│  3. AUTENTICAR OAUTH                                            │
│     └─ Via gdrive_manager.get_drive_service()                   │
├─────────────────────────────────────────────────────────────────┤
│  4. PARA CADA ARQUIVO:                                          │
│     ├─ Skip se já completado (checkpoint)                       │
│     ├─ Skip se arquivo já existe no destino                     │
│     ├─ Download .docx do Drive (binary)                         │
│     ├─ Extrair texto via python-docx                            │
│     ├─ Salvar como .txt no INBOX                                │
│     └─ Atualizar checkpoint                                     │
├─────────────────────────────────────────────────────────────────┤
│  5. GERAR SUMÁRIO                                               │
│     └─ Downloaded / Skipped / Failed                            │
└─────────────────────────────────────────────────────────────────┘
```

## TROUBLESHOOTING

### Token expirado
O script renova automaticamente. Se persistir:
```bash
rm ~/.config/moga-brain-gdrive/token.json
# Re-executar script (abrirá browser para autenticar)
```

### Broken pipe errors
Arquivos grandes ou conexão instável. O checkpoint preserva progresso.
```bash
# Re-executar com resume
python3 scripts/download_all_transcriptions.py --all --resume
```

### Arquivo não encontrado no Drive
Verificar se o fileId está correto no inventário.
```bash
# Buscar arquivo pelo ID
python3 -c "
from SCRIPTS.gdrive_manager import get_drive_service
svc = get_drive_service()
print(svc.files().get(fileId='FILE_ID_HERE').execute())
"
```

## ADICIONAR NOVOS CURSOS

1. Identificar pasta no Google Drive
2. Listar arquivos .docx com seus IDs
3. Adicionar ao inventário JSON:
```json
"NEW_COURSE_KEY": {
  "folder": "FONTE/SUBPASTA",
  "count": N,
  "files": [...]
}
```
4. Mapear no script (COURSE_FOLDERS dict)
5. Executar download

## INTEGRAÇÃO COM PIPELINE

Após download, os arquivos .txt estão prontos para:
1. **Fase 2.5 - Tagging:** Adicionar [TAG] aos nomes
2. **Fase 3 - De-Para:** Validar planilha vs computador
3. **Fase 4 - Pipeline:** Processar chunks/insights

## MÉTRICAS DE SUCESSO

```
✅ 149/149 arquivos do inventário
✅ 0 falhas permanentes
✅ Checkpoint preservado para retry
✅ Estrutura de pastas correta no INBOX
```

## HISTÓRICO

| Data | Ação | Resultado |
|------|------|-----------|
| 2026-01-08 | Download inicial completo | 149 arquivos |
| 2026-01-05 | Criação do inventário | 149 entries |

---

**JARVIS SKILL v1.0.0**
*Automatizando downloads do Google Drive para o Mega Brain*
