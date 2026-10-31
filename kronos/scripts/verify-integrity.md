# verify-integrity.sh — notas

## Reproducibilidad

El script usa `find .` para descubrir archivos. Incluye gitignored files
(`.kronos-chain/`, `.vercel/`, `.env`). Localmente produce un hash
reproducible solo si esos directorios no existen o estan vacios.

En CI (fresh clone) el hash difiere porque los gitignored files no existen.
El workflow `kronos-ci.yml` lo ejecuta como informativo (`::warning::`),
no bloqueante.

## Fix futuro

Migrar de `find .` a `git ls-files -z` para hashear solo archivos tracked.
Requiere ancla #17+ con hash reproducible desde cualquier `git clone`.
Las anclas #15/#16 usaban `find`, son reproducibles solo con los paths originales.
