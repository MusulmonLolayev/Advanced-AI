# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This is the authored course material for an "Advanced AI" course, split into one top-level directory per module's track:

- **`ml/`** — Module 1 (Classical Machine Learning). Two parallel tracks share topics but are otherwise independent:
  - **Lecture slides** (`ml/main.tex`, `ml/lectures/*.tex`, `ml/theme/*.tex`) — a single Beamer deck.
  - **Assignments** (`ml/assignments/assignmentN_<topic>/`) — self-contained Python labs, each with its own NumPy implementation package, Jupyter notebook, LaTeX lab handout, and self-check script; `ml/assignments/main.tex` compiles all `labN.tex` handouts into one booklet.
- **`statistics/`** — Module 0 (Statistics for Advanced AI). Same Beamer-deck layout as `ml/` (`statistics/main.tex`, `statistics/lectures/*.tex`, `statistics/theme/*.tex`, `statistics/scripts/`), but with its own copy of the theme/macros files rather than sharing `ml/theme/` — the two module tracks are meant to stay independently editable, same as assignments not sharing a package. No assignments track exists for this module yet.
- **`agents/`** — Module 7 (AI Agents, Tool Use & Retrieval). Same Beamer-deck layout as `ml/` and `statistics/`, with its own theme/macros copy. `course-map.md` carries its capstone-project spec, model/cost baseline and per-lecture reading list.
- **`overview/`** — a single standalone course-overview deck (not tied to one module): `overview/main.tex` `\input`s one file, `overview/content/course_overview.tex`, summarizing the course goal, the 8-module structure, and per-module topic breakdowns. Its own theme/macros copy, same as the other two directories. By design it avoids authoring-status language ("in progress", "fully authored", etc.) — it describes the planned syllabus, not what's currently drafted; `course-map.md` is where authoring status is tracked (per-module notes on which lectures are drafted vs. outline-only).

`course-map.md` (repo root) is the authoritative source for the full course structure (8 modules, 0-7), scope, what's intentionally excluded, and per-module authoring status — read it before adding or reordering material. Module 0 (`statistics/lectures/`) is complete — all 10 lectures, each split into two part files. Module 1 (`ml/lectures/`) has Lectures 1-10 of 14. Module 7 (`agents/lectures/`) is complete — all 8 lectures, each split into two part files (Lecture 1 is a single part). Modules 2-6 exist only as the outline in `course-map.md`. Assignments currently only cover Module 1 Lectures 1-7.

Two project-scoped Claude Code skills capture the established authoring workflow in detail — read them (or let them trigger) instead of re-deriving the process:
- **`pandas-vector-graphics`** (`.claude/skills/pandas-vector-graphics/`) — how lecture figures are built: pandas/numpy for the numbers, rendered to vector PDF+SVG (never raster). Most existing scripts render via TikZ/pgfplots compiled with `pdflatex`; `generate_tsne_graphics.py` (lecture 10) instead renders directly with matplotlib (`fig.savefig(...)`) — matplotlib is the preferred path for new chart-type figures (scatter/line/bar plots, comparisons) since it avoids hand-built TikZ coordinate strings; TikZ remains better suited to schematic diagrams with custom geometry. Don't retrofit the other existing TikZ scripts without being asked.
- **`latex-slide-fit`** (`.claude/skills/latex-slide-fit/`) — the compile → detect → rasterize → inspect → fix loop for catching Beamer overflow (content silently running under the footer), which a clean `pdflatex` exit code does not rule out. Applies the same way regardless of whether a figure was rendered via TikZ or matplotlib — check the embedded PDF's aspect ratio against its `\includegraphics` column width either way.

## Building the slides

Each module's deck is its own `main.tex`, which `\input`s every lecture `.tex` file in that module's `lectures/` directory in order (all lectures in a deck build together, not one-at-a-time). To build:

```bash
cd ml            # or: cd statistics, or: cd overview
pdflatex main.tex   # or latexmk -pdf main.tex
```

Follow the `latex-slide-fit` skill's two-pass-compile + warning-grep + rasterize-and-read loop after editing any frame — a successful compile does not mean the slide is readable. This applies the same way in `statistics/` as in `ml/`.

Each module has its own theme/macros copy — `ml/theme/rl-theme.tex`+`ml/theme/rl-macros.tex` and `statistics/theme/rl-theme.tex`+`statistics/theme/rl-macros.tex` — reuse macros from the matching module's theme file instead of hardcoding TikZ/math styling in a lecture file, to keep notation consistent within that module's lectures. The two copies are intentionally independent (not `\input` from a shared location); a branding/macro change made in one does not propagate to the other unless applied by hand.

## Generating lecture figures

Each lecture's figures are generated by a matching script in the module's `scripts/` directory (e.g. `ml/scripts/generate_forest_variants_graphics.py` for `ml` lecture 7), which builds the underlying numbers with pandas/numpy, renders them (TikZ/pgfplots compiled with `pdflatex`, or matplotlib directly — see the `pandas-vector-graphics` skill), and writes into that module's `figures/<topic>/` (gitignored build artifacts; only each topic directory's `.gitignore` is committed). Run a script directly:

```bash
python3 ml/scripts/generate_<topic>_graphics.py            # or statistics/scripts/...
```

and regenerate the matching figures whenever a lecture's numbers/examples change. See the `pandas-vector-graphics` skill before writing a new `generate_*_graphics.py` script. Some newer scripts (e.g. `generate_tsne_graphics.py`) additionally depend on `scikit-learn`/`pandas` beyond the core `requirements.txt`/`environment-data.yml` deps — install as needed when running them. The `adv_ai` conda env (not the assignments' `ai_courses` env) already has numpy/pandas/matplotlib/scikit-learn — run matplotlib-path scripts with `conda run -n adv_ai python3 <script>.py` rather than the bare system `python3`, which lacks these packages.

