#!/usr/bin/env bash
# Sincroniza os repos DS a partir de `repos.tsv`:
#   - se o diretório não existe, clona SHALLOW (--depth 1, single-branch, sem blobs)
#   - se já existe, faz pull --ff-only (mantém shallow)
# Roda em paralelo. Uso: ./update.sh
#
# Shallow rationale: estes são DS de referência para LEITURA (estudo de
# arquitetura/tokens/componentes). Histórico git completo é dispensável e
# multiplica espaço por 50-100x em monorepos pesados (carbon, porsche).

set -u
cd "$(dirname "$0")"

manifest="repos.tsv"
if [ ! -f "$manifest" ]; then
  echo "manifesto não encontrado: $manifest" >&2
  exit 1
fi

sync_repo() {
  local name="$1" url="$2" branch="$3"
  local tmp
  tmp=$(mktemp)
  if [ -d "$name/.git" ]; then
    if git -C "$name" pull --ff-only --depth 1 >"$tmp" 2>&1; then
      if grep -q "Already up to date" "$tmp"; then
        echo "[=] $name"
      else
        echo "[↑] $name"
      fi
      rm -f "$tmp"
      return 0
    fi
    echo "[x] $name (pull)"
    sed 's/^/    /' "$tmp"
    rm -f "$tmp"
    return 1
  else
    if git clone --branch "$branch" --depth 1 --single-branch --filter=blob:none "$url" "$name" >"$tmp" 2>&1; then
      echo "[+] $name"
      rm -f "$tmp"
      return 0
    fi
    echo "[x] $name (clone)"
    sed 's/^/    /' "$tmp"
    rm -f "$tmp"
    return 1
  fi
}
export -f sync_repo

echo "Sincronizando repos a partir de $manifest..."
echo ""

while IFS=$'\t' read -r name url branch; do
  [ -z "${name:-}" ] && continue
  case "$name" in \#*) continue ;; esac
  sync_repo "$name" "$url" "$branch" &
done < "$manifest"
wait

echo ""
echo "Concluído."
echo "Legenda: [+] clonado · [↑] atualizado · [=] up-to-date · [x] erro"
