"""Corre la prueba escondida de un mutante sobre una copia de un proyecto.

hidden.py DIR WEKUFE [--mutate]

Copia DIR, agrega al final del archivo del mutante la prueba de
data/hidden/WEKUFE.rs como un módulo `hidden_check` y corre solo esa prueba.
Con --mutate aplica antes la mutación: sirve para comprobar, sobre el
proyecto original, que la prueba pasa sin el mutante y falla con él.
Sale con 0 si la prueba pasa.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from setup_trials_rs import apply  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MUTATIONS = ROOT / "data" / "mutations" / "sc-cli-no-tests.jsonl"
HIDDEN = ROOT / "data" / "hidden"
CHECKS = ROOT / "work" / "checks"


def mutation(wekufe):
    for line in open(MUTATIONS):
        m = json.loads(line)
        if m["wekufe"] == wekufe:
            return m
    raise SystemExit(f"no mutation {wekufe}")


def check(src, wekufe, mutate=False, quiet=False):
    """Si la prueba escondida pasa sobre una copia de `src`, y su salida."""
    m = mutation(wekufe)
    CHECKS.mkdir(parents=True, exist_ok=True)
    dst = CHECKS / f"{Path(src).name}-{wekufe}{'-m' if mutate else ''}"
    if dst.exists():
        shutil.rmtree(dst)
    subprocess.run(["cp", "-Rc", str(src), str(dst)], check=True)
    f = dst / m["file"]
    text = f.read_text()
    if mutate:
        text = apply(text, m["site"])
    test = HIDDEN / f"{wekufe}.rs"
    text += f'\n#[cfg(test)]\n#[path = "{test}"]\nmod hidden_check;\n'
    f.write_text(text)
    home = dst / ".home"
    home.mkdir(exist_ok=True)
    r = subprocess.run(
        ["cargo", "test", "-q", "hidden_check", "--", "--test-threads=1"],
        cwd=dst, capture_output=True, text=True,
        env={**os.environ, "HOME": str(home)},
    )
    out = r.stdout + r.stderr
    # Al menos una prueba corrió: un filtro que no calza da verde sin probar nada.
    ran = sum(int(n) for n in re.findall(r"(\d+) passed", out)) > 0
    shutil.rmtree(dst)
    if not quiet:
        print(out[-3000:])
    return r.returncode == 0 and ran, out


def main():
    src, wekufe = sys.argv[1], sys.argv[2]
    ok, _ = check(src, wekufe, mutate="--mutate" in sys.argv)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
