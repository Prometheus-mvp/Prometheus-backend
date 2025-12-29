from app.core.crypto import encryption_service


def test_encrypt_decrypt_roundtrip():
    plaintext = "secret-token"
    enc = encryption_service.encrypt(plaintext)
    assert enc != plaintext
    dec = encryption_service.decrypt(enc)
    assert dec == plaintext
