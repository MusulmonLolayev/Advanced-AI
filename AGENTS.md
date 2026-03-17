# AGENTS.md

## Scope
These instructions apply to the `Advanced AI` teaching workspace rooted here.

## Repository Purpose
- This workspace contains lecture and exercise material for an Advanced AI / Machine Learning course.
- The main authored content lives under `ml/`.
- `docs/` contains reference material, videos, candidate-selection files, and other supporting assets. Treat it as source/archive material unless a task explicitly targets it.

## Structure
- `ml/main.tex`: main Beamer lecture deck entrypoint.
- `ml/weeks/`: lecture content split by week.
- `ml/theme/`: shared Beamer theme and macros.
- `ml/assignments/main.tex`: assignment booklet entrypoint.
- `ml/figures/intro/`: generated intro figures.
- `ml/figures/knn/`: generated k-NN figures.
- `ml/scripts/generate_intro_graphics.py`: regenerates intro vector graphics.
- `ml/scripts/generate_knn_graphics.py`: regenerates k-NN teaching figures.
- `ml/course-map.md`: course outline and sequencing reference.

## Working Rules
- Preserve the existing course voice: direct, academic, practical, and example-driven.
- Keep notation consistent with the current LaTeX sources.
- When editing exercises, respect the explicit implementation policy already stated in the booklet:
  - k-NN coding tasks must use NumPy only for the core algorithm.
  - External libraries are allowed only for data loading or pretrained feature extraction when the exercise text says so.
  - Do not introduce scikit-learn nearest-neighbor implementations into student-facing solutions or instructions.
- Prefer editing the authored `.tex` or `.md` sources, not generated `.aux`, `.log`, `.nav`, `.toc`, `.out`, or compiled PDFs.
- Do not delete or rewrite files under `docs/Selection/` or `docs/Videos/` unless the task specifically requires it.

## Build and Verification
- Build the lecture deck from `ml/` with:
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
- Build the assignment booklet from `ml/assignments/` with:
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
- Regenerate figures when relevant before rebuilding slides/booklets:
  - `python3 ml/scripts/generate_intro_graphics.py`
  - `python3 ml/scripts/generate_knn_graphics.py`
- If a task changes TikZ/PGFPlots or figure scripts, verify that the corresponding PDF outputs are regenerated successfully.

## Editing Guidance
- New lecture content should generally go in `ml/weeks/` and be included from `ml/main.tex`.
- Shared commands or presentation styling belong in `ml/theme/` only when reuse is justified.
- Assignment additions should stay in `ml/assignments/main.tex` unless the assignment set is explicitly being split into multiple files.
- Keep generated figure filenames stable if they are already referenced by the LaTeX sources.

## Operational Notes
- This workspace may not be a git repository. Do not assume git commands will work.
- Prefer `rg` for search and keep changes localized to the files directly involved in the task.
