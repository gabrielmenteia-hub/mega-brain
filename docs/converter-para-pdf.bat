@echo off
REM Script para converter DOSSIER markdown para PDF
REM Requer: pandoc (https://pandoc.org/installing.html)

echo.
echo =================================================
echo  DOSSIER: Converter Markdown para PDF
echo =================================================
echo.

REM Verificar se pandoc esta instalado
where pandoc >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] pandoc nao encontrado
    echo.
    echo Instale pandoc em: https://pandoc.org/installing.html
    echo Ou use uma ferramenta online:
    echo   - https://pandoc.org/try
    echo   - https://cloudconvert.com (markdown para PDF)
    echo.
    pause
    exit /b 1
)

echo [OK] pandoc encontrado
echo.
echo Convertendo DOSSIER-COMPLETO-VISUAL.md para PDF...
echo.

REM Converter markdown para PDF
pandoc DOSSIER-COMPLETO-VISUAL.md ^
    -o DOSSIER-COMPLETO-VISUAL.pdf ^
    -f markdown ^
    -t pdf ^
    --pdf-engine=wkhtmltopdf ^
    -V geometry:margin=1in ^
    -V fontsize=11pt ^
    --toc ^
    --toc-depth=2

if %errorlevel% equ 0 (
    echo.
    echo [SUCESSO] PDF criado com sucesso!
    echo.
    echo Arquivo: DOSSIER-COMPLETO-VISUAL.pdf
    dir DOSSIER-COMPLETO-VISUAL.pdf
    echo.
    echo Abrindo arquivo...
    start DOSSIER-COMPLETO-VISUAL.pdf
) else (
    echo.
    echo [ERRO] Falha ao converter
    echo Tente usar: https://pandoc.org/try (online)
)

echo.
pause
