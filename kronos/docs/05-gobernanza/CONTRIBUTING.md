# Contributing

## Ramas

- `feat/` — nueva funcionalidad
- `fix/` — corrección de bug
- `chore/` — housekeeping, sin cambio funcional
- `research/` — análisis o auditoría

## Commits

Conventional Commits. Ejemplos:

```
feat(core-kronos): agregar verifyBatch con proof paralela
fix(web-verify): corregir hashNode para arboles de altura 0
chore(legado): ancla #21 post-politica IA
```

## Asistencia IA

Todo commit con código o documentación generada por asistencia IA DEBE incluir el trailer:

```
Assisted-by: MARV (Claude)
Signed-off-by: Marco Valdovinos <marco@kronos2099.local>
```

El humano firma con DCO. El asistente IA se declara pero no firma. Ver política completa en [`docs/05-gobernanza/AI-ASSISTANCE-POLICY.md`](AI-ASSISTANCE-POLICY.md).

## Pull Requests

Un PR requiere:

1. Tests pasando (`pnpm test`)
2. `verify-integrity.sh` retornando OK
3. Sin secretos en el diff
4. Checkboxes de asistencia IA completados en el template

## Anclas de custodia

Cada PR que toca `kronos/**` debe generar una entrada nueva en `.audit-chain.log`. El hash se computa **después** del commit (no antes). Ver [`docs/05-gobernanza/AI-ASSISTANCE-POLICY.md`](AI-ASSISTANCE-POLICY.md) sección "Registro retroactivo" para el contexto del patrón #15–#19.
