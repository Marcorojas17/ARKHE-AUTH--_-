# Vulnerabilidades dev-only conocidas

`pnpm audit` reporta advisories en dependencias transitivas de `viem`.
Estas dependencias NO se incluyen en runtime de produccion:
- `contracts/` solo corre en Termux para deploy/check/anchor
- `deploy.mjs`, `check.mjs`, `anchor.mjs` no se importan desde `apps/` ni `packages/`
- el contrato compilado no lleva JS, solo bytecode

Riesgo: cero en produccion. Aceptado hasta que `viem` actualice deps.

Comando para verificar:
```bash
cd kronos/contracts && pnpm audit
```

Fecha de revision: 2026-10-31
