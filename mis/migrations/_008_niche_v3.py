"""Migration 008 — niches_v3, subniches, subniche_platform_slugs.

Creates the v3 niche hierarchy tables with seed data:
  - 4 top-level niches (Relacionamento, Saúde, Finanças, Renda Extra)
  - 42 subniches with fixed IDs distributed across the 4 niches
  - Platform search slugs for 9 platforms with public marketplaces

Platforms WITHOUT mappings (checkout-only / 403 without login):
  - Eduzz (id=4), Monetizze (id=5), PerfectPay (id=6)

Idempotent: safe to run multiple times — INSERT OR IGNORE on all rows.
Does NOT touch the legacy `niches` table.

IDs here MUST match constants in mis/platform_ids.py.
"""
import sqlite_utils


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

_NICHES_V3 = [
    (1, "Relacionamento", "relacionamento"),
    (2, "Saúde",          "saude"),
    (3, "Finanças",       "financas"),
    (4, "Renda Extra",    "renda-extra"),
]

_SUBNICHES = [
    # Relacionamento (niche_id=1) — 10 subnichos
    (101, 1, "Reconquista",                 "reconquista"),
    (102, 1, "Sedução masculina",            "seducao-masculina"),
    (103, 1, "Relacionamento feminino",      "relacionamento-feminino"),
    (104, 1, "Casamento e família",          "casamento-e-familia"),
    (105, 1, "Autoestima e confiança",       "autoestima-e-confianca"),
    (106, 1, "Comunicação e influência",     "comunicacao-e-influencia"),
    (107, 1, "Traição e ciúmes",             "traicao-e-ciumes"),
    (108, 1, "Divórcio e recomeço",          "divorcio-e-recomeco"),
    (109, 1, "Relacionamento à distância",   "relacionamento-a-distancia"),
    (110, 1, "Atração e linguagem corporal", "atracao-e-linguagem-corporal"),
    # Saúde (niche_id=2) — 12 subnichos
    (201, 2, "Emagrecimento",                "emagrecimento"),
    (202, 2, "Diabetes e glicemia",          "diabetes-e-glicemia"),
    (203, 2, "Ansiedade e sono",             "ansiedade-e-sono"),
    (204, 2, "Ganho de massa",               "ganho-de-massa"),
    (205, 2, "Saúde feminina",               "saude-feminina"),
    (206, 2, "Cabelo e pele",                "cabelo-e-pele"),
    (207, 2, "Dor crônica e coluna",         "dor-cronica-e-coluna"),
    (208, 2, "Tireoide e hormônios",         "tireoide-e-hormonios"),
    (209, 2, "Detox e alimentação saudável", "detox-e-alimentacao-saudavel"),
    (210, 2, "Saúde masculina",              "saude-masculina"),
    (211, 2, "Visão e audição",              "visao-e-audicao"),
    (212, 2, "Pressão alta e colesterol",    "pressao-alta-e-colesterol"),
    # Finanças (niche_id=3) — 10 subnichos
    (301, 3, "Renda extra online",           "renda-extra-online"),
    (302, 3, "Investimentos para iniciantes","investimentos-para-iniciantes"),
    (303, 3, "Sair das dívidas",             "sair-das-dividas"),
    (304, 3, "Day trade e cripto",           "day-trade-e-cripto"),
    (305, 3, "Empreendedorismo",             "empreendedorismo"),
    (306, 3, "Imóveis e renda passiva",      "imoveis-e-renda-passiva"),
    (307, 3, "Finanças para MEI",            "financas-para-mei"),
    (308, 3, "Aposentadoria e independência","aposentadoria-e-independencia"),
    (309, 3, "Concursos públicos",           "concursos-publicos"),
    (310, 3, "Importação e revenda",         "importacao-e-revenda"),
    # Renda Extra (niche_id=4) — 12 subnichos
    (401, 4, "Tráfego pago",                 "trafego-pago"),
    (402, 4, "Afiliados",                    "afiliados"),
    (403, 4, "Marketing de conteúdo",        "marketing-de-conteudo"),
    (404, 4, "Dropshipping",                 "dropshipping"),
    (405, 4, "Serviços freelancer",          "servicos-freelancer"),
    (406, 4, "Social media",                 "social-media"),
    (407, 4, "Vendas pelo WhatsApp",         "vendas-pelo-whatsapp"),
    (408, 4, "Edição de vídeo e design",     "edicao-de-video-e-design"),
    (409, 4, "Copywriting",                  "copywriting"),
    (410, 4, "Consultoria e mentoria online","consultoria-e-mentoria-online"),
    (411, 4, "YouTube e criação de conteúdo","youtube-e-criacao-de-conteudo"),
    (412, 4, "Precificação e vendas locais", "precificacao-e-vendas-locais"),
]

