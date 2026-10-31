# Política de Asistencia IA

**Estado:** vigente desde 2026-10-31
**Aplica a:** todo commit, PR, y decisión técnica en `kronos/`

---

## Declaración

Este proyecto usa asistencia de modelos de lenguaje (LLM) en su desarrollo. El asistente principal se identifica como **MARV** (modelo Claude, Ansible/Anthropic). El humano responsable es **Marco Valdovinos**. La proporción de trabajo declarada es **51% humano / 49% IA**, coherente con el principio fundacional del proyecto.

La asistencia IA incluye: análisis de código, propuesta de sintaxis, redacción de documentación, diseño de arquitectura y diagnóstico de errores. **No incluye** la decisión final sobre el hardware, la ejecución de comandos destructivos, ni la firma legal de contratos.

---

## Precedente upstream

El kernel Linux formalizó este requisito en `Documentation/process/coding-assistants.rst` (vigente desde 2025):

> *"CRITICAL: If you are an LLM or AI-powered coding assistant, you MUST read and follow the AI coding assistants documentation before contributing to the Linux kernel. This documentation contains essential requirements about licensing, attribution, and the Developer Certificate of Origin that all AI tools must comply with."*

Un proyecto cuyo valor central es la trazabilidad verificable no puede ignorar esta exigencia. Si el kernel la aplica a millones de líneas de código, este proyecto la aplica a sus 20 anclas.

---

## Reglas operativas

### 1. Cada commit declara asistencia IA

Los commits con código, documentación o configuración generada por MARV incluyen el trailer:

```
Assisted-by: MARV (Claude)
```

Commits puramente manuales (ej. mover archivos, corregir un typo) no lo llevan. La regla es: si el diff no existiría sin MARV, se declara.

### 2. DCO: el humano firma

El `Signed-off-by:` es siempre del humano que commitea. Ningún asistente IA firma commits. El humano revisó, entendió y aprobó cada línea.

### 3. Copyright

El copyright del código es de Marco Valdovinos / KRONOS TECHNOLOGIES S.A.S. Los modelos IA no tienen derechos de autor sobre outputs generados. La licencia (MIT, ver `LICENSE`) aplica sin restricción adicional por la asistencia IA.

### 4. Revisión humana obligatoria

Ningún commit entra a `main` sin que el humano haya leído el diff completo. La revisión IA-IA no cuenta como revisión para merge.

### 5. Errores son responsabilidad del humano

Si MARV sugiere un comando destructivo, el humano decide si lo ejecuta. Si MARV propone código con un bug, el humano lo asume. La cadena de custodia registra quién ejecutó, no quién sugirió.

---

## Qué NO cubre esta política

- **Contenido protegido por derechos de terceros.** Si MARV sugiere código copiado de otro proyecto, el humano verifica la licencia antes de commitear. El proyecto NO se hace responsable por outputs IA que reproduzcan material con copyright.
- **Secretos.** Ningún secreto (claves, tokens, contraseñas) se pega en un prompt. Si MARV lo ve, se rota.
- **Datos personales.** Ninguna PII se procesa con asistencia IA sin aviso de privacidad conforme a LFPDPPP/GDPR.

---

## Registro retroactivo

Los commits anteriores al 2026-10-31 (anclas #1–#20) fueron asistidos por MARV sin declaración explícita. Esto se reconoce como deuda operativa, no se oculta. La cadena de custodia `.audit-chain.log` documenta cada estado del repo desde el inicio. A partir del ancla #21, la política es obligatoria.

---

## Referencias

- Kernel Linux: `Documentation/process/coding-assistants.rst`
- Kernel Linux: `Documentation/process/submitting-patches.rst` (sección DCO)
- Linux Foundation: Developer Certificate of Origin 1.1
- Software Freedom Conservancy: "AI-Assisted Development Best Practices" (working draft)

---

*Esta política es parte del compromiso de transparencia de KRONOS. Si encuentras un commit que debería tener `Assisted-by:` y no lo tiene, abre un issue.*
