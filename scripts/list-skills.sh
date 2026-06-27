#!/usr/bin/env bash
set -euo pipefail

# Lists all skills in the repository with their names and descriptions.

REPO="$(cd "$(dirname "$0")/.." && pwd)"

echo "altr Skills"
echo "==========="
echo ""

while IFS= read -r -d '' skill_md; do
  name="$(basename "$(dirname "$skill_md")")"
  desc="$(grep -m1 '^description:' "$skill_md" 2>/dev/null | sed 's/^description: //' | cut -c1-80)"
  if [ -n "$desc" ]; then
    printf "  %-35s %s\n" "/$name" "$desc"
  else
    printf "  %-35s\n" "/$name"
  fi
done < <(find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -not -path '*/deprecated/*' -print0 | sort -z)
