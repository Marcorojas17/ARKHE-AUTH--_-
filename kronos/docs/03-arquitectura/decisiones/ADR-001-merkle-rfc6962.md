# ADR-001: Merkle RFC 6962 sobre Bitcoin-style

**Estado:** aceptado
**Fecha:** 2026-10-31
**Contexto:** diseño inicial del arbol Merkle del legado

---

## Decision

El arbol Merkle sigue **RFC 6962** (Certificate Transparency), no el diseno de Bitcoin.

| Aspecto | Bitcoin | RFC 6962 (KRONOS) |
|---|---|---|
| Hash hoja | SHA256(data) | SHA256(0x00 + data) |
| Hash nodo | SHA256(L + R) | SHA256(0x01 + L + R) |
| Nodo impar | Duplicar ultimo | Promover al siguiente nivel |

## Contexto

Bitcoin duplica el ultimo nodo impar. Esto permite CVE-2012-2459 (mutacion de arbol) y hace que hojas y nodos internos colisionen en preimagen.

RFC 6962 aplica domain separation (0x00 hoja, 0x01 nodo) para evitar second-preimage attacks. Es el estandar de Certificate Transparency.

## Consecuencias

Positivas:
- Interoperable con CT / sigstore / Trillian
- Inmune a CVE-2012-2459
- Domain separation cubierta por tests en merkle.test.js

Negativas:
- NO interoperable con implementaciones Bitcoin-style
- Hashes distintos de bitcoin-merkle o similares

## Codigo

packages/core-kronos/src/legado/merkle.js — 15 tests unitarios

## Referencias

- RFC 6962: https://datatracker.ietf.org/doc/html/rfc6962
- CVE-2012-2459: Bitcoin merkle tree vulnerability

---

*Domain separation no es opcional. Si se reimplementa el arbol, este ADR es la regla.*
