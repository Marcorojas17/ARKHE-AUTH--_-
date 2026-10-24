# Ejemplos de verificacion

## Contenido

- `test-artifact.txt` — artefacto de ejemplo (contenido fijo)
- `test-artifact.txt.receipt.json` — recibo ML-DSA-87 generado por la API publica
- `verify-valid.json` — respuesta de `/v1/verify` con el artefacto original
- `verify-tampered.json` — respuesta de `/v1/verify` con el artefacto modificado

## Verificacion offline

Cualquier tercero puede verificar la firma sin contactar la API.

Requisitos:
- Python 3.10+
- `pip install dilithium-py`

Codigo de verificacion en `tests/test_offline_verify.py`.

## Prueba negativa

El archivo `verify-tampered.json` documenta la respuesta de la API cuando
el artefacto fue modificado. El hash no coincide y la firma no valida.
Si un solo byte cambia, el sistema lo detecta.

## Especificacion

Contrato: `../spec/verification-v1.json`.
