"""
DOSSIER UPDATER — Utilitário genérico para atualizar DOSSIERs de pessoas
Economiza tokens: evita múltiplos Read/Edit do arquivo manualmente.

Uso:
    from core.intelligence.dossier_updater import DossierUpdater

    upd = DossierUpdater("DOSSIER-RUSSELL-BRUNSON.md")
    upd.add_source("RB11F")
    upd.add_section("## LEAD FUNNELS [RB11F]", content)
    upd.update_meta(total_insights=125, dna_status="v1.3.0")
    upd.save()

CLI:
    python core/intelligence/dossier_updater.py \\
        --dossier DOSSIER-RUSSELL-BRUNSON.md \\
        --add-source RB11F \\
        --update-meta total_insights=125
"""
import re
import argparse
from pathlib import Path

ROOT = Path("c:/Users/Gabriel/MEGABRAIN")
DOSSIERS_DIR = ROOT / "knowledge/dossiers/persons"


class DossierUpdater:
    def __init__(self, filename: str):
        self.path = DOSSIERS_DIR / filename
        if not self.path.exists():
            raise FileNotFoundError(f"Dossier not found: {self.path}")
        self.content = self.path.read_text(encoding="utf-8")
        self._modified = False

    # ── SOURCES LINE ──────────────────────────────────────────────────────

    def add_source(self, source_id: str) -> "DossierUpdater":
        """Add source_id to the **Sources:** line if not already present."""
        match = re.search(r'\*\*Sources:\*\* (.+)', self.content)
        if not match:
            print(f"WARNING: **Sources:** line not found")
            return self
        current = match.group(1).strip()
        if source_id in current:
            print(f"Source {source_id} already present")
            return self
        new_sources = current + f", {source_id}"
        self.content = self.content.replace(
            f"**Sources:** {current}",
            f"**Sources:** {new_sources}"
        )
        self._modified = True
        print(f"✓ Source added: {source_id}")
        return self

    # ── SECTIONS ─────────────────────────────────────────────────────────

    def add_section_before(self, anchor: str, section_content: str) -> "DossierUpdater":
        """Insert section_content immediately before the anchor string."""
        if anchor not in self.content:
            print(f"WARNING: Anchor not found: '{anchor}'")
            return self
        self.content = self.content.replace(anchor, section_content + "\n" + anchor)
        self._modified = True
        print(f"✓ Section inserted before: {anchor[:40]}...")
        return self

    def add_section_after(self, anchor: str, section_content: str) -> "DossierUpdater":
        """Insert section_content immediately after the anchor string."""
        if anchor not in self.content:
            print(f"WARNING: Anchor not found: '{anchor}'")
            return self
        self.content = self.content.replace(anchor, anchor + "\n" + section_content)
        self._modified = True
        print(f"✓ Section inserted after: {anchor[:40]}...")
        return self

    def replace_section(self, old: str, new: str) -> "DossierUpdater":
        """Replace any string in the dossier."""
        if old not in self.content:
            print(f"WARNING: String not found for replacement")
            return self
        self.content = self.content.replace(old, new)
        self._modified = True
        print(f"✓ String replaced")
        return self

    # ── METADADOS YAML BLOCK ─────────────────────────────────────────────

    def update_meta(self, **kwargs) -> "DossierUpdater":
        """
        Update key: value pairs in the METADADOS yaml block.

        Example:
            upd.update_meta(
                total_insights=125,
                dna_status='EXTRAÍDO v1.3.0 (5 fontes)'
            )
        """
        for key, value in kwargs.items():
            # Match "key: old_value" or "key: 'old_value'"
            pattern = rf'^({re.escape(key)}:\s*)(.+)$'
            replacement = rf'\g<1>{value}'
            new_content, n = re.subn(pattern, replacement, self.content, flags=re.MULTILINE)
            if n == 0:
                print(f"WARNING: key '{key}' not found in metadados")
            else:
                self.content = new_content
                self._modified = True
                print(f"✓ Meta updated: {key} → {value}")
        return self

    # ── SOURCES TABLE (metadados yaml) ────────────────────────────────────

    def add_meta_source(self, source_id: str, titulo: str, paginas: int,
                        palavras: int, chunks: int, data: str = "2026-03-09") -> "DossierUpdater":
        """
        Add a source entry inside the METADADOS yaml block.
        Inserts before 'total_insights:' line.
        """
        new_entry = (
            f"  - id: {source_id}\n"
            f"    titulo: {titulo}\n"
            f"    paginas: {paginas}\n"
            f"    palavras: {palavras}\n"
            f"    chunks: {chunks}\n"
            f"    data: {data}\n"
        )
        anchor = "total_insights:"
        if anchor not in self.content:
            print(f"WARNING: anchor '{anchor}' not found in metadados")
            return self
        self.content = self.content.replace(anchor, new_entry + anchor)
        self._modified = True
        print(f"✓ Meta source added: {source_id} ({titulo})")
        return self

    # ── SAVE ─────────────────────────────────────────────────────────────

    def save(self) -> None:
        if not self._modified:
            print("No changes made — nothing saved.")
            return
        self.path.write_text(self.content, encoding="utf-8")
        print(f"✓ Saved: {self.path.name}")

    def preview(self, lines: int = 20) -> None:
        """Print first N lines of current state."""
        for i, line in enumerate(self.content.splitlines()[:lines], 1):
            print(f"{i:4}: {line}")


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Update a DOSSIER file")
    parser.add_argument("--dossier", required=True, help="DOSSIER filename (e.g. DOSSIER-RUSSELL-BRUNSON.md)")
    parser.add_argument("--add-source", help="Add source ID to **Sources:** line")
    parser.add_argument("--update-meta", nargs="*", help="key=value pairs for metadados")
    parser.add_argument("--preview", action="store_true", help="Preview first 20 lines")
    args = parser.parse_args()

    upd = DossierUpdater(args.dossier)

    if args.add_source:
        upd.add_source(args.add_source)

    if args.update_meta:
        meta = {}
        for kv in args.update_meta:
            k, v = kv.split("=", 1)
            meta[k.strip()] = v.strip()
        upd.update_meta(**meta)

    if args.preview:
        upd.preview()
    else:
        upd.save()


if __name__ == "__main__":
    main()
