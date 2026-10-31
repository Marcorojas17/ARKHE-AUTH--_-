#!/data/data/com.termux/files/usr/bin/bash
# Verifica drift contra la última entrada de .audit-chain.log
set -euo pipefail
CHAIN="${1:-.audit-chain.log}"
[[ -f "$CHAIN" ]] || { echo "Sin cadena de auditoría. Genera una primero." >&2; exit 1; }
CURRENT=$(find . -type f -not -path './.git/*' -not -path './node_modules/*' \
  -not -path './.next/*' -not -path './.audit-chain.log*' -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1)
LAST=$(tail -n1 "$CHAIN" | awk '{print $2}')
[[ "$CURRENT" == "$LAST" ]] && echo "OK $CURRENT" \
  || { echo "DRIFT: $CURRENT != $LAST"; exit 2; }
