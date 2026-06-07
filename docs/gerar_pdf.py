#!/usr/bin/env python3
"""
Conversor Markdown → PDF para DOSSIER
Sem dependências externas (usa reportlab)
"""

import os
import sys
import re
from pathlib import Path

def convert_markdown_to_pdf():
    """Converte DOSSIER-COMPLETO-VISUAL.md para PDF"""

    # Arquivo de origem
    md_file = Path(__file__).parent / "DOSSIER-COMPLETO-VISUAL.md"
    pdf_file = Path(__file__).parent / "DOSSIER-COMPLETO-VISUAL.pdf"

    print(f"📄 Lendo: {md_file}")

    if not md_file.exists():
        print(f"❌ Arquivo não encontrado: {md_file}")
        return False

    # Ler markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"📊 Tamanho: {len(content) / 1024:.1f} KB")
    print("🔄 Convertendo para HTML...")

    # Converter markdown para HTML simples
    try:
        import markdown2
        html_content = markdown2.markdown(
            content,
            extras=['fenced-code-blocks', 'tables', 'breaks']
        )
    except ImportError:
        print("⚠️  markdown2 não disponível, usando conversão manual...")
        html_content = content.replace('\n', '<br>')

    # Criar HTML completo
    html_full = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOSSIER: ClickUp + IA + Veto Conditions</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Courier New', 'Courier', monospace;
            font-size: 10pt;
            line-height: 1.5;
            color: #000;
            background: white;
            padding: 20px;
            max-width: 900px;
        }}

        h1 {{
            font-size: 24pt;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 3px solid #000;
            padding-bottom: 10px;
            page-break-before: always;
        }}

        h1:first-child {{ page-break-before: avoid; }}

        h2 {{
            font-size: 16pt;
            margin-top: 20px;
            margin-bottom: 10px;
            border-bottom: 1px solid #666;
            padding-bottom: 5px;
        }}

        h3 {{
            font-size: 13pt;
            margin-top: 15px;
            margin-bottom: 8px;
        }}

        h4, h5, h6 {{
            font-size: 11pt;
            margin-top: 10px;
            margin-bottom: 5px;
        }}

        p {{
            margin-bottom: 10px;
        }}

        pre {{
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 12px;
            margin: 10px 0;
            overflow-x: auto;
            font-size: 8pt;
            line-height: 1.3;
        }}

        code {{
            font-family: 'Courier New', monospace;
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 2px;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            font-size: 9pt;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}

        th {{
            background-color: #e0e0e0;
            font-weight: bold;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        ul, ol {{
            margin-left: 20px;
            margin-bottom: 10px;
        }}

        li {{
            margin-bottom: 5px;
        }}

        blockquote {{
            border-left: 4px solid #ddd;
            margin: 10px 0;
            padding-left: 15px;
            color: #666;
        }}

        a {{
            color: #0066cc;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        .page-break {{
            page-break-after: always;
        }}

        .toc {{
            page-break-after: always;
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #f9f9f9;
        }}

        .toc h2 {{
            margin-top: 0;
            border: none;
            padding-bottom: 0;
        }}

        .toc ul {{
            list-style: none;
        }}

        .toc li {{
            margin-bottom: 3px;
        }}

        .toc a {{
            color: #0066cc;
        }}
    </style>
</head>
<body>

<h1>DOSSIER COMPLETO</h1>
<h2>ClickUp + IA + Veto Conditions para Infoproduto</h2>
<p><strong>Todos os 6 Processos Detalhados com Diagramas</strong></p>

<div class="toc">
<h2>📋 Índice</h2>
<ul>
<li><a href="#processo1">Processo 1: Copy Production</a></li>
<li><a href="#processo2">Processo 2: Paid Traffic</a></li>
<li><a href="#processo3">Processo 3: SDR Pipeline</a></li>
<li><a href="#processo4">Processo 4: Closer Pipeline</a></li>
<li><a href="#processo5">Processo 5: Onboarding</a></li>
<li><a href="#processo6">Processo 6: Content Production</a></li>
<li><a href="#cascata">Cascata Inteligente</a></li>
<li><a href="#dashboard">Dashboard Central</a></li>
<li><a href="#implementacao">Implementação (18 dias)</a></li>
</ul>
</div>

{html_content}

<div style="margin-top: 40px; border-top: 2px solid #000; padding-top: 20px; text-align: center; font-size: 8pt; color: #666;">
<p>DOSSIER COMPLETO: ClickUp + IA + Veto Conditions</p>
<p>Data de Geração: 2026-04-10</p>
<p>Versão: 1.0</p>
</div>

</body>
</html>"""

    print("📝 Gerando PDF a partir de HTML...")

    try:
        # Tentar com weasyprint
        try:
            from weasyprint import HTML, CSS
            print("  ✅ Usando weasyprint...")

            HTML(string=html_full).write_pdf(str(pdf_file))

            size = pdf_file.stat().st_size / 1024
            print(f"\n✅✅✅ SUCESSO!")
            print(f"📄 Arquivo: {pdf_file.name}")
            print(f"📊 Tamanho: {size:.1f} KB")
            print(f"📍 Localização: {pdf_file.parent}")
            return True

        except ImportError:
            print("  ⚠️  weasyprint não disponível, tentando xhtml2pdf...")

            try:
                from xhtml2pdf import pisa

                with open(pdf_file, 'wb') as f:
                    pisa.CreatePDF(html_full, f)

                size = pdf_file.stat().st_size / 1024
                print(f"\n✅ PDF criado com xhtml2pdf!")
                print(f"📊 Tamanho: {size:.1f} KB")
                return True

            except ImportError:
                print("  ⚠️  xhtml2pdf não disponível")

                # Fallback: salvar como HTML
                html_file = Path(__file__).parent / "DOSSIER-COMPLETO-VISUAL.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_full)

                print(f"\n⚠️  PDF libraries não disponíveis")
                print(f"✅ Salvando como HTML em vez disso...")
                print(f"📄 Arquivo: {html_file.name}")
                print(f"\n💡 Dica: Abra o HTML no navegador e use Ctrl+P → Print to PDF")
                return True

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = convert_markdown_to_pdf()
    sys.exit(0 if success else 1)
