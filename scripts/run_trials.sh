#!/usr/bin/env bash
# Un agente por copia, con claude -p. Guarda cada sesión en work/runs/tNN.jsonl.
#
# Los agentes corren sin pedir permisos (--dangerously-skip-permissions): hazlo solo
# en una máquina o contenedor desechable.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODEL="${MODEL:-sonnet}"
JOBS="${JOBS:-4}"
mkdir -p "$ROOT/work/runs"

trial() {
  local dir=$1 tid
  tid=$(basename "$dir")
  sed "s#{dir}#$dir#g" "$ROOT/prompt.md" \
    | (cd "$dir" && claude -p --model "$MODEL" --output-format stream-json --verbose \
         --dangerously-skip-permissions --no-session-persistence) \
    > "$ROOT/work/runs/$tid.jsonl"
  echo "$tid"
}
export -f trial
export ROOT MODEL

ls -d "$ROOT"/work/trials/t* | xargs -P "$JOBS" -I{} bash -c 'trial {}'
