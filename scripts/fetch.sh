#!/usr/bin/env bash
# Clona cada repo de repos.txt en el commit medido y crea el entorno de los que tienen extras.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$ROOT/work/repos"
UV="${UV:-uv}"
mkdir -p "$WORK"

grep -v '^#' "$ROOT/repos.txt" | while read -r name url sha extras; do
  [ -z "$name" ] && continue
  dir="$WORK/$name"
  if [ ! -d "$dir/.git" ]; then
    git init -q "$dir"
    git -C "$dir" remote add origin "$url"
  fi
  git -C "$dir" fetch -q --depth 1 origin "$sha"
  git -C "$dir" checkout -q FETCH_HEAD
  if [ "$extras" != "-" ]; then
    (cd "$dir" && "$UV" venv -q -p 3.13 .venv && "$UV" pip install -q -p .venv/bin/python -e "$extras" pytest pytest-xdist)
  fi
  echo "$name $(git -C "$dir" rev-parse --short HEAD)"
done
