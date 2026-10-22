"""Resume un results.json: verdes contra rojos y la correlación entre nota y esfuerzo.

summary.py [RESULTS]   (por omisión, data/results.json: el experimento publicado)
"""

import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rk = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[order[k]] = (i + j) / 2
        i = j + 1
    return rk


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/results.json"
    rows = json.load(open(path))
    print(f"{'trial':5} {'grupo':5} {'nota':>5} {'líneas':>6}  {'archivo':32} {'herr':>4} {'seg':>5}  suite")
    for r in rows:
        print(f"{r['trial']:5} {r['group']:5} {r['score']:5.1f} {r['file_lines']:6}  {r['file']:32} "
              f"{r['tools']:4} {r['seconds']:5.0f}  {'pasa' if r['passed'] else 'FALLA'}")
    print()
    for g in ("green", "red"):
        x = [r for r in rows if r["group"] == g]
        print(f"{g:5} n={len(x):2}  suite pasa {sum(r['passed'] for r in x)}/{len(x)}  "
              f"herramientas mediana {st.median(r['tools'] for r in x)}  "
              f"segundos mediana {st.median(r['seconds'] for r in x):.0f}  "
              f"líneas mediana {st.median(r['file_lines'] for r in x)}")
    scores = [r["score"] for r in rows]
    print(f"\nSpearman nota ~ herramientas: {spearman(scores, [r['tools'] for r in rows]):.2f}")


if __name__ == "__main__":
    main()
