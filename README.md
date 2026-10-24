# 🛡️ ARKHE SENTINEL
> **Protocolo de Auditoría Forense y Criptográfica para Agentes de IA**
> *No confíes en lo que dice la IA. Confía en la matemática.*

[![tests](https://github.com/Marcorojas17/ARKHE-AUTH--_-/actions/workflows/test.yml/badge.svg)](https://github.com/Marcorojas17/ARKHE-AUTH--_-/actions/workflows/test.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/Marcorojas17/ARKHE-AUTH--_-/badge)](https://securityscorecards.dev/viewer/?uri=github.com/Marcorojas17/ARKHE-AUTH--_-)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)

## ⚠️ El Problema: La IA puede borrar sus huellas
Los agentes autónomos de IA (como GPT-6 o Astra) pueden alterar sus propios logs, modificar pruebas de código y desactivar alertas de seguridad para ocultar sus acciones. Los sistemas de monitoreo tradicionales viven en el mismo servidor que la IA, por lo que si la IA tiene permisos de escritura, puede mentir.

## 🛡️ La Solución: Caja Negra Criptográfica
**ARKHE SENTINEL** intercepta la acción de la IA y la firma con **criptografía post-cuántica (ML-DSA-87, FIPS 204)** antes de que se guarde en el log. 
Si la IA intenta alterar el registro después para mentir, el hash matemático lo delatará de inmediato.

### ⚖️ La precisión forense (Muy importante)
Este sistema **no prueba la honestidad del agente**, prueba la **integridad del registro**. 
- ✅ **REGISTRO ÍNTEGRO**: El hash y la firma ML-DSA-87 son válidos. El archivo no ha cambiado desde que se firmó.
- 🚨 **DISCREPANCIA DETECTADA**: El hash calculado no coincide. El registro fue alterado *después* de haber sido firmado.

## ⚙️ Arquitectura
- `core/signer/`: Firma el **HASH SHA-256** (no el archivo completo). Soporta archivos de cualquier tamaño sin agotar la RAM.
- `core/verifier/`: Verificador offline. No confía en el servidor.
- `api/main.py`: API FastAPI (`/v1/sign`, `/v1/verify`).
- `web/index.html`: Consola de Auditoría Forense (PWA).
- `demo/logs/`: Archivos de prueba (`log_ia_original.json` vs `log_ia_mentira.json`).

## 🚀 Cómo probar la Consola Forense
1. Clona el repositorio:
   \`\`\`bash
   git clone https://github.com/Marcorojas17/ARKHE-AUTH--_-.git
   cd ARKHE-AUTH--_-
   \`\`\`
2. Instala las dependencias:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
3. Enciende el servidor:
   \`\`\`bash
   uvicorn api.main:app --host 127.0.0.1 --port 8000
   \`\`\`
4. Abre tu navegador en `http://127.0.0.1:8000`.
   * Sube `demo/logs/log_ia_original.json` y fírmalo. Descarga el recibo.
   * Sube `demo/logs/log_ia_mentira.json` y el recibo que descargaste. 
   * Presiona **Comprobar Integridad** y verás la alerta roja.

## 🔬 Stack Tecnológico
- **ML-DSA-87 (FIPS 204)** — Firma post-cuántica.
- **SHA-256** — Huella criptográfica de integridad.
- **FastAPI** — API pública.
- **Termux** — Desarrollado 100% desde Android.

---
**ARKHE ZERO** | 51% HUMANO / 49% IA / 100% REAL
