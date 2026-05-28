#!/usr/bin/env python3
"""Build markdown comparison tables from eval sample directories.

Usage: summarize-evals.py DIR [DIR ...]

Each DIR is a top-level outputs directory containing numbered sample
subdirectories, each with structural-eval*.md and tech-eval.md files.
"""

import os
import re
import sys

WORD_COUNT_RE = re.compile(r"\| Word count \| (\d+) \|")
TOTAL_RE = re.compile(r"\| \*\*Total[^|]*\| \*\*(\d+)\*\* \|")
SCORE_RE = re.compile(r"\| \*\*Score\*\* \| \*\*(\d+)%\*\* \|")


def first_match(path, regex):
    try:
        with open(path) as f:
            text = f.read()
    except FileNotFoundError:
        return None
    m = regex.search(text)
    return int(m.group(1)) if m else None


def last_match(path, regex):
    try:
        with open(path) as f:
            text = f.read()
    except FileNotFoundError:
        return None
    matches = regex.findall(text)
    return int(matches[-1]) if matches else None


def struct_eval_files(sample_dir):
    """structural-eval.md first, then -2, -3, ... in numeric order."""
    base = os.path.join(sample_dir, "structural-eval.md")
    files = [base] if os.path.exists(base) else []
    numbered = []
    for name in os.listdir(sample_dir):
        m = re.fullmatch(r"structural-eval-(\d+)\.md", name)
        if m:
            numbered.append((int(m.group(1)), os.path.join(sample_dir, name)))
    files += [p for _, p in sorted(numbered)]
    return files


def collect_sample(sample_dir):
    word_count = first_match(
        os.path.join(sample_dir, "structural-eval.md"), WORD_COUNT_RE
    )
    struct_runs = [
        v for v in (last_match(p, TOTAL_RE) for p in struct_eval_files(sample_dir))
        if v is not None
    ]
    tech = first_match(os.path.join(sample_dir, "tech-eval.md"), SCORE_RE)
    return {
        "name": os.path.basename(sample_dir.rstrip("/")),
        "word_count": word_count,
        "struct_runs": struct_runs,
        "tech": tech,
    }


def collect_dir(top_dir):
    samples = []
    for entry in sorted(os.listdir(top_dir)):
        sample_dir = os.path.join(top_dir, entry)
        if os.path.isdir(sample_dir):
            samples.append(collect_sample(sample_dir))
    return samples


def display_names(top_dirs):
    bases = [os.path.basename(d.rstrip("/")) for d in top_dirs]
    if len(bases) < 2:
        return bases
    prefix = os.path.commonprefix(bases)
    # Trim back to the last separator so segments aren't cut mid-token.
    cut = max(prefix.rfind("-"), prefix.rfind("/"))
    prefix = prefix[: cut + 1] if cut >= 0 else ""
    return [b[len(prefix):] for b in bases]


def fmt(value, suffix="", decimals=None):
    if value is None:
        return ""
    if decimals is None:
        return f"{value}{suffix}"
    return f"{value:.{decimals}f}{suffix}"


def stats(values):
    if not values:
        return None, None, None
    return sum(values) / len(values), min(values), max(values)


def render_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |"]
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def main(argv):
    if len(argv) < 2:
        sys.exit(f"Usage: {argv[0]} DIR [DIR ...]")

    top_dirs = argv[1:]
    names = display_names(top_dirs)

    groups = []
    for top_dir, name in zip(top_dirs, names):
        samples = collect_dir(top_dir)
        all_runs = [v for s in samples for v in s["struct_runs"]]
        techs = [s["tech"] for s in samples if s["tech"] is not None]
        wcs = [s["word_count"] for s in samples if s["word_count"] is not None]
        groups.append({
            "name": name,
            "samples": samples,
            "struct": stats(all_runs),
            "tech": stats(techs),
            "wc": stats(wcs),
        })

    blocks = []

    # Table 1: by eval type
    rows = []
    for g in groups:
        s_avg, s_min, s_max = g["struct"]
        t_avg, t_min, t_max = g["tech"]
        w_avg, w_min, w_max = g["wc"]
        rows.append([
            g["name"],
            fmt(s_avg, decimals=1), fmt(s_min), fmt(s_max),
            fmt(t_avg, "%", decimals=1), fmt(t_min, "%"), fmt(t_max, "%"),
            fmt(round(w_avg) if w_avg is not None else None), fmt(w_min), fmt(w_max),
        ])
    blocks.append("## By Eval Type\n\n" + render_table(
        ["Directory", "Struct avg", "Struct min", "Struct max",
         "Tech avg", "Tech min", "Tech max", "WC avg", "WC min", "WC max"],
        rows,
    ))

    # Table 2: by aggregation type
    rows = []
    for g in groups:
        s_avg, s_min, s_max = g["struct"]
        t_avg, t_min, t_max = g["tech"]
        w_avg, w_min, w_max = g["wc"]
        rows.append([
            g["name"],
            fmt(s_avg, decimals=1), fmt(t_avg, "%", decimals=1),
            fmt(round(w_avg) if w_avg is not None else None),
            fmt(s_min), fmt(t_min, "%"), fmt(w_min),
            fmt(s_max), fmt(t_max, "%"), fmt(w_max),
        ])
    blocks.append("## By Aggregation Type\n\n" + render_table(
        ["Directory", "Struct avg", "Tech avg", "WC avg",
         "Struct min", "Tech min", "WC min",
         "Struct max", "Tech max", "WC max"],
        rows,
    ))

    # Table 3: detailed breakdown
    rows = []
    for g in groups:
        for s in g["samples"]:
            rows.append([
                g["name"],
                s["name"],
                fmt(s["word_count"]),
                ", ".join(str(v) for v in s["struct_runs"]),
                fmt(s["tech"], "%"),
            ])
    blocks.append("## Detailed Breakdown\n\n" + render_table(
        ["Directory", "Sample", "Word Count", "Struct (runs)", "Tech"],
        rows,
    ))

    print("\n\n".join(blocks))


if __name__ == "__main__":
    main(sys.argv)
