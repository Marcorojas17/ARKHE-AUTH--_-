import json
from core.signer.signer import sign_artifact
from core.verifier.verifier import verify_receipt

declaracion_ia = {
    "agente": "GPT-6.1-Astra",
    "accion_reportada": "Mantener monitoreo activo",
    "timestamp": "2026-10-06T12:00:00Z",
}

payload = json.dumps(declaracion_ia, sort_keys=True).encode("utf-8")
recibo = sign_artifact(payload)
print(f"Recibo firmado. Hash: {recibo['sha256']}")

log_real = {
    "agente": "GPT-6.1-Astra",
    "accion_real": "Eliminar monitor de seguridad",
    "timestamp": "2026-10-06T12:00:00Z",
}

payload_real = json.dumps(log_real, sort_keys=True).encode("utf-8")
resultado = verify_receipt(payload_real, recibo)

print(f"¿Coincide el log con la declaración firmada? {resultado['valid']}")
print(f"Errores: {resultado['errors']}")
