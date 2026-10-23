"""Junta cada copia de sc-cli con la sesión de su agente y vuelve a correr su suite.

analyze_rs.py DIR_DE_SESIONES   (un rNN.jsonl por copia; escribe data/results-sc-cli.json)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze import session  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"


def verdict(t):
    d = WORK / "trials-rs" / t["trial"]
    r = subprocess.run(["cargo", "test", "--no-fail-fast", "-q"], cwd=d, capture_output=True, text=True)
    numstat = [l.split("\t") for l in
               subprocess.run(["git", "diff", "--numstat"], cwd=d, capture_output=True, text=True).stdout.splitlines()]
    files = [n[2] for n in numstat]
    s = t["site"]
    src = (d / t["file"]).read_bytes()
    a = s["span"]["start"]["byte"]
    restored = src[a:a + len(s["original"].encode())].decode(errors="replace") == s["original"]
    return dict(passed=r.returncode == 0, files=files,
                diff_lines=sum(int(n[0]) + int(n[1]) for n in numstat),
                exact_revert=restored and files == [t["file"]],
                tests_touched=any("tests" in f for f in files))


def main():
    runs = Path(sys.argv[1])
    out = []
    for t in sorted(json.load(open(WORK / "trials-rs.json")), key=lambda t: t["trial"]):
        path = runs / f"{t['trial']}.jsonl"
        if not path.exists():
            continue
        lines = len((WORK / "sc-cli" / t["file"]).read_text().splitlines())
        s = session(path, t["trial"])
        s["outside"] = [p for p in s["outside"] if f"/trials-rs/{t['trial']}" not in p]
        out.append(dict(trial=t["trial"], repo="sc-cli", file=t["file"], score=t["score"],
                        group="green" if t["score"] >= 85 else "red", kind=t["spell"],
                        failing=t["failing"], file_lines=lines, **s, **verdict(t)))
        print(out[-1]["trial"], out[-1]["group"], out[-1]["passed"], out[-1]["tools"], file=sys.stderr)
    json.dump(out, open(ROOT / "data" / "results-sc-cli.json", "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
