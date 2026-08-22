---
name: pandas-vector-graphics
description: Generates lecture/teaching graphics for this repo using Python + pandas for the underlying numeric data, rendered to vector PDF+SVG — never a rasterized PNG/JPEG. Two renderers are in use: TikZ/pgfplots (compiled via pdflatex) for most existing scripts, and matplotlib (direct fig.savefig) for chart-type figures going forward. Use this skill whenever creating or editing a ml/scripts/generate_*_graphics.py figure-generation script, or whenever asked to make a new chart/diagram/plot for a lecture slide in this course.
---

# Pandas -> Vector Graphics (PDF/SVG)

Every figure that ships in a lecture slide (`ml/figures/<topic>/*.pdf`) in
this course is produced by a `ml/scripts/generate_<topic>_graphics.py`
script, never hand-drawn or pulled from an external source. The data half is
always the same: **pandas DataFrame (or numpy, assembled into one) holds the
numbers.** Rendering that data uses one of two paths:

- **TikZ/pgfplots via pdflatex** — the original and still most common path
  (every script except `generate_tsne_graphics.py` as of this writing). See
  "The TikZ path" below.
- **matplotlib, saved directly to PDF/SVG** — the preferred path for new
  chart-type figures (scatter plots, line charts, small-multiples panels,
  bar charts): no TikZ coordinate-string building, no `pdflatex` subprocess,
  numerically identical output rendered more directly. `generate_tsne_graphics.py`
  is the reference implementation — read it end to end before writing a new
  matplotlib-based script. Use TikZ instead when a figure needs custom
  schematic geometry (annotated diagrams, hand-placed shapes/arrows tied to
  specific coordinates) that doesn't map cleanly onto a matplotlib chart type.

Either way, the deliverable is a vector PDF (the slides `\includegraphics`
it) and a vector SVG (kept alongside for non-LaTeX use) — raster formats
(PNG, JPEG) are not committed and are not an acceptable final output for a
course figure. A PNG screenshot of a figure is only ever a debugging/QA aid
(see the `latex-slide-fit` skill) — it is never what you write to
`ml/figures/<topic>/`.

Don't retrofit an existing TikZ script to matplotlib unless asked — the two
paths coexist per-script, not per-repo.

## The matplotlib path

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def save_fig(fig, name):
    fig.savefig(OUT_DIR / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT_DIR / f"{name}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✓ {name}.pdf")
    print(f"✓ {name}.svg")
```

Build each figure with `fig, ax = plt.subplots(figsize=(...))` (or
`plt.subplots(1, N, ...)` for side-by-side panels), plot from the
DataFrame/array directly (`ax.scatter`, `ax.plot`, `Circle` patches for
schematic shapes), then call `save_fig(fig, "<topic>_<name>")`. No
intermediate `.tex`/`.aux` files exist for this path, so there's nothing to
clean up on success and nothing to inspect on failure beyond the normal
Python traceback.

**Aspect ratio matters more here than with TikZ**: a matplotlib figure's
`figsize` directly sets the output PDF's page size (check with
`pdfinfo <file>.pdf | grep 'Page size'`), and a mismatch between that aspect
ratio and the `\includegraphics` column width it's placed into is the most
common cause of Beamer overflow for these figures (see `latex-slide-fit`).
For a figure going into a half-width two-column frame, prefer a wide/short
`figsize` (e.g. landscape multi-panel `plt.subplots(1, N, ...)`) over a
tall/narrow one.

## The TikZ path

This pipeline was established in `ml/scripts/generate_boosting_graphics.py`
and extended in `ml/scripts/generate_gmm_em_graphics.py` — read one of those
end to end as a working reference before writing a new TikZ-based script.
It is: **pandas DataFrame holds the numbers -> TikZ/pgfplots template
renders them -> pdflatex compiles to PDF -> dvisvgm converts the same PDF to
SVG.**

## Why pandas for the data

Every number that ends up plotted — a curve's sample points, a worked
numerical example's table, a synthetic dataset's coordinates — is built as a
`pandas.DataFrame` (or computed via `numpy` and assembled into one), even
when a plain Python list would "work." This keeps the data construction
inspectable and consistent with how the rest of the course's examples are
verified (compute the DataFrame, print it, sanity-check the numbers by hand
or by running the script standalone, *then* wire it into the TikZ template
or pass it straight to matplotlib). Do not skip straight to hardcoding
coordinate strings — derive them from a DataFrame/array even for a
four-point worked example.

## File layout

```python
BASE_DIR = Path(__file__).resolve().parents[1]      # ml/
OUT_DIR = BASE_DIR / "figures" / "<topic>"
OUT_DIR.mkdir(parents=True, exist_ok=True)
```

One script per lecture topic, producing every figure for that lecture. Each
topic directory needs a `.gitignore` (copy verbatim from an existing one,
e.g. `ml/figures/boosting/.gitignore`):

```
*.aux
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.tex
*.pdf
*.svg
```

Only the `.gitignore` itself is tracked — the generated PDF/SVG are build
artifacts regenerated by running the script, not committed binaries.

## The `compile_tikz` helper

Every script defines (or, if a second script in the same lecture's family
already exists, reuses the same shape of) this helper — copy it verbatim
into new scripts:

```python
def compile_tikz(content: str, name: str) -> None:
    """Write TikZ content to a .tex file and compile to PDF."""
    tex_path = OUT_DIR / f"{name}.tex"
    pdf_path = OUT_DIR / f"{name}.pdf"
    tex_path.write_text(content)
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
         "-output-directory", str(OUT_DIR), str(tex_path)],
        capture_output=True, text=True, cwd=str(OUT_DIR),
    )
    if result.returncode == 0:
        print(f"✓ {name}.pdf")
        svg_path = OUT_DIR / f"{name}.svg"
        svg_result = subprocess.run(
            ["dvisvgm", "--pdf", str(pdf_path), "-o", str(svg_path)],
            capture_output=True, text=True, cwd=str(OUT_DIR),
        )
        print(f"✓ {name}.svg" if svg_result.returncode == 0 else f"✗ {name}.svg - conversion failed")
        for ext in [".aux", ".log", ".tex"]:
            (OUT_DIR / f"{name}{ext}").unlink(missing_ok=True)
    else:
        print(f"✗ {name}.pdf - compilation failed")
        print(result.stdout[-1500:] if result.stdout else "")
