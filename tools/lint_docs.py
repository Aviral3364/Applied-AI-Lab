#!/usr/bin/env python3
"""Fail on long prose lines in Markdown so docs stay diff-friendly (one sentence per line).

Skips YAML frontmatter, fenced code blocks and table rows, which cannot be wrapped.
"""
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
MAX = 200
GLOBS = ("README.md", "CHANGELOG.md", "docs/**/*.md", "skills/**/*.md", "evals/**/*.md")


def long_lines(path):
    in_code = in_front = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if number == 1 and stripped == "---":
            in_front = True
            continue
        if in_front:
            in_front = stripped != "---"
            continue
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or stripped.startswith("|"):
            continue
        if len(line) > MAX:
            yield number, len(line)


def main():
    files = sorted({p for pattern in GLOBS for p in REPO.glob(pattern) if p.is_file()})
    problems = [(f, n, size) for f in files for n, size in long_lines(f)]
    for f, n, size in problems:
        print(f"{f.relative_to(REPO)}:{n}: {size} chars > {MAX}; put one sentence per line")
    print(f"Checked {len(files)} file(s); {len(problems)} long line(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
