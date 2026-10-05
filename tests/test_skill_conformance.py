"""Agent Skills specification conformance for every skill in skills/.

Rules follow https://agentskills.io/specification (checked 2026-10-05) plus this
repository's policy that skill directories contain runtime content only.
"""
from pathlib import Path
import re
import unittest

REPO = Path(__file__).resolve().parents[1]
SKILLS = sorted(p for p in (REPO / "skills").iterdir() if p.is_dir())
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_TOP_LEVEL = {"SKILL.md", "scripts", "references", "assets", "agents", "LICENSE", "LICENSE.txt"}
FORBIDDEN_NAMES = {"tests", "test", "evals", "README.md", "CHANGELOG.md", "__pycache__", "node_modules", ".venv"}
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def parse_frontmatter(text):
    """Parse flat keys plus one-level nested maps; enough for the spec fields, no PyYAML."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("unterminated frontmatter") from error
    data, parent = {}, None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.strip().partition(":")
        if not sep:
            raise ValueError(f"unparseable frontmatter line: {line!r}")
        value = value.strip().strip('"').strip("'")
        if line.startswith((" ", "\t")):
            if parent is None:
                raise ValueError(f"indented line without parent: {line!r}")
            data[parent][key.strip()] = value
        elif value:
            data[key.strip()], parent = value, None
        else:
            data[key.strip()], parent = {}, key.strip()
    return data, lines[end + 1:]


class SkillConformanceTests(unittest.TestCase):
    def test_skills_exist(self):
        self.assertTrue(SKILLS, "no skills found")

    def test_frontmatter(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                meta, _ = parse_frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
                name = meta.get("name", "")
                self.assertEqual(skill.name, name, "name must match directory")
                self.assertRegex(name, NAME_RE)
                self.assertLessEqual(len(name), 64)
                description = meta.get("description", "")
                self.assertTrue(isinstance(description, str) and 1 <= len(description) <= 1024)
                if "compatibility" in meta:
                    self.assertTrue(1 <= len(meta["compatibility"]) <= 500)
                if "metadata" in meta:
                    self.assertIsInstance(meta["metadata"], dict)

    def test_skill_body_under_500_lines(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                lines = (skill / "SKILL.md").read_text(encoding="utf-8").splitlines()
                self.assertLess(len(lines), 500)

    def test_only_runtime_content_ships(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                extra = {p.name for p in skill.iterdir()} - ALLOWED_TOP_LEVEL
                self.assertFalse(extra, f"unexpected top-level entries: {sorted(extra)}")
                for path in skill.rglob("*"):
                    rel = path.relative_to(skill)
                    self.assertNotIn(path.name, FORBIDDEN_NAMES, f"dev-only artifact in skill: {rel}")
                    self.assertFalse(path.name.startswith("test_"), f"test file in skill: {rel}")
                    self.assertFalse(path.name.endswith("-workspace"), f"eval workspace in skill: {rel}")

    def test_relative_links_resolve_inside_skill(self):
        for skill in SKILLS:
            docs = [skill / "SKILL.md", *sorted((skill / "references").glob("*.md"))]
            for doc in docs:
                for target in LINK_RE.findall(doc.read_text(encoding="utf-8")):
                    if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                        continue
                    with self.subTest(doc=str(doc.relative_to(REPO)), target=target):
                        resolved = (doc.parent / target.split("#", 1)[0]).resolve()
                        self.assertTrue(resolved.exists(), "broken link")
                        self.assertTrue(resolved.is_relative_to(skill.resolve()), "link escapes skill")


if __name__ == "__main__":
    unittest.main()
