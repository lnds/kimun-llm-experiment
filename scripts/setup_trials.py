"""Arma una copia aislada por mutación: fuente mutada, historial de git nuevo y entorno propio.

setup_trials.py [DIR_DE_MUTACIONES]   (por omisión, data/mutations: las del experimento publicado)
"""

import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mutate import apply  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"
UV = os.environ.get("UV", "uv")
EXTRAS = {"click": ".", "flask": ".[async]", "black": ".[d,jupyter]"}


def scores(repo):
    """Nota de cada archivo, leída del mapa de km."""
    nodes = json.load(open(WORK / "maps" / f"{repo}-llm.json"))["nodes"]
    return {n["path"]: float(n["label"].split()[1])
            for n in nodes if (n.get("label") or "").startswith("score")}


def mutations(src):
    """Las mutaciones de cada repo, con la nota de su archivo, en el orden de las copias."""
    muts = []
    for repo in EXTRAS:
        score = scores(repo)
        for line in open(src / f"{repo}.jsonl"):
            m = json.loads(line)
            if "error" not in m:
                m.update(repo=repo, score=score[m["file"]])
                muts.append(m)
    # El orden de las copias no delata el grupo.
    random.Random(42).shuffle(muts)
    for i, m in enumerate(muts, 1):
        m["trial"] = f"t{i:02d}"
    return muts


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/mutations"
    muts = mutations(src)
    root = WORK / "trials"
    root.mkdir(parents=True, exist_ok=True)
    for m in muts:
        dst = root / m["trial"]
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(WORK / "repos" / m["repo"], dst,
                        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache"))
        f = dst / m["file"]
        f.write_text(apply(f.read_text(), m))

        def run(*cmd):
            subprocess.run(cmd, cwd=dst, check=True, capture_output=True)

        # Un historial nuevo: git diff no muestra la mutación.
        run("git", "init", "-q")
        (dst / ".git/info/exclude").write_text(".venv/\n")
        run("git", "add", "-A")
        run("git", "-c", "user.name=x", "-c", "user.email=x@x", "commit", "-qm", "import")
        # Un entorno propio: uno editable compartido importaría el código sin mutar.
        run(UV, "venv", "-q", "-p", "3.13", ".venv")
        run(UV, "pip", "install", "-q", "-p", ".venv/bin/python", "-e", EXTRAS[m["repo"]],
            "pytest", "pytest-xdist")
        print(m["trial"], m["repo"], m["file"], m["score"], file=sys.stderr)
    json.dump(muts, open(WORK / "trials.json", "w"), indent=1)


if __name__ == "__main__":
    main()
