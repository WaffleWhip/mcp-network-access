import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_DIR = BASE_DIR / "storage"
INFRA_DB = str(DB_DIR / "olt.db")

DB_DIR.mkdir(exist_ok=True)
