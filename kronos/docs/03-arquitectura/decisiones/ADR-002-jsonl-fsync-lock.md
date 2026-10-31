# ADR-002: Persistencia JSONL + fsync + lock sobre SQLite

**Estado:** aceptado
**Fecha:** 2026-10-31
**Contexto:** almacenamiento del arbol Merkle y anclas en Termux Android

---

## Decision

Persistencia en **archivos JSONL append-only** con fh.sync() por linea + lock file. NO SQLite, NO Postgres.

```
.kronos-chain/
  leaves.jsonl      # { i, h, ts } por hoja
  roots.jsonl       # { ts, size, root } por ancla
  .lock             # single-writer, deteccion de stale
```

## Alternativas

| Opcion | Problema |
|---|---|
| better-sqlite3 | Compila nativo, requiere clang en Termux, ~50 MB node_modules |
| sql.js (WASM) | ~1.5 MB, funciona, pero write requiere exportar todo el archivo |
| Postgres | Imposible en Android sin proot + Docker |
| JSON unico | Se corrompe ante crash a media escritura |

## Justificacion

- RAM limitada en Termux (~4 GB device) descarta native deps
- Recovery ante crash es critico en dispositivo que puede apagarse sin avisar
- Cero dependencias alinea con @kronos/sha256-verifier
- Auditable a mano con cat

## Consecuencias

Positivas:
- recoverTail() detecta linea parcial y la trunca (test recovery trunca linea parcial)
- roots.jsonl regenerable desde leaves.jsonl si se pierde
- fsync por linea previene perdida de datos ante kill -9

Negativas:
- Single-writer. Lock no soporta concurrencia real en v1
- Sin indice. Buscar hoja especifica requiere O(n) scan
- Migracion a SQLite es deuda tecnica cuando pase ~100K hojas

## Codigo

packages/core-kronos/src/legado/store.js — 6 tests de persistencia

## Referencias

- RFC 7464: JSON Text Sequences (JSONL)
- fsync(2) man page

---

*Cuando el arbol supere 100K hojas, este ADR debe revisarse. Hoy no es el caso.*
