#!/usr/bin/env bash
# Busca una mutación por archivo: verdes (nota >= 85) y rojos (< 65) de click, flask y black.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPOS="$ROOT/work/repos"
OUT="$ROOT/work/mutations"
SEED=7
mkdir -p "$OUT"

run() {
  local repo=$1 extra=$2; shift 2
  for f in "$@"; do
    python3 "$ROOT/scripts/mutate.py" "$REPOS/$repo" "$f" "$SEED" $extra
  done > "$OUT/$repo.jsonl" 2> "$OUT/$repo.log"
}

run click "" \
  src/click/_compat.py src/click/formatting.py src/click/testing.py src/click/utils.py \
  src/click/core.py src/click/_textwrap.py src/click/_termui_impl.py &
run flask "" \
  src/flask/ctx.py src/flask/json/tag.py src/flask/sansio/app.py src/flask/templating.py \
  src/flask/helpers.py src/flask/config.py src/flask/sessions.py \
  src/flask/app.py src/flask/cli.py src/flask/sansio/blueprints.py &
run black "-n8" \
  src/black/mode.py src/black/cache.py \
  src/black/linegen.py src/black/lines.py src/black/trans.py src/black/nodes.py \
  src/black/ranges.py src/black/brackets.py &
wait
cat "$OUT"/*.jsonl
