#!/usr/bin/env python3
"""Generate vector introductory graphics as PDF files."""

from __future__ import annotations

import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "intro"


def write_rule_vs_ml_tex(path: Path) -> None:
    tex = r"""\documentclass[tikz,border=2pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,shapes.geometric,calc}

\begin{document}
\begin{tikzpicture}[font=\small, >=Latex, line cap=round, line join=round,
  stage/.style={draw, fill=white, rounded corners=2pt, align=center,
               minimum width=1.7cm, minimum height=0.85cm, inner sep=2pt},
  flow/.style={->, thick},
  link/.style={->, dashed, thin, black!55},
  arm/.style={line width=2.2pt, draw=black!65},
  joint/.style={circle, fill=white, draw=black!65, line width=0.8pt, inner sep=0pt, minimum size=4pt}]

% Robot arm: base at (#1,1.3), elbow at (#2,2.95), gripper closing on the part below x=#3
\newcommand{\robotarm}[3]{%
  \draw[fill=gray!55, draw=black!60] (#1-0.25,1.0) rectangle (#1+0.25,1.3);
  \draw[arm] (#1,1.3) -- (#2,2.95) -- (#3,2.08);
  \node[joint] at (#1,1.3) {};
  \node[joint] at (#2,2.95) {};
  \draw[line width=1.2pt, draw=black!65] (#3-0.26,2.03) -- (#3+0.26,2.03);
  \draw[line width=1.2pt, draw=black!65] (#3-0.26,2.03) -- (#3-0.26,1.6);
  \draw[line width=1.2pt, draw=black!65] (#3+0.26,2.03) -- (#3+0.26,1.6);
}

% Open-top bin between x=#1 and x=#2
\newcommand{\partbin}[4]{%
  \filldraw[fill=#3, draw=black!60, line width=0.8pt] (#1,1.75) -- (#1,1.0) -- (#2,1.0) -- (#2,1.75);
  \node[font=\scriptsize] at ({(#1+#2)/2},1.35) {#4};
}

% Panel backgrounds
\filldraw[fill=blue!4, draw=blue!45!black, rounded corners=5pt, line width=0.9pt] (0,0) rectangle (7.2,6.1);
\filldraw[fill=orange!5, draw=orange!55!black, rounded corners=5pt, line width=0.9pt] (8.0,0) rectangle (15.2,6.1);

% Titles
\node[font=\bfseries, text=blue!55!black] at (3.6,5.5) {Rule-based cell};
\node[font=\bfseries, text=orange!75!black] at (11.6,5.5) {Machine learning cell};

% ---------------- Left panel: rule-based cell ----------------
\node[stage, draw=blue!55!black] (L1) at (1.25,4.43) {part\\sensor};
\node[stage, draw=blue!55!black] (L2) at (3.6,4.43)  {if--then\\rules};
\node[stage, draw=blue!55!black] (L3) at (5.95,4.43) {fixed\\motion};
\draw[flow, blue!70!black] (L1) -- (L2);
\draw[flow, blue!70!black] (L2) -- (L3);

\draw[fill=gray!23, draw=gray!55] (0.35,1.0) rectangle (3.95,1.3);
\foreach \x in {0.55,1.25,1.95,2.65,3.35} {
  \draw[fill=blue!35, draw=blue!65!black, rounded corners=1pt] (\x,1.3) rectangle ++(0.42,0.42);
}
% photo-eye sensor above the conveyor
\draw[fill=green!25, draw=green!45!black, rounded corners=1pt] (1.26,2.95) rectangle (1.66,3.2);
\draw[red!60, dashed] (1.46,2.95) -- (1.46,1.78);
\draw[link] (1.46,3.2) -- (L1.south);

\robotarm{4.45}{4.15}{3.56}
\draw[link] (L3.south) -- (4.2,3.05);
\partbin{5.0}{6.85}{blue!12}{bin}

\node[font=\small, text=black!75] at (3.6,0.45) {same part shape, same route};

% ---------------- Right panel: machine learning cell ----------------
\node[stage, draw=orange!70!black] (R1) at (9.25,4.43)  {camera\\image};
\node[stage, draw=orange!70!black] (R2) at (11.6,4.43)  {learned\\model};
\node[stage, draw=orange!70!black] (R3) at (13.95,4.43) {good /\\reject};
\draw[flow, orange!80!black] (R1) -- (R2);
\draw[flow, orange!80!black] (R2) -- (R3);

\draw[fill=gray!23, draw=gray!55] (8.35,1.0) rectangle (11.95,1.3);
\draw[fill=orange!45, draw=orange!75!black, rounded corners=1pt] (8.55,1.3) rectangle ++(0.42,0.42);
\draw[fill=orange!45, draw=orange!75!black, rounded corners=1pt, rotate around={18:(9.46,1.51)}] (9.25,1.3) rectangle ++(0.42,0.36);
\draw[fill=red!45, draw=red!65!black] (10.16,1.51) circle (0.21);
\draw[fill=orange!45, draw=orange!75!black, rounded corners=1pt] (10.7,1.3) rectangle ++(0.3,0.55);
\draw[fill=red!45, draw=red!65!black] (11.56,1.51) circle (0.21);
% camera above the conveyor, with its field of view
\draw[fill=purple!15, draw=purple!55!black, rounded corners=1pt] (9.35,2.95) rectangle (9.85,3.25);
\fill[purple!55!black] (9.6,3.1) circle (0.06);
\draw[purple!45, dashed] (9.45,2.95) -- (8.75,1.8);
\draw[purple!45, dashed] (9.75,2.95) -- (10.45,1.8);
\draw[link] (9.6,3.25) -- (R1.south);

\robotarm{12.45}{12.15}{11.56}
\draw[link] (R3.south) -- (12.2,3.05);
\partbin{12.95}{13.95}{green!15}{good}
\partbin{14.05}{15.0}{red!12}{reject}

\node[font=\small, text=black!75] at (11.6,0.45) {different parts, learned routing};

% Separator text
\node[font=\bfseries] at (7.6,3.05) {vs};

\end{tikzpicture}
\end{document}
"""
    path.write_text(tex, encoding="utf-8")


def compile_tex(tex_path: Path) -> None:
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
        cwd=tex_path.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to compile {tex_path.name}\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tex_path = OUT_DIR / "manufacturing_rule_vs_ml.tex"
    write_rule_vs_ml_tex(tex_path)
    compile_tex(tex_path)
    print(f"Saved vector intro graphics to: {OUT_DIR}")


if __name__ == "__main__":
    main()
