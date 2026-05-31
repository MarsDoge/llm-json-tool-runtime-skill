#!/usr/bin/env python3
"""Validate installable Hermes skill files in this repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML is required: python3 -m pip install pyyaml", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

required_headings = [
    "## Overview",
    "## When to Use",
    "## Common Pitfalls",
    "## Verification Checklist",
]


def validate(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        raise AssertionError(f"{path}: frontmatter must start at byte 0")

    match = re.search(r"\n---\s*\n", content[3:])
    if not match:
        raise AssertionError(f"{path}: missing closing frontmatter fence")

    frontmatter = content[3 : match.start() + 3]
    body = content[3:][match.end() :]
    metadata = yaml.safe_load(frontmatter)

    if not isinstance(metadata, dict):
        raise AssertionError(f"{path}: frontmatter is not a YAML mapping")

    name = metadata.get("name")
    description = metadata.get("description")

    if not name:
        raise AssertionError(f"{path}: missing name")
    if not description:
        raise AssertionError(f"{path}: missing description")
    if len(name) > 64:
        raise AssertionError(f"{path}: name longer than 64 chars")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        raise AssertionError(f"{path}: name must be lowercase hyphenated")
    if len(description) > 1024:
        raise AssertionError(f"{path}: description longer than 1024 chars")
    if len(content) > 100_000:
        raise AssertionError(f"{path}: content longer than 100,000 chars")
    if not body.strip():
        raise AssertionError(f"{path}: empty body")

    for heading in required_headings:
        if heading not in body:
            raise AssertionError(f"{path}: missing heading {heading!r}")

    print(f"OK {path.relative_to(ROOT)} {name}")


def main() -> int:
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if not skill_files:
        print("ERROR: no skills/*/SKILL.md files found", file=sys.stderr)
        return 1

    try:
        for path in skill_files:
            validate(path)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