# ---------------------------------------------------------------------------
# Platform slug mappings per niche group.
# Format: (subniche_id, platform_id, search_slug)
#
# Platform IDs (from mis/platform_ids.py):
#   hotmart=1, clickbank=2, kiwify=3, braip=7
#   udemy=9, gumroad=11, appsumo=12
#   product_hunt=8 (always "trending"), jvzoo=10 (always "84")
#
# Platforms WITHOUT mappings (no public marketplace search):
#   eduzz=4, monetizze=5, perfectpay=6
# ---------------------------------------------------------------------------

# Slugs por nicho — (platform_id, search_slug)
_SLUG_BY_NICHE = {
    1: [  # Relacionamento
        (1,  "relacionamentos"),
        (2,  "self-help"),
        (3,  "relacionamentos"),
        (7,  "cursos-online"),
        (9,  "Personal Development"),
        (11, "self-improvement"),
        (12, "productivity"),
        (8,  "trending"),
        (10, "84"),
    ],
    2: [  # Saúde
        (1,  "saude-e-fitness"),
        (2,  "health"),
        (3,  "saude"),
        (7,  "encapsulados"),
        (9,  "Health & Fitness"),
        (11, "health"),
        (12, "health-fitness"),
        (8,  "trending"),
        (10, "84"),
    ],
    3: [  # Finanças
        (1,  "financas"),
        (2,  "investing"),
        (3,  "financas"),
        (7,  "cursos-online"),
        (9,  "Finance & Accounting"),
        (11, "finance"),
        (12, "finance"),
        (8,  "trending"),
        (10, "84"),
    ],
    4: [  # Renda Extra
        (1,  "marketing"),
        (2,  "marketing"),
        (3,  "marketing"),
        (7,  "cursos-online"),
        (9,  "Marketing"),
        (11, "marketing"),
        (12, "marketing-sales"),
        (8,  "trending"),
        (10, "84"),
    ],
}

# niche_id mapping for each subniche range
_NICHE_ID_FOR_SUBNICHE = {
    101: 1, 102: 1, 103: 1, 104: 1, 105: 1,
    106: 1, 107: 1, 108: 1, 109: 1, 110: 1,
    201: 2, 202: 2, 203: 2, 204: 2, 205: 2, 206: 2,
    207: 2, 208: 2, 209: 2, 210: 2, 211: 2, 212: 2,
    301: 3, 302: 3, 303: 3, 304: 3, 305: 3,
    306: 3, 307: 3, 308: 3, 309: 3, 310: 3,
    401: 4, 402: 4, 403: 4, 404: 4, 405: 4, 406: 4,
    407: 4, 408: 4, 409: 4, 410: 4, 411: 4, 412: 4,
}


def _build_platform_slugs() -> list[tuple[int, int, str]]:
    """Build the full (subniche_id, platform_id, search_slug) list from niche mappings."""
    rows = []
    for subniche_id, niche_id in _NICHE_ID_FOR_SUBNICHE.items():
        for platform_id, search_slug in _SLUG_BY_NICHE[niche_id]:
            rows.append((subniche_id, platform_id, search_slug))
    return rows


_PLATFORM_SLUGS = _build_platform_slugs()


