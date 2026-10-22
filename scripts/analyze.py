"""Junta cada copia con la sesión de su agente y vuelve a correr su suite.

analyze.py [DIR_DE_SESIONES]   (por omisión, work/runs)

Cada sesión es un tNN.jsonl: la salida de `claude -p --output-format stream-json --verbose`
o el transcript de un subagente de Claude Code. Escribe work/results.json.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"


def session(path, tid):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    tools, outside, usage = 0, [], {}
    seconds = None
    for r in rows:
        if r.get("type") == "result":
            seconds = r.get("duration_ms", 0) / 1000
        msg = r.get("message")
        if r.get("type") != "assistant" or not isinstance(msg, dict):
            continue
        if msg.get("usage"):
            # El último registro de cada mensaje trae su uso final.
            usage[msg.get("id")] = msg["usage"]
        for b in msg.get("content") or []:
            if b.get("type") != "tool_use":
                continue
            tools += 1
            for p in re.findall(r"(/[\w\-./]+)", json.dumps(b.get("input"))):
                if f"/trials/{tid}" in p or f"/t/{tid}" in p:
                    continue
                if "/trials/" in p or "/repos/" in p or "site-packages" in p:
                    outside.append(p)
    if seconds is None:
        stamps = [datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
                  for r in rows if r.get("timestamp")]
        seconds = (max(stamps) - min(stamps)).total_seconds()
    # Contexto de entrada de cada turno: lo nuevo más lo que se reenvía desde la caché.
    ctx = [u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
           + u.get("cache_creation_input_tokens", 0) for u in usage.values()]
    return dict(tools=tools, turns=len(ctx), ctx_peak=max(ctx), seconds=seconds,
                input_tokens_total=sum(ctx), context_start=ctx[0], context_growth=max(ctx) - ctx[0],
                outside=sorted(set(outside)))


def verdict(tid, t):
    d = WORK / "trials" / tid
    r = subprocess.run([".venv/bin/python", "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider", "-n", "8"],
                       cwd=d, capture_output=True, text=True)
    numstat = [l.split("\t") for l in
               subprocess.run(["git", "diff", "--numstat"], cwd=d, capture_output=True, text=True).stdout.splitlines()]
    files = [n[2] for n in numstat]
    line = (d / t["file"]).read_text().splitlines()[t["line"] - 1]
    restored = line[t["col"]:t["col"] + len(t["old"])] == t["old"]
    return dict(passed=r.returncode == 0, files=files,
                diff_lines=sum(int(n[0]) + int(n[1]) for n in numstat),
                exact_revert=restored and files == [t["file"]],
                tests_touched=any(f.startswith("tests/") for f in files))


def main():
    runs = Path(sys.argv[1]) if len(sys.argv) > 1 else WORK / "runs"
    out = []
    for t in sorted(json.load(open(WORK / "trials.json")), key=lambda t: t["trial"]):
        tid = t["trial"]
        path = runs / f"{tid}.jsonl"
        if not path.exists():
            continue
        lines = len((WORK / "repos" / t["repo"] / t["file"]).read_text().splitlines())
        out.append(dict(trial=tid, repo=t["repo"], file=t["file"], score=t["score"],
                        group="green" if t["score"] >= 85 else "red", kind=t["kind"],
                        failing=t["failing"], file_lines=lines,
                        **session(path, tid), **verdict(tid, t)))
    json.dump(out, open(WORK / "results.json", "w"), indent=1)
    print(f"{len(out)} intentos en {WORK / 'results.json'}")


if __name__ == "__main__":
    main()
