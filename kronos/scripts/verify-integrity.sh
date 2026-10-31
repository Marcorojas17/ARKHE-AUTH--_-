#!/data/data/com.termux/files/usr/bin/bash
# Verifica drift contra la ultima entrada de .audit-chain.log
# Esquema #19+: usa "git ls-files" -> hash reproducible desde cualquier clon
set -euo pipefail

CHAIN="${1:-.audit-chain.log}"
[[ -f "$CHAIN" ]] || { echo "Sin cadena de auditoria. Genera una primero." >&2; exit 1; }

# Solo archivos tracked por git. Excluye .audit-chain.log* (no auto-referencia).
# git ls-files produce paths relativos sin "./" -> determinista cross-clone.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: no es un repositorio git" >&2
  exit 1
fi

CURRENT=$(git ls-files -z | grep -zv -E "^\\.audit-chain\\.log" | sort -z | xargs -0 sha256sum | sha256sum | cut -d" " -f1)

LAST=$(tail -n1 "$CHAIN" | awk "{print \$2}")
[[ "$CURRENT" == "$LAST" ]] && echo "OK $CURRENT" \
  || { echo "DRIFT: $CURRENT != $LAST"; exit 2; }
