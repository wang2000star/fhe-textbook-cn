#!/usr/bin/env python3
"""Validate review coverage and finding references; this is not a math proof."""
from collections import Counter
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def read(name):
    return json.loads((HERE / name).read_text())


def main():
    baseline, coverage, findings = read("baseline-headings.json"), read("coverage.json"), read("findings.json")
    assert baseline["baseline_commit"] == coverage["baseline_commit"] == "2a901038078fe054371e53089c86caaaa1112209"
    chapters = sorted(p.name for p in ROOT.glob("*.tex") if re.fullmatch(r"[abcd]\d{2}-.+\.tex", p.name))
    assert chapters == baseline["chapter_files"] and len(chapters) == 34
    for name in chapters:
        assert (ROOT / "zh-CN" / name).is_file(), name
    records = coverage["records"]
    ids = [r["record_id"] for r in records]
    assert len(set(ids)) == len(ids), "duplicate coverage IDs"
    by_id = {r["record_id"]: r for r in records}
    finding_ids = {r["id"] for r in findings}
    assert len(finding_ids) == len(findings)
    for record in records:
        assert record["status"] and record["review"], record["record_id"]
        assert (ROOT / record["file"]).is_file(), record["file"]
        assert set(record["findings"]) <= finding_ids, record["record_id"]
        assert (HERE / record["source_ledger"]).is_file()
    expected = {(h["file"], h["ordinal"]): h for h in baseline["headings"]}
    mapping = coverage["baseline_heading_mapping"]
    assert len(mapping) == len(expected) == 288
    assert {(m["file"], m["ordinal"]) for m in mapping} == set(expected)
    for item in mapping:
        heading, record = expected[(item["file"], item["ordinal"])], by_id[item["record_id"]]
        assert (record["file"], record["original_line"], record["kind"]) == (heading["file"], heading["original_line"], heading["kind"])
        assert not record["added_during_audit"]
        assert re.sub(r"\s+", "", record["heading"]) == re.sub(r"\s+", "", heading["heading"])
    reviewed_chapters = {r["file"] for r in records if r["kind"] in {"chapter", "introduction"}}
    assert set(chapters) <= reviewed_chapters
    assert sum(r["kind"] == "table" for r in records) == 24
    code_files = {str(p.relative_to(ROOT)) for p in (ROOT / "source code").glob("*.py")}
    assert code_files == {r["file"] for r in records if r["kind"] == "python-file"} and len(code_files) == 15
    assets = {str(p.relative_to(ROOT)) for p in (ROOT / "figures").iterdir() if p.is_file()}
    assert assets == {r["file"] for r in records if r["kind"] == "figure"} and len(assets) == 19
    # Guard against silently upgrading documented proof gaps during aggregation.
    assert any(r["status"] == "corrected_with_pending_security" and "FND-035" in r["findings"] for r in records)
    assert sum(r["status"] == "partially_verified" and r["source_ledger"] == "tfhe-bfv-coverage.json" for r in records) == 4
    assert sum(r["status"] == "partially_verified" and r["source_ledger"] == "ckks-bgv-rns-coverage.json" for r in records) == 2
    for finding in findings:
        report = (HERE / finding["report"]).read_text()
        assert re.search(r"^#{2,4}\s+" + re.escape(finding["id"]) + r"\b", report, re.M), finding["id"]
    print(f"PASS: {len(chapters)} chapters, 288 original headings, 24 tables, 15 Python files, 19 figures; {len(records)} authored coverage records and {len(findings)} finding IDs. Pending/partial states preserved.")


if __name__ == "__main__":
    main()
