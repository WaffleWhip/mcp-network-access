from .config import SKILLS_DIR

def list_skills():
    if not SKILLS_DIR.exists(): return []
    return [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

def read_skill(category):
    skill_file = SKILLS_DIR / category.lower() / "SKILL.md"
    if skill_file.exists():
        return skill_file.read_text()
    return f"Error: Skill '{category}' not found."
