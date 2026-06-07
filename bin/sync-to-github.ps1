# sync-to-github.ps1
# Sincroniza TUDO do MEGABRAIN para os repos GitHub correspondentes.
#
# Repos atualizados:
#   - mega-brain (parent)    -> código tracked
#   - mega-brain-data        -> Layer 3 (inbox, knowledge, artifacts, etc.)
#   - evotwin (submodule)    -> se houver mudanças
#   - simplex (submodule)    -> se houver mudanças
#   - anti-procrastination   -> se houver mudanças
#
# Uso: powershell -ExecutionPolicy Bypass -File scripts\sync-to-github.ps1

$ErrorActionPreference = "Continue"
$MEGABRAIN = "D:\MEGABRAIN"
$DATA_BACKUP = "D:\mega-brain-data"

function Sync-Repo {
    param([string]$Path, [string]$Branch, [string]$Label)
    Write-Host "`n=== $Label ===" -ForegroundColor Cyan
    Push-Location $Path
    $status = git status --short
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Host "  No changes." -ForegroundColor Gray
    } else {
        Write-Host "  Changes detected:" -ForegroundColor Yellow
        Write-Host $status
        git add -A
        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        git commit -m "sync: $stamp"
    }
    git push origin $Branch
    Pop-Location
}

# 1. Mirror Layer 3 from MEGABRAIN -> mega-brain-data
Write-Host "`n=== Mirroring Layer 3 -> mega-brain-data ===" -ForegroundColor Cyan

# Only exclude what would CORRUPT the repo or LEAK secrets
$excludeDirs = @(
    ".git", "node_modules", "__pycache__", ".pytest_cache",
    ".venv", "venv", ".next", "dist", "build", "out",
    ".turbo", ".mypy_cache",
    "EvoTwin", "Simplex", "One Day"
)
$excludeFiles = @(
    ".env", ".env.local",
    "*.pyc", "*.db", "*.sqlite", "*.sqlite3", "*.tsbuildinfo"
)
$args = @($MEGABRAIN, $DATA_BACKUP, "/E", "/R:1", "/W:1", "/NP", "/NFL", "/NDL", "/XD") + $excludeDirs + @("/XF") + $excludeFiles
& robocopy @args | Out-Null

# Defensive: nuke any nested .env that slipped through
Get-ChildItem -Path $DATA_BACKUP -Recurse -Force -Filter ".env" -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $DATA_BACKUP -Recurse -Force -Filter ".env.local" -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

# Strip nested .git dirs (NOT the root .git of mega-brain-data itself!)
$rootGit = Join-Path $DATA_BACKUP ".git"
Get-ChildItem -Path $DATA_BACKUP -Recurse -Force -Directory -Filter ".git" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -ne $rootGit } |
    ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }

# 2. Push each repo
Sync-Repo -Path "$MEGABRAIN\EvoTwin" -Branch "master" -Label "EvoTwin (submodule)"
Sync-Repo -Path "$MEGABRAIN\Simplex" -Branch "master" -Label "Simplex (submodule)"
Sync-Repo -Path "$MEGABRAIN\One Day\anti-procrastination" -Branch "master" -Label "One Day app"
Sync-Repo -Path $MEGABRAIN -Branch "main" -Label "mega-brain (parent)"
Sync-Repo -Path $DATA_BACKUP -Branch "main" -Label "mega-brain-data (Layer 3 backup)"

Write-Host "`n=== All synced. ===" -ForegroundColor Green
