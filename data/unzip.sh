#!/usr/bin/env sh
# Rebuild data/csv/ from the zip parts in data/archive/.
# Usage (from the repo root): sh data/unzip.sh
set -e
cd "$(dirname "$0")"

cat archive/csv.zip.part* > csv.zip
if command -v unzip >/dev/null 2>&1; then
    unzip -o -q csv.zip
else
    python -m zipfile -e csv.zip .
fi
rm csv.zip
echo "Done: data/csv/"
