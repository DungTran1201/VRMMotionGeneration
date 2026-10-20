from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / ".agents"
errors: list[str] = []

if not (ROOT / "AGENTS.md").is_file():
    errors.append("Missing root AGENTS.md")
for required in ("README.md", "rules", "skills", "agents", "hooks", "project"):
    if not (AGENTS / required).exists():
        errors.append(f"Missing .agents/{required}")

skill_root = AGENTS / "skills"
if skill_root.exists():
    for skill_file in skill_root.glob("*/SKILL.md"):
        folder = skill_file.parent.name
        text = skill_file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if not match:
            errors.append(f"{skill_file.relative_to(ROOT)}: missing YAML frontmatter")
            continue
        metadata = match.group(1)
        name_match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", metadata, re.M)
        desc_match = re.search(r"^description:\s*(.+?)\s*$", metadata, re.M)
        if not name_match:
            errors.append(f"{skill_file.relative_to(ROOT)}: missing/invalid name")
        elif name_match.group(1) != folder:
            errors.append(f"{skill_file.relative_to(ROOT)}: name doesn't match folder {folder}")
        if not desc_match:
            errors.append(f"{skill_file.relative_to(ROOT)}: missing description")

for role_file in (AGENTS / "agents").glob("*.md") if (AGENTS / "agents").exists() else []:
    text = role_file.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "name:" not in text.split("---", 2)[1]:
        errors.append(f"{role_file.relative_to(ROOT)}: missing role frontmatter/name")

if errors:
    print("Agent assets INVALID:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)
print(f"Agent assets OK: {len(list(skill_root.glob('*/SKILL.md')))} skills, "
      f"{len(list((AGENTS / 'agents').glob('*.md')))} specialist agents.")