## Assignments

Each `ml/assignments/assignmentN_<topic>/` directory is fully independent — there is no shared package between assignments; `advanced_ai/` is copied and re-specialized per assignment rather than imported from a common location. A typical assignment contains:

- `advanced_ai/` — the NumPy implementation package for that topic (e.g. `forest/isolation_forest.py`, `trees/decision_tree.py`), plus `config.py` (paths, random seed, hyperparameter grids), `data_utils.py`, `metrics.py`.
- `advanced_ai/self_checks.py` — hand-written `assert`-based checks (no pytest). Run with:
  ```bash
  python3 -m advanced_ai.self_checks
  ```
  from inside the assignment directory. Each check function is named `check_*` and wired into `run_all_checks()` at the bottom of the file — add new checks there when adding new functionality.
- `<topic>.ipynb` — the student-facing notebook that exercises the package.
- `lab<N>.tex` — the LaTeX assignment handout, also pulled into `ml/assignments/main.tex` (the combined assignment booklet).
- `prepare_datasets.py` / `scripts/prepare_all_data.py` — dataset staging into `datasets/` (gitignored; regenerated locally, not committed).
- `collectSubmission.sh` — runs `python3 makepdf.py <notebook>.ipynb`, which shells out to `jupyter nbconvert --to pdf`, to produce the graded PDF submission.

Setup uses conda: `environment-data.yml` (per assignment) defines env `ai_courses` (Python 3.11, numpy, matplotlib, jupyter, nbconvert). `scripts/prepare_all_data.sh` (where present) creates the env if missing and runs data prep inside it via `conda run -n ai_courses`. `requirements.txt` lists the same deps for a plain venv/pip setup.

When adding a new assignment, follow the newest existing one (`assignment7_forest_variants`) as the template rather than an older one — the self-check and data-prep conventions have evolved (e.g. assignment5 has no `scripts/` data-prep tooling or `forest/`-style subpackages; assignment7 does).

## Notation and pacing conventions

- Keep math notation consistent between a lecture and its corresponding assignment package (variable names in `advanced_ai/*.py` should match the symbols used in the matching `lecture0N_*.tex`).
- Lecture pacing pattern: short derivation → numerical example → graphic.
- `course-map.md` calls out cross-module forward/back references explicitly (e.g. Module 1 L14 forward-references Module 5's RLHF math) — check it when a lecture assumes prerequisite material from another module, since modules are authored out of strict numeric order.

## Uzbek translation rules

Uzbek text in this repo (video narration, on-screen labels, any Uzbek slide text) is spoken or read in the instructor's
own voice, so it must sound like them, not like a translation. Apply these whenever translating or writing Uzbek:

- **Terminology (instructor's choice, not negotiable):**
  - data → **berilganlar** (from Latin *datum*, "given"); dataset → **berilganlar toʻplami**. Never "maʼlumot(lar)" for
    data — **maʼlumot means *information*** and is used only in that sense (e.g. "ob-havo maʼlumoti").
  - descriptive → **tavsiflovchi** (e.g. "tavsiflovchi statistika"), not "tavsifiy".
  - population / sample → **bosh toʻplam / tanlanma**; spread → **tarqoqlik**; mean → **oʻrtacha qiymat**.
  - mode → **mod** (kept as the international term, not "moda").
  - label (a training example's target, as in labelled data) → **belgilanganlar**; data stays **berilganlar**.
- **Latin letters are spoken by their English names**, written in Uzbek spelling in the narration so the voice reads
  them right: x → eks, f → ef, n → en, s → es, i → ay, y → uay, A → ey, B → bi, C → si, Q → kyu, IQR → ay kyu ar
  (capitalized at a sentence start: "Eks ikki — …"). Greek letters keep their names (sigma, mu, omega). The screen
  shows the symbol itself.
- **English counterparts name the quantity, not the thing**: "farzandlar soni" → "number of children", never
  "children".
  Add new term decisions here as the instructor makes them.
- **Never translate word-for-word from English.** Write the sentence the way it would be said aloud in Uzbek: short
  active clauses, first-person-plural verbs, verb last. Example: "Toshkent qoʻshuv Samarqand, boʻlinsin ikki" (calque)
  → "Toshkent qoʻshuv Samarqand, va boʻlamiz ikkiga". Prefer "maʼnosi yoʻq" over "maʼnoga ega emas".
- **"We", not "you".** *Keling, …-aylik*, *tasavvur qilamiz*, *hisoblaymiz*, *misolimizda*. Videos open with
  "Assalomu alaykum, aziz doʻstlar"; transitions use "Xoʻp, endi", "Mana bu yerda", "Demak", "yaʼni"; a part ends with
  "Mana shu bilan … tugatamiz". Only the pause card ("Videoni toʻxtating") addresses the viewer directly. These come
  from the instructor's transcribed lectures.
- **Orthography:** oʻ/gʻ use U+02BB (ʻ), the tutuq belgisi uses U+02BC (ʼ). No Cyrillic or Turkish letters
  (scan: `grep -nP '[\x{0400}-\x{04FF}\x{0131}]'`).
- **Numbers are spelled out for the ear** ("ellik bir ming olti yuz oʻn uch dollar", "nol butun oʻndan besh") and
  must come from a captured script output, never retyped.
- **The instructor approves every Uzbek line before it is voiced or built.** Show the draft (Uzbek with the English
  alongside), apply their corrections, and record any new term or phrasing rule in this section.
