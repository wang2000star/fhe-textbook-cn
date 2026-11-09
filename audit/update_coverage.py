#!/usr/bin/env python3
"""Assemble authored review ledgers; never infer review status from source text.

Run after editing a group report or ledger. The baseline inventory is a fixed
snapshot extracted from the stated Git commit, not a list of current headings.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GROUPS = ["foundations", "tfhe-bfv", "ckks-bgv-rns", "summary", "python"]
STATUS = {
    "corrected": "已修正",
    "corrected_with_pending_security": "已修正；具体安全范围未认证",
    "checked_under_stated_conditions": "按所列条件核查",
    "verified_with_conditions": "条件性核验",
    "checked_with_conditions": "条件性核验",
    "checked_no_independent_issue": "未发现独立问题",
    "reviewed_no_independent_issue": "未发现独立问题",
    "partially_verified": "部分核验；保留边界",
    "reviewed_correct": "已核查原内容",
    "conditions_added": "已补必要条件",
    "reviewed_scope_external": "代码审校另列",
    "validated_under_conditions": "条件下核验",
    "reviewed_no_material_issue": "未发现独立问题",
    "reviewed_corrected_or_clarified": "修正/补充条件",
    "reviewed_corrected": "已修正",
    "reviewed_clarified": "已澄清",
    "reviewed_with_limitations": "核查；保留边界",
    "reviewed_with_documented_limitations": "核查；保留边界",
    "reviewed_in_context": "结合正文核查",
    "reviewed_unused_asset": "未使用资源已检查",
}


def read_json(name):
    return json.loads((HERE / name).read_text())


def write_json(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def plain_heading(text):
    """Readable table labels only; exact original TeX remains in the JSON."""
    text = re.sub(r"\\href\{[^{}]*\}\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\cite\{[^{}]*\}", "", text)
    for _ in range(5):
        text = re.sub(r"\\(?:textsf|textbf|textit|texttt|textrm|underline|bm|vec|mathbb|mathcal)\{([^{}]*)\}", r"\1", text)
    for old, new in {r"\Delta": "Δ", r"\beta": "β", r"\sigma": "σ", r"\gamma": "γ", r"\ell": "ℓ", r"\rightarrow": "→", r"\times": "×"}.items():
        text = text.replace(old, new)
    text = re.sub(r"\\([A-Za-z]+)", r"\1", text)
    text = re.sub(r"[$}{]", "", text).replace("|", r"\|")
    return re.sub(r"\s+", " ", text).strip()


def records_from(group):
    name = group + "-coverage.json"
    data = read_json(name)
    rows = data if isinstance(data, list) else data.get("records", data.get("units"))
    assert isinstance(rows, list), name
    result = []
    for i, row in enumerate(rows, 1):
        unit = row.get("unit", "")
        kind = row.get("kind", row.get("heading_command"))
        if not kind:
            if unit.startswith("table-"):
                kind = "table"
            elif unit == "file-level-academic-code-review":
                kind = "python-file"
            elif unit == "demo-capability-paragraph":
                kind = "chapter"
            else:
                kind = unit.split("-")[0]
        notes = row.get("review", row.get("reasoning", row.get("checks", [])))
        if isinstance(notes, list):
            notes = "；".join(notes)
        result.append({
            "record_id": row.get("id", row.get("unit_id", f"{group}-{i:03d}")),
            "file": row["file"],
            "kind": kind,
            "heading": row["heading"],
            "original_line": row.get("baseline_line", row.get("original_line", row.get("line_start"))),
            "label": row.get("own_label", row.get("label")),
            "added_during_audit": row.get("added_during_audit", False),
            "status": row["status"],
            "findings": row.get("findings", []),
            "review": notes,
            "source_ledger": name,
        })
        # Preserve authored subclaim distinctions: a completed conditional
        # reduction and uncertified concrete parameters are different claims.
        if "security_subclaims" in row:
            result[-1]["security_subclaims"] = row["security_subclaims"]
        if "followup" in row:
            result[-1]["followup"] = row["followup"]
    return result


def main():
    baseline = read_json("baseline-headings.json")
    records = [record for group in GROUPS for record in records_from(group)]
    for i, asset in enumerate(read_json("figure-coverage.json"), 1):
        records.append({
            "record_id": f"FIG-{i:03d}", "file": asset["file"], "kind": "figure",
            "heading": Path(asset["file"]).name, "original_line": None, "label": None,
            "added_during_audit": False, "status": asset["status"], "findings": [],
            "review": asset["review"], "source_ledger": "figure-coverage.json",
        })
    finding_files = {}
    for record in records:
        for finding in record["findings"]:
            finding_files.setdefault(finding, set()).add(record["file"])
    findings = []
    for group in GROUPS:
        report = group + "-review.md"
        text = (HERE / report).read_text()
        for match in re.finditer(r"^#{2,4}\s+((?:FND|TB|CBR|SUM|CODE)-\d{3})[：: \u3000—-]*(.+)$", text, re.M):
            identifier, title = match.groups()
            findings.append({"id": identifier, "title": title.strip(), "report": report,
                             "files": sorted(finding_files.get(identifier, []))})
    known = {x["id"] for x in findings}
    assert len(known) == len(findings), "duplicate finding IDs"
    missing = set(finding_files) - known
    assert not missing, f"unresolved findings: {sorted(missing)}"
    heading_kinds = {"section", "subsection", "subsubsection", "paragraph", "subparagraph", "para"}
    lookup = {}
    for record in records:
        if record["kind"] in heading_kinds and not record["added_during_audit"]:
            key = (record["file"], record["original_line"], record["kind"])
            assert key not in lookup, f"duplicate heading record: {key}"
            lookup[key] = record
    mapping = []
    for heading in baseline["headings"]:
        key = (heading["file"], heading["original_line"], heading["kind"])
        assert key in lookup, f"unreviewed baseline heading: {key}"
        record = lookup[key]
        assert re.sub(r"\s+", "", heading["heading"]) == re.sub(r"\s+", "", record["heading"]), (key, heading["heading"], record["heading"])
        mapping.append({"file": heading["file"], "ordinal": heading["ordinal"], "record_id": record["record_id"]})
    assert len(mapping) == len(lookup), "extra/misclassified baseline heading records"
    counts = Counter(record["kind"] for record in records)
    output = {
        "schema_version": 1, "review_date": "2026-11-08",
        "baseline_commit": baseline["baseline_commit"],
        "policy": "Review status comes from authored ledgers, never from heading extraction or test success. Changes to original partial/pending states require the explicit evidence and remaining scope recorded in followup-status.json.",
        "counts": {"chapter_files": len(baseline["chapter_files"]), "baseline_headings": len(mapping),
                   "records": len(records), "findings": len(findings), "record_kinds": dict(counts),
                   "statuses": dict(Counter(r["status"] for r in records))},
        "baseline_heading_mapping": mapping, "records": records,
    }
    write_json("coverage.json", output)
    write_json("findings.json", findings)
    lines = ["# 全部审校条目索引", "", f"共 {len(findings)} 个稳定编号。相关条目可能描述同一根因在不同章节、概要或代码中的表现，不能相加为独立漏洞数量。完整判定、证据与修订见各分组报告。", ""]
    for group in GROUPS:
        report = group + "-review.md"
        title = (HERE / report).read_text().splitlines()[0].lstrip("# ")
        lines += [f"## {title}", "", f"详细报告：[{report}]({report})。", "", "| 编号 | 事项 |", "|---|---|"]
        for finding in findings:
            if finding["report"] == report:
                lines.append(f"| {finding['id']} | {plain_heading(finding['title'])} |")
        lines.append("")
    (HERE / "findings-index.md").write_text("\n".join(lines).rstrip() + "\n")
    lines = ["# 逐项覆盖清单", "", f"基线 `{baseline['baseline_commit']}`；{len(baseline['chapter_files'])} 个章节、{len(mapping)} 个原始标题单元均有对应的实际审查记录。共 {len(records)} 条覆盖记录还包括章节整体、定理框、24 个比较主题、代码、图形、前言和参考文献。计数有包含关系，不应当作互不重叠的文本单元。", "", "原始 TeX 标题、标签、逐项核查理由及分组来源见 `coverage.json`。本表为可读索引；标题去掉了排版宏。‘按条件核查’不表示具体参数已获安全认证；续审状态变化须有 followup-status.json 中的逐项证明与边界记录。FND-035 的已完成条件性归约和未认证参数分别保存在 security_subclaims 中。新增标题明确标记，不计入 288 个原始标题。", ""]
    files = baseline["chapter_files"] + ["00-main.tex", "z-bibfile.bib"]
    files += sorted({r["file"] for r in records if r["kind"] in {"python-file", "figure"}})
    for file in files:
        selected = [r for r in records if r["file"] == file]
        if not selected:
            continue
        lines += [f"## {file}", "", "| 原位置 / 类型 | 审查单元 | 状态及关联条目 |", "|---|---|---|"]
        for record in selected:
            where = (str(record["original_line"]) if record["original_line"] is not None else "—") + " / " + record["kind"]
            if record["added_during_audit"]:
                where = "本轮新增 / " + record["kind"]
            status = STATUS.get(record["status"], record["status"])
            refs = ", ".join(record["findings"])
            lines.append(f"| {where} | {plain_heading(record['heading'])} | {status}" + (f"；{refs}" if refs else "") + " |")
        if selected[0]["kind"] in {"python-file", "figure"}:
            lines += ["", selected[0]["review"]]
        lines.append("")
    (HERE / "coverage.md").write_text("\n".join(lines).rstrip() + "\n")
    print(json.dumps(output["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
