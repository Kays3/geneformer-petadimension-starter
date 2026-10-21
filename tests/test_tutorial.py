"""Static checks for the tutorial Markdown: code blocks parse, links resolve."""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = sorted(
    p for p in ROOT.rglob("*.md") if ".git" not in p.parts and ".pytest_cache" not in p.parts
)
FENCE = re.compile(r"^```(\w*)\n(.*?)^```", re.MULTILINE | re.DOTALL)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def blocks(language: str) -> list[tuple[str, int, str]]:
    found = []
    for path in MARKDOWN:
        text = path.read_text(encoding="utf-8")
        for match in FENCE.finditer(text):
            if match.group(1) == language:
                line = text.count("\n", 0, match.start()) + 1
                found.append((str(path.relative_to(ROOT)), line, match.group(2)))
    return found


PYTHON_BLOCKS = blocks("python")
BASH_BLOCKS = blocks("bash")


def test_lessons_exist_and_end_consistently() -> None:
    lessons = sorted(p for p in (ROOT / "tutorial").glob("[0-9][0-9]-*.md"))
    assert [p.name[:2] for p in lessons] == [f"{i:02d}" for i in range(11)]
    assert (ROOT / "tutorial" / "GLOSSARY.md").exists()
    for lesson in lessons:
        text = lesson.read_text(encoding="utf-8")
        assert "## You should now see" in text, lesson.name
        if lesson.name[:2] != "00":
            assert "## Troubleshooting" in text, lesson.name


def test_there_are_code_blocks_to_check() -> None:
    assert len(PYTHON_BLOCKS) >= 8
    assert len(BASH_BLOCKS) >= 4


@pytest.mark.parametrize("source,line,code", PYTHON_BLOCKS, ids=lambda v: str(v)[:40])
def test_python_block_parses(source: str, line: int, code: str) -> None:
    try:
        ast.parse(code)
    except SyntaxError as error:
        pytest.fail(f"{source}:{line + (error.lineno or 0)}: {error.msg}")


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")
@pytest.mark.parametrize("source,line,code", BASH_BLOCKS, ids=lambda v: str(v)[:40])
def test_bash_block_parses(source: str, line: int, code: str) -> None:
    result = subprocess.run(["bash", "-n"], input=code, text=True, capture_output=True)
    assert result.returncode == 0, f"{source}:{line}: {result.stderr}"


def test_relative_links_resolve() -> None:
    missing = []
    for path in MARKDOWN:
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            if not (path.parent / target.split("#")[0]).exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")
    assert not missing, "\n".join(missing)


def test_no_secrets_or_personal_paths() -> None:
    """Nothing that identifies a private network, a person's machine or a credential."""
    patterns = {
        "real home directory path": re.compile(r"/(Users|home)/(?!yourname\b)[a-z]"),
        "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        "key-copying step": re.compile(r"ssh-copy-id|>>\s*\S*authorized_keys"),
        "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
        "Hugging Face token": re.compile(r"hf_[A-Za-z0-9]{20,}"),
        "private-network address": re.compile(r"\b(100\.\d{1,3}|10\.\d{1,3}|192\.168|172\.(1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"),
        "tailnet name": re.compile(r"\.ts\.net|tailscale", re.IGNORECASE),
        "shared-drive path": re.compile(r"/mnt/nas|~/NAS", re.IGNORECASE),
        "email address": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    }
    # Documents under these roots are checked as text. The quickstart code and
    # the lockfile are checked too, because they are published as well.
    candidates = list(MARKDOWN) + [
        p for p in (ROOT / "quickstart").rglob("*")
        if p.is_file() and p.suffix in {".py", ".sh", ".toml", ".lock", ".gitignore", ""}
    ] + [ROOT / ".github" / "workflows" / "ci.yml"]
    hits = []
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        for name, pattern in patterns.items():
            if path.suffix == ".lock" and name == "private-network address":
                continue  # package version strings such as 10.4.0.35 look like addresses
            if pattern.search(text):
                hits.append(f"{path.relative_to(ROOT)}: {name}")
    assert not hits, "\n".join(hits)
