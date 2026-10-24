[![tests](https://github.com/Marcorojas17/ARKHE-AUTH--_-/actions/workflows/test.yml/badge.svg)](https://github.com/Marcorojas17/ARKHE-AUTH--_-/actions/workflows/test.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/Marcorojas17/ARKHE-AUTH--_-/badge)](https://securityscorecards.dev/viewer/?uri=github.com/Marcorojas17/ARKHE-AUTH--_-)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)

# ARKHE-AUTH

Verificación criptográfica anti-falsificación con firma post-cuántica
(ML-DSA-87, FIPS 204) y anclaje inmutable en Bitcoin (OpenTimestamps).

## Qué hace

Firma cualquier artefacto (documento, imagen, binario, número de serie de
producto) con ML-DSA-87 y produce un recibo verificable offline por
cualquier tercero, humano o IA, sin confiar en el servidor que lo emitió.

## Estado

Pre-alpha. Repo en construcción activa.

## Stack

- ML-DSA-87 (FIPS 204) — firma post-cuántica
- SHA-256 — hash de integridad
- OpenTimestamps — anclaje en Bitcoin
- FastAPI — API pública de verificación
- PWA — verificación offline desde el navegador

## Estructura

- `spec/` — contratos técnicos (JSON Schema, OpenAPI)
- `core/signer/` — firma ML-DSA-87
- `core/verifier/` — verificación offline
- `core/ots/` — anclaje OpenTimestamps
- `api/` — servicio HTTP
- `web/` — PWA de verificación
- `tests/` — pruebas
- `deploy/` — scripts de despliegue en Termux

## Contacto

Abrir un GitHub Issue en este repositorio.

## Ecosistema historico

La narrativa conceptual completa vive en:
https://github.com/Marcorojas17/kronos-protocol

Este repositorio es la implementacion tecnica de produccion.
