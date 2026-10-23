"""Cuántas pruebas hace fallar cada mutante muerto de kalku, para quedarse con los de 1 a 15.

failing_rs.py COPIA killed.jsonl SHARD/N   imprime cada mutante con su `failing`
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from setup_trials_rs import apply  # noqa: E402


def failing(repo):
    r = subprocess.run(["cargo", "test", "--no-fail-fast", "-q"], cwd=repo,
                       capture_output=True, text=True, timeout=600)
    out = r.stdout + r.stderr
    if "could not compile" in out:
        return None
    return len(set(re.findall(r"^    (\S+)$", out, re.M)))


def main():
    repo, src = Path(sys.argv[1]), sys.argv[2]
    shard, n = map(int, sys.argv[3].split("/"))
    for i, line in enumerate(open(src)):
        if i % n != shard:
            continue
        m = json.loads(line)
        f = repo / m["file"]
        orig = f.read_text()
        try:
            f.write_text(apply(orig, m["site"]))
            m["failing"] = failing(repo)
        finally:
            f.write_text(orig)
        print(json.dumps(m), flush=True)


if __name__ == "__main__":
    main()
