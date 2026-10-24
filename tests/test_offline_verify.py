"""Verificacion offline de un recibo ML-DSA-87 sin contactar la API."""
import json
import base64
import hashlib
from pathlib import Path
from dilithium_py.ml_dsa import ML_DSA_87


def test_example_receipt_is_valid():
    root = Path(__file__).parent.parent / "examples"
    data = (root / "test-artifact.txt").read_bytes()
    receipt = json.loads((root / "test-artifact.txt.receipt.json").read_text())

    sha = hashlib.sha256(data).hexdigest()
    assert sha == receipt["sha256"], "hash no coincide con el recibo"

    pk = base64.b64decode(receipt["signer_pk_b64"])
    sig = base64.b64decode(receipt["sig_b64"])
    assert ML_DSA_87.verify(pk, data, sig), "firma ML-DSA-87 invalida"
