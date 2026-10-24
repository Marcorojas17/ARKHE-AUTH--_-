"""Verificador offline. No confia en el servidor."""
import hashlib
import base64
from dilithium_py.ml_dsa import ML_DSA_87


def verify_receipt(artifact_bytes: bytes, receipt: dict) -> dict:
    errors = []

    if receipt.get("version") != "verification-v1":
        errors.append("version desconocida")
    if receipt.get("sig_alg") != "ML-DSA-87":
        errors.append("algoritmo no soportado")

    sha256 = hashlib.sha256(artifact_bytes).hexdigest()
    if sha256 != receipt.get("sha256"):
        errors.append(f"hash no coincide: calculado {sha256}")

    try:
        pk = base64.b64decode(receipt["signer_pk_b64"])
        sig = base64.b64decode(receipt["sig_b64"])
        sig_valid = ML_DSA_87.verify(pk, artifact_bytes, sig)
    except Exception as e:
        sig_valid = False
        errors.append(f"error verificacion: {e}")

    if not sig_valid:
        errors.append("firma ML-DSA-87 invalida")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "sha256": sha256,
        "sig_valid": sig_valid,
    }
