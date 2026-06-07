# Setup em máquina nova — Mega Brain

Guia passo-a-passo para restaurar todo o Mega Brain em um PC diferente.

## Pré-requisitos a instalar

| Ferramenta | Versão | Como instalar (Windows) |
|---|---|---|
| **Python** | 3.10+ | https://python.org → adicione ao PATH |
| **Node.js** | 18+ | https://nodejs.org → adicione `C:\Program Files\nodejs` ao PATH |
| **Git** | 2.40+ | https://git-scm.com |
| **GitHub CLI** | 2.x | `winget install GitHub.cli` |
| **VSCode** (opcional) | — | https://code.visualstudio.com |
| **Claude Code** | — | Extensão VSCode ou app desktop |
| **rtk** (opcional) | 0.38+ | `cargo install rtk` (token saver) |
| **Tesseract** (opcional) | — | Para OCR de PDFs escaneados |

## 1. Autenticar GitHub CLI

```bash
gh auth login
# Escolha: GitHub.com → HTTPS → Login com browser
```

## 2. Clonar todos os repos

```powershell
mkdir D:\MEGABRAIN
cd D:\

git clone https://github.com/gabrielmenteia-hub/mega-brain MEGABRAIN
cd MEGABRAIN
git submodule update --init --recursive

cd D:\
git clone https://github.com/gabrielmenteia-hub/mega-brain-data
```

## 3. Restaurar Layer 3 (dados pessoais)

```powershell
xcopy /E /I /Y D:\mega-brain-data\inbox       D:\MEGABRAIN\inbox
xcopy /E /I /Y D:\mega-brain-data\knowledge   D:\MEGABRAIN\knowledge
xcopy /E /I /Y D:\mega-brain-data\artifacts   D:\MEGABRAIN\artifacts
xcopy /E /I /Y D:\mega-brain-data\logs        D:\MEGABRAIN\logs
xcopy /E /I /Y D:\mega-brain-data\persons     D:\MEGABRAIN\agents\persons
```

## 4. Instalar dependências

```powershell
cd D:\MEGABRAIN

pip install -r requirements.txt
npm install

pip install -r EvoTwin\backend\requirements.txt
pip install -r Simplex\backend\requirements.txt

cd EvoTwin\frontend && npm install && cd ..\..
cd Simplex\frontend && npm install && cd ..\..
```

## 5. Configurar `.env`

API keys NÃO estão no repo — configure manualmente.

```bash
cd D:\MEGABRAIN
# Abra Claude Code aqui e rode:
/setup
```

O wizard pede:
- **OPENAI_API_KEY** (obrigatório — Whisper)
- **VOYAGE_API_KEY** (recomendado — embeddings RAG)
- **ANTHROPIC_API_KEY** (não necessário com Claude Code)
- **GOOGLE_CLIENT_ID/SECRET** (opcional — Drive)
- **ELEVENLABS_API_KEY** (opcional — áudio Boardroom)

Submódulos têm `.env.example` próprios:
- `EvoTwin\frontend\.env.local` — `NEXT_PUBLIC_API_URL`
- `Simplex\frontend\.env.local` — Supabase URL, anon key, API URL
- `Simplex\backend\.env` — config Postgres/Supabase

## 6. Validar

```powershell
rtk --version
node --version
python --version
gh auth status

# Claude Code:
/jarvis-briefing
```

## 7. (Opcional) Migrar memória do JARVIS

Memória persistente fica em:
```
C:\Users\<user>\.claude\projects\d--MEGABRAIN\memory\
```

Esta pasta NÃO está no repo. Você pode:
- Copiar manualmente do PC antigo (preserva memórias)
- Recomeçar limpa (JARVIS reconstrói com uso)

## Sincronização contínua

Após trabalho significativo:

```powershell
# Código (Claude faz quando você pede)
cd D:\MEGABRAIN
git add . && git commit -m "..." && git push

# Dados (manual, periódico)
cd D:\mega-brain-data
robocopy D:\MEGABRAIN\inbox       inbox       /MIR
robocopy D:\MEGABRAIN\knowledge   knowledge   /MIR
robocopy D:\MEGABRAIN\artifacts   artifacts   /MIR
robocopy D:\MEGABRAIN\logs        logs        /MIR
robocopy D:\MEGABRAIN\agents\persons persons  /MIR
git add -A
git commit -m "sync: snapshot"
git push
```

## Repos relacionados

| Repo | Visibilidade | Propósito |
|---|---|---|
| [mega-brain](https://github.com/gabrielmenteia-hub/mega-brain) | Public | Engine, agentes, skills, hooks |
| [mega-brain-data](https://github.com/gabrielmenteia-hub/mega-brain-data) | 🔒 Private | Layer 3 (inbox, knowledge, dossiês) |
| [evotwin](https://github.com/gabrielmenteia-hub/evotwin) | 🔒 Private | Submódulo EvoTwin |
| [simplex](https://github.com/gabrielmenteia-hub/simplex) | 🔒 Private | Submódulo Simplex |
| [anti-procrastination](https://github.com/gabrielmenteia-hub/anti-procrastination) | Private | One Day app |

## Solução de problemas

| Problema | Solução |
|---|---|
| `rtk: command not found` | Adicionar `%USERPROFILE%\.cargo\bin` ao PATH |
| `node: command not found` | Adicionar `C:\Program Files\nodejs` ao PATH |
| Hook Python falha | Verificar Python 3.10+ no PATH |
| Submódulos vazios | `git submodule update --init --recursive` |
| Git push bloqueado | Verificar `.claude\settings.json` deny rules |
