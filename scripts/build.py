#!/usr/bin/env python3
"""Build the textbook PDFs with latexmk from any working directory."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EDITIONS = {
    "en": ("00-main.tex", "-pdf"),
    "zh": ("00-main-zh.tex", "-xelatex"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("language", choices=["en", "zh", "all"], nargs="?", default="zh")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "build")
    args = parser.parse_args()
    if not shutil.which("latexmk"):
        parser.error("latexmk is required. Install TeX Live (including XeLaTeX and Chinese support); see README.zh-CN.md.")
    languages = list(EDITIONS) if args.language == "all" else [args.language]
    if "zh" in languages:
        subprocess.run([sys.executable, str(ROOT / "scripts/check_translation.py")], cwd=ROOT, check=True)
    for language in languages:
        source, engine = EDITIONS[language]
        destination = args.output_dir.resolve() / language
        destination.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["latexmk", engine, "-interaction=nonstopmode", "-halt-on-error",
             "-file-line-error", f"-outdir={destination}", source],
            cwd=ROOT, check=True,
        )
        pdf = destination / Path(source).with_suffix(".pdf").name
        if not pdf.is_file():
            raise RuntimeError(f"The compiler did not produce {pdf}")
        print(f"Built {language}: {pdf}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode)
