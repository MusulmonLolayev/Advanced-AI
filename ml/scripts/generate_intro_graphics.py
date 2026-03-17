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
\begin{tikzpicture}[font=\small, >=Latex, line cap=round, line join=round]

% Panel backgrounds
\fill[blue!4] (0,0) rectangle (7.2,6.1);
\fill[orange!5] (8.0,0) rectangle (15.2,6.1);
\draw[rounded corners=5pt, draw=blue!45!black, line width=0.9pt] (0,0) rectangle (7.2,6.1);
\draw[rounded corners=5pt, draw=orange!55!black, line width=0.9pt] (8.0,0) rectangle (15.2,6.1);

% Titles
\node[font=\bfseries\small, text=blue!55!black] at (3.6,5.55) {Rule-based cell};
\node[font=\bfseries\small, text=orange!75!black] at (11.6,5.55) {Machine learning cell};

% Left panel: rule-based cell
\draw[fill=gray!23, draw=gray!55] (0.7,1.0) rectangle (6.5,1.38);
\foreach \x in {1.05,2.05,3.05,4.05,5.05} {
  \draw[fill=blue!35, draw=blue!65!black, rounded corners=1pt] (\x,1.38) rectangle ++(0.52,0.42);
}
\draw[fill=green!20, draw=green!45!black, rounded corners=2pt] (5.15,2.15) rectangle (6.25,2.78);
\node[font=\scriptsize] at (5.7,2.46) {sensor};
\draw[fill=white, draw=blue!55!black, rounded corners=2pt] (0.9,3.2) rectangle (2.65,4.0);
\node[font=\scriptsize] at (1.78,3.6) {rules};
\draw[line width=1.35pt, draw=black!70] (3.0,4.55) -- (3.95,4.55) -- (4.3,3.35);
\draw[line width=1.35pt, draw=black!70] (3.48,4.55) -- (3.48,3.1);
\fill[black!70] (3.48,3.1) circle (0.09);
\draw[fill=blue!12, draw=blue!55!black, rounded corners=2pt] (5.25,3.5) rectangle (6.35,4.15);
\node[font=\scriptsize] at (5.8,3.82) {bin};
\draw[->, thick, blue!70!black] (5.7,2.78) -- (5.7,3.5);
\draw[->, thick, blue!70!black] (2.65,3.6) -- (3.0,3.6);
\draw[->, thick, blue!70!black] (4.35,3.6) -- (5.25,3.82);
\node[font=\scriptsize, text=black!75] at (3.6,0.45) {same part shape, same route};

% Right panel: ML-enabled cell
\draw[fill=gray!23, draw=gray!55] (8.7,1.0) rectangle (14.5,1.38);
\draw[fill=orange!45, draw=orange!75!black, rounded corners=1pt] (9.05,1.38) rectangle ++(0.48,0.42);
\draw[fill=orange!45, draw=orange!75!black, rounded corners=1pt, rotate around={18:(10.18,1.6)}] (9.92,1.38) rectangle ++(0.52,0.4);
\draw[fill=red!45, draw=red!65!black] (11.32,1.6) circle (0.2);
\draw[fill=orange!45, draw=orange!75!black, rounded corners=1pt] (12.05,1.38) rectangle ++(0.34,0.58);
\draw[fill=red!45, draw=red!65!black] (13.18,1.6) circle (0.2);
\draw[line width=1.35pt, draw=black!70] (10.35,4.55) -- (11.25,4.55) -- (11.6,3.35);
\draw[line width=1.35pt, draw=black!70] (10.8,4.55) -- (10.8,3.1);
\fill[black!70] (10.8,3.1) circle (0.09);
\draw[fill=purple!15, draw=purple!55!black, rounded corners=2pt] (12.6,4.0) rectangle (13.95,4.75);
\fill[black!85] (12.95,4.42) circle (0.055);
\fill[black!85] (13.45,4.42) circle (0.055);
\draw[black!85, line width=0.45pt] (12.87,4.12) rectangle (13.53,4.24);
\node[font=\scriptsize] at (13.28,3.76) {camera};
\draw[fill=white, draw=orange!70!black, rounded corners=2pt] (8.45,3.2) rectangle (10.6,4.0);
\node[font=\scriptsize] at (9.52,3.6) {model};
\draw[fill=orange!12, draw=orange!70!black, rounded corners=2pt] (12.2,2.45) rectangle (13.25,3.1);
\draw[fill=red!12, draw=red!70!black, rounded corners=2pt] (13.45,2.45) rectangle (14.5,3.1);
\node[font=\scriptsize] at (12.72,2.78) {good};
\node[font=\scriptsize] at (13.98,2.78) {reject};
\draw[->, thick, orange!80!black] (13.28,4.0) -- (10.6,3.72);
\draw[->, thick, orange!80!black] (10.6,3.48) -- (11.75,3.48);
\draw[->, thick, orange!80!black] (11.75,3.48) -- (12.72,3.1);
\draw[->, thick, orange!80!black] (11.75,3.48) -- (13.98,3.1);
\node[font=\scriptsize, text=black!75] at (11.6,0.45) {different parts, learned routing};

% Separator text
\node[draw=none, fill=white, font=\bfseries\small, rounded corners=2pt] at (7.6,3.05) {vs};

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
