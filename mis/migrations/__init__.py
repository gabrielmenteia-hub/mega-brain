"""Migration registry for MIS database schema."""
from ._001_initial import run_migrations  # noqa: F401
from ._002_product_enrichment import run_migration_002  # noqa: F401
from ._003_spy_dossiers import run_migration_003  # noqa: F401
