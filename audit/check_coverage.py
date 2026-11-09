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
    # The six original gaps remain individually traceable after follow-up.
    # This gate checks traceability, not the truth of a mathematical proof.
    followup = read("followup-status.json")
    assert followup["followup_base_commit"] == "25d4cdb06d3dfd5ce4e741c54c590c14f0b9c226"
    expected_targets = {("d02-bfv.tex", line) for line in (909, 1982, 2115, 2408)}
    expected_targets |= {("d03-ckks.tex", line) for line in (1925, 1936)}
    targets = followup["targets"]
    assert len(targets) == 6
    assert {(r["file"], r["original_line"]) for r in targets} == expected_targets
    for target in targets:
        record = by_id[target["record_id"]]
        for key in ("file", "original_line", "source_ledger"):
            assert record[key] == target[key], (target["record_id"], key)
        assert target["previous_status"] == "partially_verified"
        assert record["status"] == target["current_status"]
        assert target["verified_claims"] and target["remaining_scope"]
        assert target["evidence"] and all((HERE / path).is_file() for path in target["evidence"])
    # The unavailable complete Meta-BTS paper has not been silently certified.
    assert by_id["d03-ckks-050"]["status"] == "partially_verified"
    assert {r["record_id"] for r in records if r["status"] == "partially_verified"} == {"d03-ckks-050"}
    security = followup["security"]
    security_records = [r for r in records if "FND-035" in r["findings"]
                        and r["status"] == "corrected_with_pending_security"]
    assert len(security_records) == 11
    assert {r["record_id"] for r in security_records} == set(security["record_ids"])
    assert all((HERE / path).is_file() for path in security["evidence"])
    authored_security = {r["id"]: r for r in read("foundations-coverage.json")["records"]}
    for record in security_records:
        claims = record["security_subclaims"]
        assert claims == authored_security[record["record_id"]]["security_subclaims"], "lost or changed security subclaims during aggregation"
        assert claims and len({r["id"] for r in claims}) == len(claims)
        assert any(r["status"] == "conditional_reduction_complete" for r in claims)
        assert any(r["status"] == "concrete_parameters_uncertified" for r in claims)
        for claim in claims:
            assert claim["status"] in security["subclaim_statuses"]
            assert claim["statement"] and claim["conditions_or_remaining_obligation"] and claim["evidence"]
    for finding in findings:
        report = (HERE / finding["report"]).read_text()
        assert re.search(r"^#{2,4}\s+" + re.escape(finding["id"]) + r"\b", report, re.M), finding["id"]
    print(f"PASS: {len(chapters)} chapters, 288 original headings, 24 tables, 15 Python files, 19 figures; {len(records)} authored coverage records and {len(findings)} finding IDs. Six follow-up decisions traced; Meta-BTS full-paper gap and 11 security-instance boundaries preserved.")


if __name__ == "__main__":
    main()
