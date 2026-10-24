from core.signer.signer import generate_keypair, sign_artifact
from core.verifier.verifier import verify_receipt


def test_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("core.signer.signer.KEY_DIR", str(tmp_path))
    generate_keypair("test")
    payload = b"contenido de prueba anti-falsificacion"
    receipt = sign_artifact(payload, "test")
    result = verify_receipt(payload, receipt)
    assert result["valid"], result["errors"]


def test_tampered_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("core.signer.signer.KEY_DIR", str(tmp_path))
    generate_keypair("test")
    payload = b"contenido original"
    receipt = sign_artifact(payload, "test")
    tampered = b"contenido alterado"
    result = verify_receipt(tampered, receipt)
    assert not result["valid"]