```

Each figure in the script is one `<topic>_<descriptive_name>` standalone
document built as a string, then one `compile_tikz(tex_string, "name")` call.
On success the `.tex`/`.aux`/`.log` are deleted automatically — only the
`.pdf` and `.svg` remain. On failure, the `.tex` is deliberately *not*
deleted so you can inspect what was actually written and re-run `pdflatex`
on it directly to see the full error if the truncated stdout isn't enough.

## Building the TikZ string: avoid backslash hell

Two interpolation styles are both in use across this repo's scripts — pick
based on how much LaTeX-vs-Python content the figure mixes:

**String concatenation with raw strings** (preferred when most of the
content is literal LaTeX/TikZ and only a few numeric values are
data-driven): keep every literal LaTeX/TikZ chunk in its own `r"""..."""`
block (so backslashes need no escaping at all), and concatenate with plain
`f"{value:.3f}"` fragments only where a number must be inserted:

```python
tex = (
    r"""
\documentclass[crop]{standalone}
...
\addplot[...] coordinates {
"""
    + " ".join(f"({x:.3f},{y:.5f})" for x, y in zip(xs, ys))
    + r"""
};
\end{axis}
\end{tikzpicture}
\end{document}
"""
)
```

**Raw f-string (`rf"""..."""`)** (fine when there are many small numeric
interpolations scattered through otherwise-short LaTeX, e.g. several
`\node`/`\draw` coordinates computed from Python floats): the `r` makes
backslashes literal, so `\draw`, `\node`, `\mu` etc. need no escaping; just
remember every literal LaTeX `{`/`}` must be doubled (`{{`/`}}`) since the
`f` half of the string still treats single braces as interpolation syntax:

```python
tex = rf"""
\documentclass[crop]{{standalone}}
\node[font=\small] at (axis cs: {mu:.3f},{label_y:.4f}) {{$\mu$}};
"""
```

Whichever style you pick for a given figure, don't mix both *within the same
string* — it's how brace-mismatch bugs creep in. A bad sign during
debugging: if editing the surrounding Python text doesn't change the
resulting LaTeX output at all, suspect you're concatenating a stale/duplicate
string fragment, not that the edit was a no-op.

## Building shapes/geometry from real computation, not eyeballed numbers

Don't hand-place coordinates for anything that has a closed-form geometric
meaning — compute it:

- **Decision boundaries between two clusters**: perpendicular bisector of
  the two centroids, via `numpy` (`direction = cB - cA`,
  `perp = [-direction[1], direction[0]]`, normalize, scale to the desired
  line length).
- **Responsibility/posterior blending colors**: compute the actual
  posterior/responsibility value, then use TikZ's `colorA!XX!colorB` mixing
  syntax with `XX` set from that computed percentage — don't pick a color by
  eye.
- **Covariance ellipses**: eigendecompose the covariance matrix
  (`np.linalg.eigh`), take `V @ diag(sqrt(eigvals))` as a square root of
  $\Sigma$, apply it to unit-circle points, scale by the desired
  $n$-sigma — don't approximate an ellipse by guessing semi-axis lengths.
- **Pie-slice / split-probability glyphs**: either precompute arc endpoints
  via `numpy.cos`/`numpy.sin` in Python and pass them to TikZ's `arc` path
  operator, or — for an exact 50/50 split — clip a filled circle with two
  half-plane rectangles, which avoids angle arithmetic entirely and is
  preferable when the split is exactly even.

This keeps the figure correct if the underlying numbers (a worked example's
inputs, a dataset's points) ever change — rerunning the script regenerates a
geometrically consistent figure instead of a stale hand-tuned one.

## Verifying the numbers before trusting the figure

For a worked numerical example that the slide states specific values for
(e.g. "$\mu_1^{(1)} \approx 1.650$"), don't just trust the formula
transcription — actually run the computation (either inline in the script,
or via a quick standalone Python snippet importing the same helper
functions) and print the intermediate values, then check they match what's
written in the `.tex` prose. A formula that's subtly wrong (sign error,
wrong axis, off-by-one in a sum) will still compile a fine-looking plot.

## After generating

1. Run the script: `python3 ml/scripts/generate_<topic>_graphics.py` — every
   figure should print `✓ <name>.pdf` and `✓ <name>.svg`; a `✗` (TikZ path)
   means stop and read the captured `pdflatex` stdout before continuing, and
   a Python traceback (matplotlib path) means stop and fix it there.
2. Rasterize the new PDF standalone (e.g.
   `mutool draw -o /tmp/check.png -r 200 ml/figures/<topic>/<name>.pdf`) and
   `Read` it to sanity-check the figure looks like what you intended *before*
   wiring it into a lecture frame — this is much faster to iterate on than
   debugging it through a full Beamer recompile. For a matplotlib figure,
   also check `pdfinfo <file>.pdf | grep 'Page size'` against the frame's
   `\includegraphics` column width (see "Aspect ratio matters more here" above).
3. Only after the standalone figure looks right, embed it in the `.tex`
   lecture frame and follow the `latex-slide-fit` skill to make sure it fits.
