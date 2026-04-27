from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
INFRA_DB = BASE_DIR / "storage" / "olt" / "olt.db"
ONT_DIR = BASE_DIR / "storage" / "ont"
SKILLS_DIR = BASE_DIR / "skills"
