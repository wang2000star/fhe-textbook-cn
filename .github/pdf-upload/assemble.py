#!/usr/bin/env python3
"""Assemble the three reviewed PDFs; never build, commit, or push."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

COMMIT = "92900a4923efd2a1c984f0365eef5650d2010ac2"
RUN = 42675134457
IDS = {"en": 13700880661, "zh": 13700266478}
REPO = "wang2000star/fhe-textbook-cn"
DEST = {"en": "pdf/fhe-textbook-en.pdf", "zh": "pdf/fhe-textbook-zh.pdf",
        "report": "pdf/fhe-textbook-academic-review.pdf"}
INTRO = "本仓库在保留英文源码的基础上，提供对应的 **34 个章节中文译本**和独立中文 PDF 编译入口。\n\n"
START, END = "<!-- published-pdf-links:start -->", "<!-- published-pdf-links:end -->"
LINKS = (START + "\n- [中文教材 PDF](pdf/fhe-textbook-zh.pdf)\n"
         "- [英文教材 PDF](pdf/fhe-textbook-en.pdf)\n"
         "- [逐项学术审校报告 PDF](pdf/fhe-textbook-academic-review.pdf)\n" + END + "\n\n")
POLICY = ("The source_sha256 mapping records the explicitly listed academic-review source paths, "
          "excluding this validation file. Published PDFs and their byte hashes are separately "
          "recorded in pdf/manifest.json. The README.md digest reflects the publication links; "
          "earlier academic checks and local PDF build records are unchanged.")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def inside(root, name):
    path = (root / name).resolve()
    require(not Path(name).is_absolute() and path.is_relative_to(root), "Path escapes repository")
    return path


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
    try:
        temporary.chmod(0o644)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def assemble(root):
    root = root.resolve()
    manifest = json.loads(inside(root, ".github/pdf-upload/manifest.json").read_text("utf-8"))
    require(manifest["source_commit"] == COMMIT, "Unexpected source commit")
    require(manifest["textbook_run_id"] == RUN, "Unexpected artifact run")
    require(manifest["textbook_artifact_ids"] == IDS, "Unexpected artifact IDs")
    report, chunks = manifest["report"], []
    require(len(report["parts"]) == 8, "Expected eight report parts")
    require(len({p["path"] for p in report["parts"]}) == 8, "Duplicate report part path")
    for part in report["parts"]:
        data = inside(root, part["path"]).read_bytes()
        require(len(data) == part["bytes"] > 0, "Report part byte count mismatch: " + part["path"])
        require(sha(data) == part["sha256"], "Report part SHA-256 mismatch: " + part["path"])
        blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == part["blob_sha"], "Report part Git SHA mismatch")
        chunks.append(data)
    pdfs = {"en": inside(root, "build/published-en/00-main.pdf").read_bytes(),
            "zh": inside(root, "build/published-zh/00-main-zh.pdf").read_bytes(),
            "report": b"".join(chunks)}
    require(len(pdfs["report"]) == report["bytes"], "Assembled report byte count mismatch")
    require(sha(pdfs["report"]) == report["sha256"], "Assembled report SHA-256 mismatch")
    for key, data in pdfs.items():
        require(len(data) > 16 and data.startswith(b"%PDF-") and data.rstrip().endswith(b"%%EOF"),
                "Empty PDF or missing header/final EOF: " + DEST[key])
    validation = json.loads(inside(root, "audit/validation.json").read_text("utf-8"))
    history = {key: {field: validation["pdfs"][key][field] for field in ("path", "pages", "sha256")}
               for key in DEST}
    require(history["report"]["sha256"] == report["sha256"], "Historical report hash differs")
    require(history["report"]["pages"] == report["pages"], "Historical report page count differs")
    old_readme = inside(root, "README.md").read_bytes()
    require(validation["source_sha256"]["README.md"] == sha(old_readme), "Prior README hash differs")
    readme = old_readme.decode("utf-8")
    require(readme.count(INTRO) == 1, "README introductory paragraph does not match exactly")
    if START in readme or END in readme:
        require(readme.count(START) == readme.count(END) == 1 and INTRO + LINKS in readme,
                "Existing publication block differs or moved")
        require(all(readme.count(path) == 1 for path in DEST.values()), "Duplicate PDF links")
    else:
        require(not any(path in readme for path in DEST.values()), "PDF links already exist")
        readme = readme.replace(INTRO, INTRO + LINKS, 1)
    readme_bytes = readme.encode("utf-8")
    # These are the only two changes to the academic validation record.
    validation["source_sha256"]["README.md"] = sha(readme_bytes)
    validation["source_hash_policy"] = POLICY
    run_url = f"https://github.com/{REPO}/actions/runs/{RUN}"
    commit_url = f"https://github.com/{REPO}/commit/{COMMIT}"
    published = {
        "schema_version": 1, "repository": REPO, "source_commit": COMMIT, "source_commit_url": commit_url,
        "textbook_source": {"workflow_run_id": RUN, "workflow_run_url": run_url, "artifact_ids": IDS},
        "files": {key: {"path": DEST[key], "bytes": len(data), "sha256": sha(data),
                       "origin": "local reviewed PDF" if key == "report" else "GitHub Actions artifact",
                       **({"artifact_id": IDS[key]} if key in IDS else {})} for key, data in pdfs.items()},
        "report_transport_verification": {
            "parts": report["parts"], "bytes": report["bytes"], "sha256": report["sha256"],
            "pages_from_local_validation": report["pages"],
            "note": "Part paths are temporary publication inputs, removed after assembly."},
        "historical_local_pdf_validation": {
            "source": "audit/validation.json at the reviewed source commit", "pdfs": history,
            "note": "Earlier local-build hashes are historical. Published textbook bytes are independently "
                    "hashed above; equality between CI binaries and local binaries is not assumed."},
        "publication_checks": {"report_part_bytes_sha256_and_git_blob_sha": "passed",
                               "report_aggregate_bytes_and_sha256": "passed",
                               "all_pdf_headers_and_final_eof_markers": "passed",
                               "scope": "Transport/file-identity checks; no new build or academic tests."}}
    pdf_readme = (
        "# PDF 下载\n\n- [中文教材 PDF](fhe-textbook-zh.pdf)\n- [英文教材 PDF](fhe-textbook-en.pdf)\n"
        "- [逐项学术审校报告 PDF](fhe-textbook-academic-review.pdf)\n\n"
        f"来源提交：[{COMMIT}]({commit_url})。\n\n"
        f"两版教材来自该提交的 [Textbook PDFs 工作流]({run_url})；审校报告来自已验证的本地构建。\n\n"
        "文件大小、SHA-256 和来源见 [manifest.json](manifest.json)。其中保留的本地历史哈希"
        "不等同于 CI 生成文件的哈希。\n").encode("utf-8")
    outputs = {DEST[key]: data for key, data in pdfs.items()}
    outputs.update({"pdf/manifest.json": encode(published), "pdf/README.md": pdf_readme,
                    "README.md": readme_bytes, "audit/validation.json": encode(validation)})
    # Validate every input and destination before making any publication change.
    destinations = [(inside(root, path), data) for path, data in outputs.items()]
    for path, data in destinations:
        atomic_write(path, data)
    print(json.dumps({"status": "assembled", "source_commit": COMMIT, "files": published["files"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        assemble(args.root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"PDF publication assembly failed: {error}\n")
