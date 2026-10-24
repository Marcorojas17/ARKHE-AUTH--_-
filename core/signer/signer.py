"""Firma ML-DSA-87 (FIPS 204). Unica fuente de verdad para firmar artefactos."""
import json
import hashlib
import base64
import os
from dilithium_py.ml_dsa import ML_DSA_87

KEY_DIR = os.path.expanduser("~/.arkhe/keys")
os.makedirs(KEY_DIR, exist_ok=True)


def generate_keypair(name: str = "root") -> None:
    pk, sk = ML_DSA_87.keygen()
    with open(os.path.join(KEY_DIR, f"{name}.pk"), "wb") as f:
        f.write(pk)
    with open(os.path.join(KEY_DIR, f"{name}.sk"), "wb") as f:
        f.write(sk)
    print(f"Par de claves generado: {KEY_DIR}/{name}.pk y .sk")


def load_pk(name: str = "root") -> bytes:
    with open(os.path.join(KEY_DIR, f"{name}.pk"), "rb") as f:
        return f.read()


def load_sk(name: str = "root") -> bytes:
    with open(os.path.join(KEY_DIR, f"{name}.sk"), "rb") as f:
        return f.read()


def sign_artifact(artifact_bytes: bytes, name: str = "root") -> dict:
    sha256 = hashlib.sha256(artifact_bytes).hexdigest()
    sig = ML_DSA_87.sign(load_sk(name), artifact_bytes)
    return {
        "version": "verification-v1",
        "sha256": sha256,
        "sig_alg": "ML-DSA-87",
        "signer_pk_b64": base64.b64encode(load_pk(name)).decode(),
        "sig_b64": base64.b64encode(sig).decode(),
        "artifact_size": len(artifact_bytes),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "keygen":
        generate_keypair()
    elif len(sys.argv) > 1:
        with open(sys.argv[1], "rb") as f:
            receipt = sign_artifact(f.read())
        out = sys.argv[1] + ".receipt.json"
        with open(out, "w") as f:
            json.dump(receipt, f, indent=2)
        print(f"Recibo escrito en {out}")
    else:
        print("Uso: python core/signer/signer.py keygen | <archivo>")
