# NotesCI

Central CI logic for my Typst course-notes repositories. Each course repo
(e.g. `UniversityPhysics`, `MathematicalAnalysis`) contains only its notes and
a tiny stub workflow that calls the reusable workflow here — so the build logic
(fonts, compilation, release, README generation) is maintained in **one place**.

## What's here

| Path | Purpose |
|------|---------|
| `.github/workflows/typst-release.yml` | Reusable workflow: install fonts → compile all `.typ` (except `template.typ`) → regenerate README → publish PDF to Releases |
| `scripts/gen_readme.py` | Generates `README.md` from a course repo's `course.toml` |

## How a course repo uses it

Each course repo has a 6-line `.github/workflows/auto_release.yml`:

```yaml
name: Auto-Compile and Release PDF
on:
  push: { branches: [main] }
  workflow_dispatch:
jobs:
  build:
    uses: ClosureScope/NotesCI/.github/workflows/typst-release.yml@main
    permissions:
      contents: write
```

Plus a `course.toml` with the three lines that actually change per course:

```toml
name_en = "University Physics(H)"
name_zh = "大学物理（荣誉）（1）"
code    = "PHY1251H"
```

That's it — no scripts, no build logic in the course repo.

## Starting a new course

Use the [`NotesTemplate`](https://github.com/ClosureScope/NotesTemplate)
repository ("Use this template"), then edit `course.toml`.

## Changing the build for all courses at once

Edit `typst-release.yml` or `gen_readme.py` here. Every course repo picks up the
change on its next push (they all reference `@main`).

> **Note:** this repo must stay **public** — public course repos can only call
> reusable workflows from public repositories.
