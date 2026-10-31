# ADR-006: Confianza en metadatos diferidos

**Estado:** aceptado
**Fecha:** 2026-10-31
**Contexto:** lecciones de CVE-2026-99999 (PwnEscape), patch fbnic, y bug interno de ancla #15–#19

---

## Contexto

Tres incidentes distintos en el mismo día revelaron el mismo antipatrón estructural:

| Incidente | Validación en | Uso real en | Divergencia |
|---|---|---|---|
| PwnEscape (CVE-2026-99999) | `skb_transport_offset(skb)` (relativo a `skb->data`) | `ip_hdrlen(skb)` (relativo a `network_header`) | Diferencia entre vista relativa al frame y vista relativa al header |
| fbnic (netdev 2026-10-30) | `qt->sub0.q_idx` (header buffer queue, siempre 0) | `qt->cmpl.q_idx` (completion queue, id real) | Índice "de la primera cola" vs "índice netdev" |
| KRONOS ancla #15–#19 | Hash del working tree **antes** del commit | Hash del working tree **después** del commit | Pre-commit vs post-commit |

Los tres son la misma clase de bug: **un componente intermedio valida un valor relativo a una interpretación; el consumidor final lo usa como si estuviera en otra interpretación. Funciona "casi siempre" porque los valores coinciden accidentalmente. Falla en cuanto difieren.**

---

## Decisión

En KRONOS, **toda verificación de integridad se hace contra la representación final que el consumidor va a usar**, no contra una representación intermedia.

Aplicado a:

### 1. `MerkleStore.append()`
El leaf hash se valida contra el árbol en el mismo estado en que se escribe a disco. No hay transformación entre validación y escritura. Si el proceso muere a media escritura, `recoverTail()` detecta la línea parcial y la trunca. Nunca hay una hoja validada contra un estado que luego difiere.

### 2. `verify-integrity.sh`
El hash se computa con `git ls-files` (archivos tracked) en **ambos lados**: local y CI. No se usa `find .` (que incluye gitignored) porque el consumidor final (CI) no tiene esos archivos. Verificado empíricamente en run `41230602909` con hash `716a7d40` coincidente en local y Ubuntu.

### 3. Anclas de custodia
El hash del ancla se computa **después** del commit que estabiliza los archivos. Nunca antes. Patrón #15–#19 fue roto por esta razón; #20 es la primera ancla con el patrón correcto.

### 4. `AnchorLog.sol` (pendiente de deploy)
El contrato recibe `(root, size)` y valida `root != 0 && size > 0` en el mismo bloque que escribe storage. No hay operación diferida entre validación y escritura. El evento `Anchored` se emite en la misma transacción.

---

## Consecuencias

### Positivas

- Cero falsos positivos de DRIFT en CI desde ancla #20.
- `verify-integrity.sh` reproducible desde cualquier `git clone`.
- Patrón documentado para futuras implementaciones (receipts, worker on-chain, API).

### Negativas

- Cambio de esquema en `.audit-chain.log` (#15–#19 con `find`, #20+ con `git ls-files`). Los hashes no son comparables entre ambos esquemas. Documentado en `scripts/verify-integrity.md`.
- Requiere que el humano recuerde el orden: commit → hash → ancla → commit ancla → push. No es automático.

---

## Referencias

- CVE-2026-99999: https://pwn.ai/blog/pwnescape
- Fix upstream Linux: commit `6785011f8b16` (mainline v7.3)
- Patch v6 propuesto: https://lore.kernel.org/netdev/20260922030310.8684-2-habte.yibelo@gmail.com/
- fbnic patch: https://lore.kernel.org/netdev/20261030141450.xxxxx/
- Bug interno KRONOS: anclas #15–#19 en `.audit-chain.log`

---

*Este ADR documenta el antipatrón y la política de defensa. Cualquier nueva verificación de integridad en KRONOS debe demostrar que cumple la regla "validar contra representación final".*
