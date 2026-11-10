"""Arma una copia aislada de sc-cli por mutante que la suite no detecta.

setup_trials_nt.py [RONDA]   (por omisión nt: work/trials-nt y work/trials-nt.json)

Cada copia lleva la fuente mutada, un historial de git nuevo y un HOME vacío
(`.home`, fuera de git), para que las pruebas no lean una configuración real.
El agente recibe el reporte del síntoma de data/reports; la prueba escondida
de data/hidden queda fuera de la copia.
"""

import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from setup_trials import scores  # noqa: E402
from setup_trials_rs import apply  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"
DATA = ROOT / "data"
REPO = "sc-cli"


def main():
    rnd = sys.argv[1] if len(sys.argv) > 1 else "nt"
    score = scores(REPO)
    muts = [json.loads(line) for line in open(DATA / "mutations" / "sc-cli-no-tests.jsonl")]
    for m in muts:
        m.update(repo=REPO, score=score[m["file"]],
                 report=(DATA / "reports" / f"{m['wekufe']}.md").read_text().strip())
    # El orden de las copias no delata el grupo.
    random.Random(42).shuffle(muts)
    root = WORK / f"trials-{rnd}"
    root.mkdir(parents=True, exist_ok=True)
    for i, m in enumerate(muts, 1):
        m["trial"] = f"n{i:02d}"
        dst = root / m["trial"]
        if dst.exists():
            shutil.rmtree(dst)
        # Clon de APFS: el target compilado viene gratis y solo se recompila el crate.
        subprocess.run(["cp", "-Rc", str(WORK / REPO), str(dst)], check=True)
        shutil.rmtree(dst / ".git")
        f = dst / m["file"]
        f.write_text(apply(f.read_text(), m["site"]))
        (dst / ".home").mkdir()

        def run(*cmd):
            subprocess.run(cmd, cwd=dst, check=True, capture_output=True)

        # Un historial nuevo: git diff no muestra la mutación.
        run("git", "init", "-q")
        (dst / ".git" / "info" / "exclude").write_text(".home/\n")
        run("git", "add", "-A")
        run("git", "-c", "user.name=x", "-c", "user.email=x@x", "-c", "commit.gpgsign=false",
            "commit", "-qm", "import")
        print(m["trial"], m["file"], m["score"], file=sys.stderr)
    json.dump(muts, open(WORK / f"trials-{rnd}.json", "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
