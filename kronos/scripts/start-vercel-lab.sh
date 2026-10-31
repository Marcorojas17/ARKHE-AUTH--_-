#!/data/data/com.termux/files/usr/bin/bash
# SOLO correr con autorización escrita de Vercel. Ver research/README.md
[[ -f .scope-authorized ]] || {
  echo "AUTORIZACIÓN ESCRITA REQUERIDA (crear .scope-authorized). Abortando." >&2
  exit 1
}
echo "Lab autorizado. Levantando entorno..."
