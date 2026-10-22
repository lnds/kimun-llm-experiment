"""Find one-token mutations in a Python file that a repo's test suite detects."""

import ast
import json
import random
import re
import subprocess
import sys
from pathlib import Path

CMP_SWAP = {"==": "!=", "!=": "==", "<": ">=", ">=": "<", ">": "<=", "<=": ">",
            "is": "is not", "is not": "is", "in": "not in", "not in": "in"}


def sites(src):
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    out = []

    def between(a, b):
        if a.end_lineno != b.lineno:
            return None
        return (a.end_lineno, a.end_col_offset, b.col_offset)

    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not fn:
                continue
            span = None
            if isinstance(node, ast.Compare) and len(node.ops) == 1:
                span = between(node.left, node.comparators[0])
                kind = "cmp"
            elif isinstance(node, ast.BoolOp) and len(node.values) == 2:
                span = between(node.values[0], node.values[1])
                kind = "bool"
            elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
                span = between(node.left, node.right)
                kind = "arith"
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                if node.lineno == node.operand.lineno:
                    span = (node.lineno, node.col_offset, node.operand.col_offset)
                kind = "not"
            elif isinstance(node, ast.Return) and isinstance(node.value, ast.Constant) \
                    and isinstance(node.value.value, bool):
                v = node.value
                span = (v.lineno, v.col_offset, v.end_col_offset)
                kind = "ret"
            elif isinstance(node, ast.Constant) and type(node.value) is int \
                    and 0 <= node.value <= 10 and node.lineno == node.end_lineno:
                span = (node.lineno, node.col_offset, node.end_col_offset)
                kind = "int"
            if not span:
                continue
            ln, a, b = span
            line = lines[ln - 1]
            seg = line[a:b]
            text = seg.strip()
            if kind == "cmp":
                text = re.sub(r"\s+", " ", text.strip("() "))
                if text not in CMP_SWAP:
                    continue
                new = CMP_SWAP[text]
            elif kind == "bool":
                text = text.strip("() ")
                if text not in ("and", "or"):
                    continue
                new = "or" if text == "and" else "and"
            elif kind == "arith":
                text = text.strip("() ")
                if text not in ("+", "-"):
                    continue
                new = "-" if text == "+" else "+"
            elif kind == "not":
                if not seg.startswith("not"):
                    continue
                text, new = seg, ""
            elif kind == "ret":
                new = "False" if text == "True" else "True"
            else:
                new = str(int(text, 0) + 1) if text.isdigit() else None
                if new is None:
                    continue
            start = a + seg.index(text)
            out.append({"line": ln, "col": start, "old": text, "new": new,
                        "kind": kind, "function": fn.name})
    return out


def apply(src, m):
    lines = src.splitlines(keepends=True)
    line = lines[m["line"] - 1]
    c = m["col"]
    assert line[c:c + len(m["old"])] == m["old"]
    lines[m["line"] - 1] = line[:c] + m["new"] + line[c + len(m["old"]):]
    return "".join(lines)


def failures(repo, extra):
    cmd = [f"{repo}/.venv/bin/python", "-m", "pytest", "tests", "-q",
           "-p", "no:cacheprovider", "--maxfail=40", *extra]
    try:
        r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=400)
    except subprocess.TimeoutExpired:
        return None
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    f = re.search(r"(\d+) failed", tail)
    e = re.search(r"(\d+) error", tail)
    return (int(f.group(1)) if f else 0) + (int(e.group(1)) if e else 0)


def main():
    """mutate.py REPO FILE SEED [pytest args]: prints the first mutation that fails 1 to 15 tests."""
    repo, rel, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    extra = sys.argv[4:]
    path = Path(repo) / rel
    src = path.read_text()
    cands = sites(src)
    random.Random(seed).shuffle(cands)
    try:
        for m in cands[:25]:
            path.write_text(apply(src, m))
            n = failures(repo, extra)
            print(f"  try {rel}:{m['line']} {m['old']!r}->{m['new']!r} fails={n}", file=sys.stderr)
            if n and 1 <= n <= 15:
                m.update(file=rel, failing=n, candidates=len(cands))
                print(json.dumps(m))
                return
    finally:
        path.write_text(src)
    print(json.dumps({"file": rel, "error": "none found", "candidates": len(cands)}))


if __name__ == "__main__":
    main()
