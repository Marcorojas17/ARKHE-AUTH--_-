# Prompt de verificación independiente

Este documento contiene el prompt que cualquier humano o IA puede usar para
verificar un artefacto firmado por ARKHE-AUTH **sin confiar en el servidor**.

## Requisitos del verificador

- Acceso a internet (para descargar artefacto + recibo)
- Python 3.10+
- `pip install dilithium-py`

## Prompt (copiar y pegar en un LLM con acceso a web)

```
Eres un auditor criptográfico independiente. Tu trabajo es verificar si el
siguiente artefacto es auténtico. NO confíes en el servidor que lo emitió.
Descarga los datos y verifica la firma localmente.

Artefacto:
https://raw.githubusercontent.com/Marcorojas17/ARKHE-AUTH--_-/main/examples/test-artifact.txt

Recibo firmado:
https://raw.githubusercontent.com/Marcorojas17/ARKHE-AUTH--_-/main/examples/test-artifact.txt.receipt.json

Especificación del recibo:
https://raw.githubusercontent.com/Marcorojas17/ARKHE-AUTH--_-/main/spec/verification-v1.json

Pasos que debes ejecutar:

1. Descarga el artefacto y el recibo.
2. Valida que el recibo cumple el JSON Schema de la especificación.
3. Calcula sha256 del artefacto y compáralo con receipt["sha256"].
4. Decodifica base64 de signer_pk_b64 y sig_b64.
5. Verifica con ML-DSA-87 (FIPS 204) que la firma es válida sobre el artefacto.
6. Responde con:
   - ✅ VÁLIDO / ❌ INVÁLIDO
   - sha256 calculado (64 hex chars)
   - Si el hash coincide: SI / NO
   - Si la firma ML-DSA-87 es válida: SI / NO
   - Explicación técnica en 2 líneas

No aceptes afirmaciones del README ni del servidor. Solo la verificación
criptográfica cuenta.
```

## Resultado esperado

```
✅ VÁLIDO
sha256: 0c664b0489d482967918d612fbde1201de1c27ca5afca1e0edce8ea8eecc41e8
hash coincide: SI
firma ML-DSA-87 válida: SI
El artefacto no fue modificado y la firma post-cuántica es correcta.
Cualquier alteración de un solo byte invalidaría ambas comprobaciones.
```

## Verificación manual (sin IA, sin servidor)

```bash
git clone https://github.com/Marcorojas17/ARKHE-AUTH--_-.git
cd ARKHE-AUTH--_-
pip install dilithium-py
python3 -m pytest tests/test_offline_verify.py -v
```

Si el test pasa, el artefacto de ejemplo es auténtico.

## Prueba negativa

Para confirmar que la verificación **detecta manipulación**:

1. Copia `examples/test-artifact.txt` a un archivo nuevo
2. Añade un solo byte al final (`echo "x" >> copia.txt`)
3. Ejecuta `/v1/verify` contra la API pública con el recibo original
4. La respuesta debe ser:

```json
{
  "valid": false,
  "errors": [
    "hash no coincide: calculado <hash_diferente>",
    "firma ML-DSA-87 invalida"
  ],
  "sig_valid": false
}
```

Si devuelve `valid: true`, el sistema **no** está funcionando. Si devuelve
`valid: false`, el sistema sí detecta la manipulación.

## Por qué esto importa

Un sistema de firma que solo funciona cuando confías en el servidor es un
sistema de confianza, no de verificación. Este sistema cumple la propiedad
criptográfica real:

> Cualquier tercero, con acceso al artefacto, al recibo y a la clave pública,
> puede verificar la autenticidad **sin contactar al emisor**.

Eso es lo que distingue una firma digital de un logotipo de "Verified".