# ---------------------------------------------------------------------------
# Migration function
# ---------------------------------------------------------------------------

def run_migration_008(db_path: str) -> None:
    """Create v3 niche hierarchy tables and seed data.

    Creates:
      - niches_v3: 4 top-level niches with fixed IDs
      - subniches: 42 subniches with fixed IDs linked to niches_v3
      - subniche_platform_slugs: search slugs per subniche per platform

    Idempotent: uses IF NOT EXISTS for DDL and INSERT OR IGNORE for rows.
    Does NOT touch the legacy `niches` table or any existing product data.

    Args:
        db_path: Path to the SQLite database file.
    """
    db = sqlite_utils.Database(db_path)

    # SQLite does not enforce foreign keys by default
    db.execute("PRAGMA foreign_keys=ON")

    table_names = db.table_names()

    # ------------------------------------------------------------------
    # 1. niches_v3 — top-level niche taxonomy (v3 replacement for niches)
    # ------------------------------------------------------------------
    if "niches_v3" not in table_names:
        db.execute(
            """
            CREATE TABLE niches_v3 (
                id   INTEGER PRIMARY KEY,
                name TEXT    NOT NULL,
                slug TEXT    NOT NULL
            )
            """
        )
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_niches_v3_slug ON niches_v3 (slug)"
        )

    # ------------------------------------------------------------------
    # 2. subniches — second-level taxonomy linked to niches_v3
    # ------------------------------------------------------------------
    if "subniches" not in table_names:
        db.execute(
            """
            CREATE TABLE subniches (
                id       INTEGER PRIMARY KEY,
                niche_id INTEGER NOT NULL REFERENCES niches_v3(id),
                name     TEXT    NOT NULL,
                slug     TEXT    NOT NULL
            )
            """
        )
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_subniches_niche_slug "
            "ON subniches (niche_id, slug)"
        )

    # ------------------------------------------------------------------
    # 3. subniche_platform_slugs — search slug per subniche per platform
    # ------------------------------------------------------------------
    if "subniche_platform_slugs" not in table_names:
        db.execute(
            """
            CREATE TABLE subniche_platform_slugs (
                subniche_id  INTEGER NOT NULL REFERENCES subniches(id),
                platform_id  INTEGER NOT NULL REFERENCES platforms(id),
                search_slug  TEXT    NOT NULL,
                PRIMARY KEY (subniche_id, platform_id)
            )
            """
        )

    # ------------------------------------------------------------------
    # 4-6. Seed data — skip if already populated (idempotent fast-path).
    #
    # Checking COUNT(*) avoids acquiring a write lock on repeated calls
    # when another connection (e.g. a test fixture) holds an open
    # write transaction on the same file.
    # ------------------------------------------------------------------
    niches_count = next(db.execute("SELECT COUNT(*) FROM niches_v3"))[0]
    if niches_count < len(_NICHES_V3):
        for nid, name, slug in _NICHES_V3:
            db.execute(
                "INSERT OR IGNORE INTO niches_v3 (id, name, slug) VALUES (?, ?, ?)",
                (nid, name, slug),
            )

    subniches_count = next(db.execute("SELECT COUNT(*) FROM subniches"))[0]
    if subniches_count < len(_SUBNICHES):
        for sid, niche_id, name, slug in _SUBNICHES:
            db.execute(
                "INSERT OR IGNORE INTO subniches (id, niche_id, name, slug) VALUES (?, ?, ?, ?)",
                (sid, niche_id, name, slug),
            )

    slugs_count = next(db.execute("SELECT COUNT(*) FROM subniche_platform_slugs"))[0]
    if slugs_count < len(_PLATFORM_SLUGS):
        for subniche_id, platform_id, search_slug in _PLATFORM_SLUGS:
            db.execute(
                "INSERT OR IGNORE INTO subniche_platform_slugs "
                "(subniche_id, platform_id, search_slug) VALUES (?, ?, ?)",
                (subniche_id, platform_id, search_slug),
            )

    db.conn.commit()
