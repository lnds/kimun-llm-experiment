#!/usr/bin/env bash
# Mapas (km map --color-by llm) y notas (km score) de cada repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/work/maps"
mkdir -p "$OUT"
cd "$ROOT/work/repos"

for name in */; do
  name="${name%/}"
  excl=()
  case "$name" in
    black) excl=(--exclude-dir profiling) ;;  # datos de prueba del perfilador
    redis) excl=(--exclude-dir deps) ;;       # código de terceros
  esac
  km map "$name" --color-by llm "${excl[@]}" --html "$OUT/$name-llm.html" > /dev/null
  km map "$name" --color-by llm "${excl[@]}" --format json > "$OUT/$name-llm.json"
  km score "$name" "${excl[@]}" --format json > "$OUT/$name-score.json"
  echo "$name"
done
