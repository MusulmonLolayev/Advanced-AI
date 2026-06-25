---
name: latex-slide-fit
description: Ensures Beamer/LaTeX slide content (text, equations, figures) actually fits within a frame's visible bounds instead of overflowing past the footer or getting clipped. Use this skill any time you add, edit, or compile a Beamer frame in this repo's lecture decks (ml/lectures/*.tex, main.tex) — especially after adding a figure, equation, or extra bullet to an existing frame, or after writing a brand-new lecture. Also use it whenever the user asks to "check slides fit", "fix overflow", "QA the deck", or reports clipped/cut-off content.
---

# LaTeX Slide Fit

Beamer silently overflows: a frame whose content is too tall does not error or
wrap — it just lets the bottom of the content run under the footer, where it
is invisible until someone actually looks at the rendered page. A clean
`pdflatex` exit code proves nothing about whether a human can read the slide.
This skill is the compile -> detect -> rasterize -> inspect -> fix loop that
catches this class of bug before the deck ships.

This convention was established authoring `ml/lectures/lecture08_boosting.tex`
and `ml/lectures/lecture09_gmm_em.tex` — follow it for every lecture in this
course.

## The loop

Run this after every edit that changes a frame's content (new bullet,
equation, included figure, block environment), not just at the end of a
session.

### 1. Compile twice

Beamer/LaTeX cross-references (`\eqref`, `\ref`) need a second pass to
resolve, and the second pass is also where stable Overfull/Underfull warnings
show up (the first pass can have spurious ones from `\label`s not existing
yet):

```bash
cd ml
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /tmp/c1.log 2>&1
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /tmp/c2.log 2>&1
```

Treat a non-zero exit / `-halt-on-error` abort as a hard failure — read the
log tail to find the actual LaTeX error before doing anything else.

### 2. Grep the second-pass log for warnings

```bash
grep -iE "overfull|underfull|undefined" /tmp/c2.log
```

- `Overfull \vbox (<N>pt too high) detected at line <L>` — content taller
  than the frame. `<L>` is the line number *in the currently-open source
  file* (the `.tex` file containing the frame, e.g.
  `ml/lectures/lectureNN_*.tex`), not in `main.tex`. It is almost always the
  `\end{frame}` line of the offending frame — read that file at `<L>` to
  identify which frame.
- `Underfull \hbox` — usually harmless spacing, but check if it coincides
  with a frame you just edited.
- `Undefined` — a `\ref`/`\eqref` to a label that doesn't exist; fix the
  label/reference, don't suppress it.

Zero warnings is the bar. Sub-1pt "overfull" warnings can occasionally be
real but invisible glue rounding — confirm with a visual check (next step)
before deciding a warning is cosmetic; don't assume.

### 3. Map warnings to page numbers, then rasterize

Find the shipped page number associated with the warning by looking at the
page-marker lines (`[N ...]`) around it in the log:

```bash
grep -n "Overfull\|^\[" /tmp/c2.log
```

A page marker `[N]` appears in the log right after the page is shipped, so a
warning printed just before `[N]` belongs to page `N`. Note that one `\frame`
with several `\pause`s produces multiple consecutive PDF pages (one per
overlay step) — a warning that repeats 3-4 times in a row at the same source
line is the same frame's overlay steps, not 3-4 different frames.

Rasterize the suspect page(s) at a readable resolution:

```bash
mutool draw -o /tmp/page_N.png -r 150 main.pdf N
```

### 4. Visually inspect with Read

Use the Read tool on the PNG. Look specifically at the bottom edge of the
slide against the footer bar — clipped text, a cut-off figure, or a bullet
that's simply missing (pushed past the visible frame) are the tell. Don't
stop at "the warning is small" — read the page.

### 5. Fix by shrinking, not by hiding

In order of preference:

1. **Shrink the figure itself at the source** — reduce the pgfplots/TikZ
   `width=`/`height=` in the generating Python script (see the
   `pandas-vector-graphics` skill) and regenerate the PDF, rather than only
   scaling `\includegraphics` width down. A figure rendered too large and
   then scaled down in LaTeX still reserves the same proportional vertical
   space relative to its own internal font sizes — shrinking at the
   `\includegraphics` width is usually enough and is the faster first try,
   but if you're already below ~0.5\linewidth and still overflowing, the
   figure's own aspect ratio is the problem.
2. **Reduce `\includegraphics[width=...]`** in the `.tex` frame — this is
   usually the fastest lever.
3. **Tighten vertical spacing** — add a small negative `\vspace{-Npt}`
   (start around 3-6pt) right after the element that's pushing things over,
   or shorten `\vspace` already present between elements.
4. **Compress text** — shorten a bullet to fewer words so it wraps to fewer
   lines; remove a redundant clause rather than rephrasing at the same
   length.
5. **Split the frame** — if a frame has too much *content* (not just a
   sizing problem — e.g. 4 bullets + a block + a figure all genuinely
   belong on screen at once), split it into two frames (`"Title"` and
   `"Title (cont.)"`) rather than cramming. This is the right call when
   steps 1-4 would require shrinking text/figures to the point of hurting
   readability.

After any fix, go back to step 1 — re-run the full two-pass compile and
re-grep. Don't assume a single edit fixed it; iterate until the grep is
empty AND the rasterized page looks right. Both checks matter: the log can
be clean while a figure still visually overlaps a bullet (rare but
possible with `\centering` figures with no surrounding box), and a fix can
reduce the overfull pt value to a y that still does not eliminate the
warning.

## Quick reference: common causes in this deck

- A frame that had 2-3 bullets and was fine, then gained an
  `\includegraphics` in the middle — almost always overflows immediately;
  budget for it preemptively by shrinking the image to ~0.5-0.65\textwidth
  for an image accompanied by bullets above *and* below it, vs. up to
  ~0.85\textwidth for an image-only frame.
- Two-column (`columns[T]`) frames: the overflow can come from *either*
  column independently — check both, don't assume the column with the
  figure is the culprit.
- pgfplots legends and axis labels add real vertical height beyond the
  plotted curve; account for `legend pos=north east` etc. eating into the
  visual budget you assumed from the `height=` value alone.
