# KRONOS — Evidence Integrity OS

Ecosistema descentralizado de integridad documental forense.
Lerma, Estado de México. 2026.

## Estructura

- `apps/` — superficies desplegables (Next.js)
- `packages/` — librerías compartidas (Merkle, SHA-256, SDK)
- `services/` — backends y workers
- `infra/` — Supabase, Vercel, Cloudflare
- `docs/` — documentación técnica y gobernanza
- `legal/` — compliance y propiedad intelectual
- `soberano/` — actas fundacionales
- `research/`, `poc/`, `reports/` — seguridad ofensiva autorizada
- `archive/` — versiones históricas

## Setup local (Termux)

    pkg install -y git nodejs-lts coreutils
    corepack enable && corepack prepare pnpm@latest --activate
    pnpm install

## Verificación de integridad

    ./scripts/verify-integrity.sh

## Licencia

MIT. Ver `LICENSE`.
