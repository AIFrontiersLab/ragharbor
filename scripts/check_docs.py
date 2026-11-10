"""Fail if a relative Markdown link points at a missing file."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)#:]+)(?:#[^)]*)?\)")
missing = []
for md in ROOT.rglob("*.md"):
    for target in LINK.findall(md.read_text(encoding="utf-8")):
        if not (md.parent / target).resolve().exists():
            missing.append(f"{md.relative_to(ROOT)} -> {target}")
print("\n".join(missing) or "all links resolve")
sys.exit(1 if missing else 0)
