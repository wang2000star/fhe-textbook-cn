#!/usr/bin/env python3
"""Check the Chinese chapters against the English source using only the stdlib.

The default checks are strict structural checks.  Existing duplicate/undefined
labels in the English edition are reported as a baseline, not as regressions.
``--math`` additionally compares multisets of normalized mathematical snippets;
differences require manual review and make the command fail.  This is a lexical
checker, not a TeX interpreter or a proof of mathematical/translation accuracy.
It does not expand macros or evaluate arbitrary TeX conditionals.  Compile both
editions as well, and review any intended changes rather than disabling checks.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Iterator


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = re.compile(r"[abcd]\d{2}-[^/]+\.tex\Z")
REF_COMMANDS = {"ref", "autoref", "nameref", "eqref", "pageref", "cref", "Cref"}
SECTION_COMMANDS = {
    "part", "chapter", "section", "subsection", "subsubsection",
    "paragraph", "subparagraph", "para",
}
VERBATIM_ENVS = {"verbatim", "verbatim*", "Verbatim", "lstlisting", "minted"}
URL_COMMANDS = {"href", "url", "nolinkurl", "path"}
MATH_ENVS = {
    "equation", "equation*", "align", "align*", "alignat", "alignat*",
    "gather", "gather*", "multline", "multline*", "eqnarray", "eqnarray*",
    "displaymath", "math", "flalign", "flalign*",
}
TEXT_COMMANDS = {"text", "textrm", "textbf", "textit", "textsf", "textnormal", "mbox"}
# Single-word prose is otherwise ambiguous with a mathematical identifier.
# Keep unfamiliar identifiers (ct, evk, RLWE, ModRaise, ...) unchanged.
PROSE_WORDS = {
    "a", "an", "and", "or", "where", "since", "because", "if", "then",
    "otherwise", "for", "the", "is", "are", "small", "large", "noise",
    "error", "message", "plaintext", "ciphertext", "input", "output",
    "integer", "coefficient", "coefficients", "constant", "rounding",
    "level", "maximum", "minimum", "degree", "modulus", "times", "effect",
    "repetitions",
}


def blank(text: str) -> str:
    """Keep line numbers stable while masking content that is not active TeX."""
    return "".join("\n" if ch == "\n" else " " for ch in text)


def command_at(text: str, pos: int) -> tuple[str, bool, int]:
    """Read a control word or control symbol; do not misread \\\\ as a command."""
    match = re.match(r"\\([A-Za-z@]+)(\*)?", text[pos:])
    if match:
        return match[1], bool(match[2]), pos + match.end()
    return text[pos + 1:pos + 2], False, min(pos + 2, len(text))


def group_at(text: str, pos: int, opening: str = "{") -> tuple[str, int, int] | None:
    """Return (body, opening position, end) for a balanced TeX group."""
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != opening:
        return None
    closing = "}" if opening == "{" else "]"
    start, depth, brace_depth = pos, 1, 0
    pos += 1
    while pos < len(text):
        ch = text[pos]
        if ch == "\\":
            # Escaped braces/percent signs and control symbols are indivisible.
            _, _, pos = command_at(text, pos)
            continue
        if opening == "[" and ch in "{}":
            brace_depth += 1 if ch == "{" else -1
        if not brace_depth:
            if ch == opening:
                depth += 1
            elif ch == closing:
                depth -= 1
                if depth == 0:
                    return text[start + 1:pos], start, pos + 1
        pos += 1
    raise ValueError(f"unclosed {opening!r} group near line {text.count(chr(10), 0, start) + 1}")


def skip_options(text: str, pos: int) -> int:
    while True:
        group = group_at(text, pos, "[")
        if group is None:
            return pos
        pos = group[2]


def active_tex(text: str) -> str:
    """Mask comments/verbatim, preserving escaped % and visible hyperlink text.

    Hyperref reads URL arguments with special catcodes.  In particular, %20 in
    ``\\href{.../source%20code/...}{visible text}`` must not turn the remainder
    of the line into a comment.  URL targets are masked before comment handling;
    the visible second argument of \\href is still checked normally.
    """
    pieces: list[str] = []
    pos = 0
    while pos < len(text):
        if text[pos] == "%":
            end = text.find("\n", pos)
            end = len(text) if end < 0 else end
            pieces.append(blank(text[pos:end]))
            pos = end
            continue
        if text[pos] != "\\":
            pieces.append(text[pos])
            pos += 1
            continue
        name, star, end = command_at(text, pos)
        if name == "verb" and end < len(text):
            delimiter = text[end]
            stop = text.find(delimiter, end + 1)
            if stop < 0:
                raise ValueError("unterminated \\verb")
            pieces.append(blank(text[pos:stop + 1]))
            pos = stop + 1
            continue
        if name in URL_COMMANDS:
            group = group_at(text, skip_options(text, end))
            if group is not None:
                _, start, stop = group
                pieces.append(text[pos:start + 1] + blank(text[start + 1:stop - 1]) + "}")
                pos = stop
                continue
        if name == "begin":
            group = group_at(text, end)
            if group and group[0] in VERBATIM_ENVS | {"comment"}:
                environment = group[0]
                closing = re.search(r"\\end\s*\{" + re.escape(environment) + r"\}", text[group[2]:])
                if closing is None:
                    raise ValueError(f"unterminated {environment!r} environment")
                stop_start = group[2] + closing.start()
                stop_end = group[2] + closing.end()
                if environment == "comment":
                    pieces.append(blank(text[pos:stop_end]))
                else:
                    pieces.append(text[pos:group[2]])
                    pieces.append(blank(text[group[2]:stop_start]))
                    pieces.append(text[stop_start:stop_end])
                pos = stop_end
                continue
        if name == "ignore":
            group = group_at(text, end)
            if group is not None:
                pieces.append(blank(text[pos:group[2]]))
                pos = group[2]
                continue
        pieces.append(text[pos:end])
        pos = end
    return "".join(pieces)


def commands(text: str) -> Iterator[tuple[str, bool, int, int]]:
    pos = 0
    while pos < len(text):
        if text[pos] == "\\":
            name, star, end = command_at(text, pos)
            yield name, star, pos, end
            pos = end
        else:
            pos += 1


def key(text: str) -> str:
    return re.sub(r"\s+", "", text)


def tex_path(text: str) -> str:
    return str(PurePosixPath(text.strip()))


def chapter_path(text: str) -> str | None:
    path = tex_path(text)
    if not path.endswith(".tex"):
        path += ".tex"
    return path if CHAPTER.fullmatch(PurePosixPath(path).name) else None


def metrics(text: str) -> dict[str, Counter]:
    result = {name: Counter() for name in (
        "labels", "references", "citations", "environments", "graphics", "sections", "inputs",
    )}
    for name, star, _, end in commands(text):
        command = name + ("*" if star else "")
        if name in SECTION_COMMANDS:
            result["sections"][command] += 1
        if name not in {"label", "begin", "end", "includegraphics", "input", "include"} | REF_COMMANDS and not name.lower().startswith("cite") and name != "nocite":
            continue
        group = group_at(text, skip_options(text, end))
        if group is None:
            # TeX also accepts unbraced \input file; this repo uses it for pdf-trans.
            if name in {"input", "include"}:
                match = re.match(r"\s*([^\s{}\\]+)", text[end:])
                if match:
                    result["inputs"][tex_path(match[1])] += 1
            continue
        argument = group[0]
        if name == "label":
            result["labels"][key(argument)] += 1
        elif name in REF_COMMANDS:
            for target in argument.split(","):
                result["references"][(command, key(target))] += 1
        elif name.lower().startswith("cite") or name == "nocite":
            for target in argument.split(","):
                result["citations"][(command, key(target))] += 1
        elif name in {"begin", "end"}:
            result["environments"][(name, key(argument))] += 1
        elif name == "includegraphics":
            result["graphics"][tex_path(argument)] += 1
        else:
            result["inputs"][tex_path(argument)] += 1
    return result


@dataclass
class Document:
    path: Path
    active: str
    stats: dict[str, Counter]

    @classmethod
    def read(cls, path: Path) -> "Document":
        active = active_tex(path.read_text(encoding="utf-8"))
        return cls(path, active, metrics(active))


def text_payload(body: str) -> str:
    """Normalize prose in math text without discarding math identifiers.

    Pure identifiers are retained.  Natural-language words can change language,
    but numbers, acronyms and isolated variable letters in prose are retained.
    Mixed/nested TeX is handled conservatively rather than discarded wholesale.
    """
    if not body.strip():
        return ""
    regions = list(math_regions(body))
    if regions:
        # Text annotations can contain real math, e.g. \text{the first $n/2$
        # elements}.  Translate the surrounding prose while strictly retaining
        # these nested formulas and their multiplicities, even if grammar moves
        # independent snippets within the annotation.
        prose_parts = []
        formulas = []
        last = 0
        for start, end, snippet in regions:
            prose_parts.append(body[last:start])
            formulas.append(normalize_math(snippet))
            last = end
        prose_parts.append(body[last:])
        prose = text_payload("".join(prose_parts))
        return "<text:" + prose + "|math:" + "|".join(sorted(formulas)) + ">"
    if any(ch in body for ch in "\\${}"):
        return normalize_math(body)
    # English possessives attached to a preceding math island are not a new
    # mathematical variable named s.
    body = re.sub(r"['’]s\b", "", body)
    words = re.findall(r"[A-Za-z]+|\d+(?:\.\d+)?", body)
    chinese = bool(re.search(r"[\u3400-\u9fff]", body))
    prose = chinese or len(words) > 1 or (words and words[0].lower() in PROSE_WORDS)
    if not prose:
        return re.sub(r"\s+", "", body.translate(str.maketrans("（），：；", "(),:;")))
    identifiers = [word for word in words if (
        word[0].isdigit()
        or (word.isupper() and word.lower() not in PROSE_WORDS)
        or (len(word) == 1 and word.lower() != "a")
        or (any(ch.isupper() for ch in word[1:]) and not word.isupper())
    )]
    return "<prose:" + ",".join(identifiers) + ">"


def normalize_math(text: str) -> str:
    # A cross-reference wrapped in $...$ carries no algebra.  Moving it back
    # to text mode fixes CJK glyph rendering; the strict reference counter still
    # checks its exact command, key and number of occurrences.
    reference = re.fullmatch(r"\s*\\(?:ref|autoref|nameref|eqref|pageref)\*?\s*\{[^{}]+\}\s*", text)
    if reference:
        return ""
    pieces: list[str] = []
    pos = 0
    while pos < len(text):
        if text[pos] != "\\":
            pieces.append(text[pos])
            pos += 1
            continue
        name, _, end = command_at(text, pos)
        if name in TEXT_COMMANDS:
            group = group_at(text, end)
            if group is not None:
                pieces.append(text_payload(group[0]))
                pos = group[2]
                continue
        if name in {" ", ",", ";", ":", "!", "quad", "qquad", "enspace", "thinspace", "medspace", "thickspace", "left", "right", "big", "Big", "bigg", "Bigg", "bigl", "bigr", "Bigl", "Bigr", "biggl", "biggr", "Biggl", "Biggr"}:
            pos = end
            continue
        pieces.append(text[pos:end])
        pos = end
    return re.sub(r"\s+|~", "", "".join(pieces))


def math_regions(text: str) -> Iterator[tuple[int, int, str]]:
    """Yield (start, end, body) for non-overlapping mathematical regions."""
    pos = 0
    while pos < len(text):
        start = pos
        closing = None
        if text.startswith("$$", pos):
            opening, closing = "$$", "$$"
        elif text[pos] == "$":
            opening, closing = "$", "$"
        elif text.startswith(r"\(", pos):
            opening, closing = r"\(", r"\)"
        elif text.startswith(r"\[", pos):
            opening, closing = r"\[", r"\]"
        elif text[pos] == "\\":
            name, _, end = command_at(text, pos)
            if name == "begin":
                group = group_at(text, end)
                if group and group[0] in MATH_ENVS:
                    stop = re.search(r"\\end\s*\{" + re.escape(group[0]) + r"\}", text[group[2]:])
                    if stop is None:
                        raise ValueError(f"unclosed math environment {group[0]}")
                    stop_start = group[2] + stop.start()
                    pos = group[2] + stop.end()
                    yield start, pos, text[group[2]:stop_start]
                    continue
            pos = end
            continue
        if closing is None:
            pos += 1
            continue
        pos += len(opening)
        body_start = pos
        brace_depth = 0
        while pos < len(text):
            # \text{...$x$...} (and the book's \gap{$...$}) contain nested
            # math islands.  Those dollars must not terminate the outer math
            # snippet before their enclosing TeX group has closed.
            if brace_depth == 0 and text.startswith(closing, pos):
                snippet = text[body_start:pos]
                pos += len(closing)
                yield start, pos, snippet
                break
            if text[pos] == "\\":
                _, _, pos = command_at(text, pos)
            else:
                if text[pos] == "{":
                    brace_depth += 1
                elif text[pos] == "}":
                    brace_depth -= 1
                    if brace_depth < 0:
                        raise ValueError(f"unbalanced math group near line {text.count(chr(10), 0, pos) + 1}")
                pos += 1
        else:
            raise ValueError(f"unclosed math delimiter near line {text.count(chr(10), 0, start) + 1}")


def math_snippets(text: str) -> Iterator[tuple[int, str]]:
    for start, _, body in math_regions(text):
        yield text.count("\n", 0, start) + 1, body


def global_label_issues(documents: list[Document]) -> tuple[Counter, Counter]:
    labels: Counter = Counter()
    refs: Counter = Counter()
    for document in documents:
        labels.update(document.stats["labels"])
        refs.update(target for (_, target), count in document.stats["references"].items() for _ in range(count))
    duplicates = Counter({target: count - 1 for target, count in labels.items() if count > 1})
    undefined = Counter({target: count for target, count in refs.items() if target not in labels and "#" not in target and "\\" not in target})
    return duplicates, undefined


def describe_counter(counter: Counter, limit: int) -> str:
    entries = sorted(counter.items(), key=lambda item: str(item[0]))
    shown = [f"{target!r}" + (f" (x{count})" if count != 1 else "") for target, count in entries[:limit]]
    if len(entries) > limit:
        shown.append(f"... {len(entries) - limit} more")
    return "; ".join(shown)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this script's parent repository)")
    parser.add_argument("--math", action="store_true", help="also flag normalized formula differences for manual review (exit 1 if any)")
    parser.add_argument("--max-details", type=int, default=12, help="maximum details per finding (default: 12)")
    args = parser.parse_args(argv)
    if args.max_details < 1:
        parser.error("--max-details must be positive")
    root = args.root.resolve()
    errors: list[str] = []
    try:
        english_main = Document.read(root / "00-main.tex")
        chinese_main = Document.read(root / "00-main-zh.tex")
        expected: Counter = Counter()
        for path, count in english_main.stats["inputs"].items():
            chapter = chapter_path(path)
            if chapter:
                expected[chapter] += count
        if not expected:
            raise ValueError("00-main.tex contains no active a/b/c/dNN chapter inputs")
        actual: Counter = Counter()
        for path, count in chinese_main.stats["inputs"].items():
            chapter = chapter_path(path)
            if chapter:
                actual[chapter] += count
        expected_zh = Counter({f"zh-CN/{path}": count for path, count in expected.items()})
        if expected_zh - actual:
            errors.append("Chinese entry point is missing chapter inputs: " + describe_counter(expected_zh - actual, args.max_details))
        if actual - expected_zh:
            errors.append("Chinese entry point has unexpected/English fallback chapter inputs: " + describe_counter(actual - expected_zh, args.max_details))

        english = [english_main]
        chinese = [chinese_main]
        pairs: list[tuple[str, Document, Document]] = []
        for path in expected:
            source = Document.read(root / path)
            english.extend([source] * expected[path])
            target_path = root / "zh-CN" / path
            if not target_path.is_file():
                errors.append(f"Missing Chinese chapter: zh-CN/{path}")
                continue
            target = Document.read(target_path)
            chinese.extend([target] * expected[path])
            pairs.append((path, source, target))
            for metric in ("labels", "references", "citations", "environments", "graphics", "sections"):
                missing = source.stats[metric] - target.stats[metric]
                added = target.stats[metric] - source.stats[metric]
                if missing:
                    errors.append(f"{path}: missing/changed {metric}: {describe_counter(missing, args.max_details)}")
                if added:
                    errors.append(f"{path}: added/changed {metric}: {describe_counter(added, args.max_details)}")
            for nested in target.stats["inputs"]:
                if chapter_path(nested) and not tex_path(nested).startswith("zh-CN/"):
                    errors.append(f"zh-CN/{path}: possible English fallback via input {nested!r}")

        baseline_duplicates, baseline_undefined = global_label_issues(english)
        for title, values in (("duplicate labels", baseline_duplicates), ("undefined reference keys", baseline_undefined)):
            if values:
                print(f"BASELINE: English edition already has {len(values)} {title}: {describe_counter(values, args.max_details)}")
            else:
                print(f"BASELINE: English edition has no {title}.")
        if len(pairs) == len(expected):
            target_duplicates, target_undefined = global_label_issues(chinese)
            for title, values in (("duplicate labels", target_duplicates - baseline_duplicates), ("undefined references", target_undefined - baseline_undefined)):
                if values:
                    errors.append(f"New {title} compared with English baseline: {describe_counter(values, args.max_details)}")

        math_count = 0
        if args.math:
            for path, source, target in pairs:
                indexes = []
                for document in (source, target):
                    index: dict[str, list[tuple[int, str]]] = defaultdict(list)
                    for line, snippet in math_snippets(document.active):
                        normalized = normalize_math(snippet)
                        if normalized:  # Empty $ $ is spacing, not a formula.
                            index[normalized].append((line, snippet))
                    indexes.append(index)
                source_counts = Counter({value: len(locations) for value, locations in indexes[0].items()})
                target_counts = Counter({value: len(locations) for value, locations in indexes[1].items()})
                math_count += sum(source_counts.values())
                for title, diff, index in (("missing/changed", source_counts - target_counts, indexes[0]), ("added/changed", target_counts - source_counts, indexes[1])):
                    if diff:
                        entries = []
                        for value, count in list(diff.items())[:args.max_details]:
                            line, snippet = index[value][0]
                            preview = " ".join(snippet.split())[:180]
                            entries.append(f"line {line}: {preview!r} (x{count})")
                        if len(diff) > args.max_details:
                            entries.append(f"... {len(diff) - args.max_details} more distinct snippets")
                        errors.append(f"MATH REVIEW {path}: {sum(diff.values())} {title} snippets: " + "; ".join(entries))
        for error in errors:
            print("ERROR: " + error)
        if errors:
            print(f"FAIL: {len(errors)} findings; checked {len(pairs)}/{len(expected)} Chinese chapters.")
            return 1
        print(f"PASS: all {len(pairs)} Chinese chapters are explicitly included; labels, references, citations, environments, graphics and section counts match.")
        print("PASS: no new duplicate labels or undefined references relative to the English baseline.")
        if args.math:
            print(f"PASS: {math_count} normalized mathematical snippets match, allowing prose translation and snippet reordering.")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
