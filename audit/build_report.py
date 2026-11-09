#!/usr/bin/env python3
"""Build the complete Chinese academic-review PDF with Pandoc and XeLaTeX."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARTS = ["ACADEMIC_REVIEW.md", "FOLLOWUP_REVIEW.md", "security-followup.md",
         "bootstrap-followup.md", "ckks-followup.md", "openfhe-review.md",
         "foundations-review.md", "tfhe-bfv-review.md",
         "ckks-bgv-rns-review.md", "summary-review.md", "python-review.md",
         "findings-index.md", "coverage.md"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "build" / "audit")
    args = parser.parse_args()
    for tool in ["pandoc", "latexmk", "xelatex"]:
        if not shutil.which(tool):
            parser.error(f"{tool} is required; see audit/ACADEMIC_REVIEW.md")
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    parts = []
    for index, name in enumerate(PARTS):
        content = (HERE / name).read_text()
        if index == 0:
            content = re.sub(r"\A#[^\n]*", "# 总览与主要结论", content, count=1)
        else:
            content = "\\clearpage\n\n" + content
        # File links remain useful outside the checked-out repository.
        content = re.sub(r"\]\(([^():]+\.(?:md|json|py|cpp|txt)(?:#[^)]*)?)\)",
                         lambda m: "](https://github.com/wang2000star/fhe-textbook-cn/blob/chinese-edition/audit/" + quote(m[1], safe="/#") + ")", content)
        parts.append(content)
    markdown = destination / "complete-review.md"
    markdown.write_text("\n\n".join(parts))
    tex = destination / "fhe-textbook-academic-review.tex"
    subprocess.run([
        "pandoc", str(markdown), "--standalone", "--from=markdown+tex_math_dollars+tex_math_single_backslash+raw_tex",
        "--to=latex", "--output=" + str(tex), "--toc", "--toc-depth=1",
        "--lua-filter=" + str(HERE / "pdf-format.lua"),
        "--metadata=title:FHE Textbook 中英文版逐项学术审校",
        "--metadata=subtitle:原文核验 · 双语修订 · 反例与覆盖记录",
        "--metadata=date:2026-11-08",
        "--variable=documentclass:ctexart", "--variable=classoption:UTF8,fontset=fandol",
        "--variable=fontsize:10pt", "--variable=papersize:a4",
        "--variable=geometry:left=19mm,right=19mm,top=20mm,bottom=20mm",
        "--variable=mainfont:DejaVu Serif", "--variable=sansfont:DejaVu Sans",
        "--variable=mainfontoptions:AutoFakeSlant=0.2",
        "--variable=monofont:DejaVu Sans Mono", "--variable=mathfont:Latin Modern Math",
        "--variable=colorlinks:true", "--variable=linkcolor:blue", "--variable=urlcolor:blue",
        "--include-in-header=" + str(HERE / "report-header.tex"),
    ], cwd=ROOT, check=True)
    subprocess.run(["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
                    "-outdir=" + str(destination), str(tex)], cwd=destination, check=True)
    pdf = tex.with_suffix(".pdf")
    if not pdf.is_file():
        raise RuntimeError(f"Missing report output: {pdf}")
    print(f"Built complete academic review: {pdf}")


if __name__ == "__main__":
    main()
