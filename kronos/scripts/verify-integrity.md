# verify-integrity.sh — notas

## Esquema actual (#19+): `git ls-files`

El script hashea solo archivos tracked por git. Paths relativos sin `./`.
Reproducible desde cualquier `git clone` del repo.

## Histórico (#15–#18): `find .`

Versión anterior usaba `find .` que incluía gitignored files en local
y no en CI. El hash resultante NO era reproducible desde un clon limpio.
Esas anclas quedan como registro histórico del esquema viejo.

Migración a `git ls-files` en ancla #19. Los hashes de #15–#18 no
son comparables con #19+ por el cambio de esquema.

## Exclusión del propio log

`.audit-chain.log*` se excluye del hash para evitar auto-referencia
(el log contiene el hash de sí mismo). Patrón: `^\.audit-chain\.log`.
