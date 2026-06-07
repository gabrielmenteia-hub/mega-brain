#!/usr/bin/env bash
# clone-tier-s.sh — Clona os 17 repos Tier S em shallow mode
# Uso: bash clone-tier-s.sh
# Destino: DS-main/DS-main/<nome-do-repo>/
# Estimativa: ~1.5 GB | Tempo: 5-15 min (depende da conexão)

set -euo pipefail

DEST="$(cd "$(dirname "$0")/DS-main" && pwd)"
cd "$DEST"

# Tier S — 17 repos selecionados
declare -A TIER_S=(
  [ant-design]="https://github.com/ant-design/ant-design master"
  [carbon]="https://github.com/carbon-design-system/carbon main"
  [chakra-ui]="https://github.com/chakra-ui/chakra-ui main"
  [fluentui]="https://github.com/microsoft/fluentui master"
  [govuk-design-system]="https://github.com/alphagov/govuk-design-system main"
  [govuk-frontend]="https://github.com/alphagov/govuk-frontend main"
  [headless-ui]="https://github.com/tailwindlabs/headlessui main"
  [lightning-design-system]="https://github.com/salesforce-ux/design-system main"
  [mantine]="https://github.com/mantinedev/mantine master"
  [material-ui]="https://github.com/mui/material-ui master"
  [material-web]="https://github.com/material-components/material-web main"
  [polaris-react]="https://github.com/Shopify/polaris-react main"
  [polaris-tokens]="https://github.com/Shopify/polaris-tokens main"
  [primer-primitives]="https://github.com/primer/primer-primitives main"
  [primer-react]="https://github.com/primer/react main"
  [radix-ui]="https://github.com/radix-ui/primitives main"
  [shadcn-ui]="https://github.com/shadcn-ui/ui main"
)

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

clone_or_update() {
  local name="$1"
  local url="$2"
  local branch="$3"

  if [ -d "$name/.git" ]; then
    echo -e "${YELLOW}[↑] $name${NC} — atualizando..."
    git -C "$name" pull --ff-only --depth 1 origin "$branch" 2>&1 | tail -1
    echo -e "${GREEN}[=] $name${NC} — up-to-date"
  else
    echo -e "${BLUE}[+] $name${NC} — clonando shallow..."
    git clone --depth 1 --single-branch --branch "$branch" \
      --filter=blob:none "$url" "$name" 2>&1 | tail -2
    echo -e "${GREEN}[✓] $name${NC} — clonado"
  fi
}

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  DS-main Clone Tier S — 17 repos                    ║"
echo "║  Destino: $DEST"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

TOTAL=${#TIER_S[@]}
COUNT=0
ERRORS=()

for name in "${!TIER_S[@]}"; do
  read -r url branch <<< "${TIER_S[$name]}"
  COUNT=$((COUNT + 1))
  echo -e "[$COUNT/$TOTAL] Processando $name..."
  if ! clone_or_update "$name" "$url" "$branch"; then
    echo -e "${RED}[x] $name${NC} — erro!"
    ERRORS+=("$name")
  fi
  echo ""
done

echo "══════════════════════════════════════════════════════"
echo "  Concluído: $((TOTAL - ${#ERRORS[@]}))/$TOTAL repos clonados"
if [ ${#ERRORS[@]} -gt 0 ]; then
  echo -e "${RED}  Erros: ${ERRORS[*]}${NC}"
fi
echo "══════════════════════════════════════════════════════"
