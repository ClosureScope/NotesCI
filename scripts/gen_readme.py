#!/usr/bin/env python3
"""从 course.toml 生成 README.md。

在课程仓库的根目录下运行：
    python path/to/gen_readme.py

读取当前工作目录（cwd）下的 course.toml，把 README.md 写到同一目录。
所有课程仓库共用这一份脚本，无需修改；要改 README 样式，改本文件顶部的
TEMPLATE 即可，改动对所有课程仓库自动生效（通过 NotesCI 的可复用工作流）。
"""
from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path.cwd()
COURSE_FILE = ROOT / "course.toml"
README_FILE = ROOT / "README.md"


def find_sources() -> list[str]:
    """笔记源文件 = 除 template.typ 外的所有 .typ。"""
    return sorted(p.name for p in ROOT.glob("*.typ") if p.name != "template.typ")


TEMPLATE = """\
<div align="center">

# {name_en}

{name_zh} · `{code}` · SJTU

**Author Closure**

[![Auto Release](https://github.com/{repo}/actions/workflows/auto_release.yml/badge.svg)](https://github.com/{repo}/actions/workflows/auto_release.yml)
[![Latest PDF](https://img.shields.io/badge/download-latest%20PDF-red)](https://github.com/{repo}/releases/latest)
[![Made with Typst](https://img.shields.io/badge/made%20with-Typst-239dad)](https://typst.app/)

</div>

---

Course notes for **{name_en}（{name_zh}, `{code}`）** at **SJTU**,
typeset in [Typst](https://typst.app/) and continuously built into a PDF by CI.

## Download

The latest PDF is built automatically on every push and published to
[**Releases → latest**]({pdf_url}). No need to clone or compile anything.

## Repository layout

| File | Description |
|------|-------------|
{source_rows}
| [`template.typ`](template.typ) | Styling template (imported by the notes, not compiled on its own) |
| [`course.toml`](course.toml) | Course metadata — the single source of truth for this README and the release workflow |
| `*.pdf` | Compiled output — built by CI, get it from [Releases]({pdf_url}) |

## Building locally

```bash
{build_cmds}
```

---

<div align="center">
<sub>README is generated from <code>course.toml</code> — edit the TOML, not this file. CI logic lives in <a href="https://github.com/ClosureScope/NotesCI">NotesCI</a>.</sub>
</div>
"""


def repo_slug() -> str:
    """尽量从 git remote 推断 owner/repo，失败则用占位符。"""
    try:
        url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "OWNER/REPO"
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    return m.group(1) if m else "OWNER/REPO"


def main() -> int:
    if not COURSE_FILE.exists():
        print(f"error: {COURSE_FILE} not found (run from a course repo root)", file=sys.stderr)
        return 1

    with COURSE_FILE.open("rb") as f:
        course = tomllib.load(f)

    repo = repo_slug()
    sources = find_sources() or ["notebook.typ"]
    source_rows = "\n".join(
        f"| [`{s}`]({s}) | Source of the notes, written in Typst |" for s in sources
    )
    build_cmds = "\n".join(f"typst compile {s}" for s in sources)
    content = TEMPLATE.format(
        name_en=course.get("name_en", "Course"),
        name_zh=course.get("name_zh", ""),
        code=course.get("code", ""),
        source_rows=source_rows,
        build_cmds=build_cmds,
        repo=repo,
        pdf_url=f"https://github.com/{repo}/releases/latest",
    )
    README_FILE.write_text(content, encoding="utf-8")
    print(f"wrote {README_FILE} (repo={repo}, sources={sources})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
