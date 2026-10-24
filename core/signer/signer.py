"""Firma ML-DSA-87 (FIPS 204). Firma el hash SHA-256 para soportar archivos de cualquier tamaño."""
import json
import hashlib
import base64
import os
from dilithium_py.ml_dsa import ML_DSA_87

KEY_DIR = os.path.expanduser("~/.arkhe/keys")
os.makedirs(KEY_DIR, exist_ok=True)

def generate_keypair(name: str = "root") -> None:
    pk, sk = ML_DSA_87.keygen()
    with open(os.path.join(KEY_DIR, f"{name}.pk"), "wb") as f: f.write(pk)
    with open(os.path.join(KEY_DIR, f"{name}.sk"), "wb") as f: f.write(sk)
    print(f"Par de claves generado: {KEY_DIR}/{name}.pk y .sk")

def load_pk(name: str = "root") -> bytes:
    with open(os.path.join(KEY_DIR, f"{name}.pk"), "rb") as f: return f.read()

def load_sk(name: str = "root") -> bytes:
    with open(os.path.join(KEY_DIR, f"{name}.sk"), "rb") as f: return f.read()

def sign_artifact(artifact_bytes: bytes, name: str = "root") -> dict:
    # Calcular el hash del archivo (soporta cualquier tamaño)
    sha256 = hashlib.sha256(artifact_bytes).hexdigest()
    # Firmar el hash en lugar del archivo completo (mucho más rápido y seguro)
    sig = ML_DSA_87.sign(load_sk(name), sha256.encode())
    return {
        "version": "verification-v1",
        "sha256": sha256,
        "sig_alg": "ML-DSA-87",
        "signer_pk_b64": base64.b64encode(load_pk(name)).decode(),
        "sig_b64": base64.b64encode(sig).decode(),
        "artifact_size": len(artifact_bytes),
    }
