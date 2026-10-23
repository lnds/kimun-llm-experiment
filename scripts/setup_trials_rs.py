"""Arma una copia aislada de sc-cli por mutación: fuente mutada, historial de git nuevo y target propio.

setup_trials_rs.py MUTACIONES.jsonl   (un sitio de kalku por línea, con su `file`)
"""

import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from setup_trials import scores  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"
REPO = "sc-cli"


def apply(src, site):
    """El código con el reemplazo de un sitio de kalku, por sus bytes."""
    b = src.encode()
    a, z = site["span"]["start"]["byte"], site["span"]["end"]["byte"]
    assert b[a:z].decode() == site["original"], site
    return (b[:a] + site["replacement"].encode() + b[z:]).decode()


def main():
    score = scores(REPO)
    muts = [json.loads(line) for line in open(sys.argv[1]) if line.strip()]
    for m in muts:
        m.update(repo=REPO, score=score[m["file"]])
    # El orden de las copias no delata el grupo.
    random.Random(42).shuffle(muts)
    root = WORK / "trials-rs"
    root.mkdir(parents=True, exist_ok=True)
    for i, m in enumerate(muts, 1):
        m["trial"] = f"r{i:02d}"
        dst = root / m["trial"]
        if dst.exists():
            shutil.rmtree(dst)
        # Clon de APFS: el target compilado viene gratis y solo se recompila el crate.
        subprocess.run(["cp", "-Rc", str(WORK / REPO), str(dst)], check=True)
        shutil.rmtree(dst / ".git")
        f = dst / m["file"]
        f.write_text(apply(f.read_text(), m["site"]))

        def run(*cmd):
            subprocess.run(cmd, cwd=dst, check=True, capture_output=True)

        # Un historial nuevo: git diff no muestra la mutación.
        run("git", "init", "-q")
        run("git", "add", "-A")
        run("git", "-c", "user.name=x", "-c", "user.email=x@x", "-c", "commit.gpgsign=false", "commit", "-qm", "import")
        print(m["trial"], m["file"], m["score"], file=sys.stderr)
    json.dump(muts, open(WORK / "trials-rs.json", "w"), indent=1)


if __name__ == "__main__":
    main()
