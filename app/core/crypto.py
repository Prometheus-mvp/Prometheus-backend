"""AES-256-GCM encryption/decryption for OAuth tokens."""

import hashlib
import logging
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting and decrypting sensitive data using AES-256-GCM."""

    def __init__(self, key: Optional[str] = None):
        """
        Initialize encryption service.

        Args:
            key: 32-byte hex string encryption key.
                If None, uses ENCRYPTION_KEY from settings.
        """
        key_hex = key or settings.encryption_key
        if len(key_hex) != 64:  # 32 bytes = 64 hex characters
            raise ValueError("Encryption key must be 32 bytes (64 hex characters)")
        self.key = bytes.fromhex(key_hex)
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256-GCM.

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded encrypted data with nonce (format: nonce:encrypted_data)
        """
        if not plaintext:
            return ""

        # Generate random 12-byte nonce (required for GCM)
        nonce = os.urandom(12)

        # Encrypt
        plaintext_bytes = plaintext.encode("utf-8")
        ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)

        # Combine nonce and ciphertext, encode as hex
        combined = nonce + ciphertext
        return combined.hex()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data using AES-256-GCM.

        Args:
            encrypted_data: Hex-encoded encrypted data with nonce

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If decryption fails (invalid key, corrupted data, etc.)
        """
        if not encrypted_data:
            return ""

        try:
            # Decode from hex
            combined = bytes.fromhex(encrypted_data)

            # Extract nonce (first 12 bytes) and ciphertext (rest)
            nonce = combined[:12]
            ciphertext = combined[12:]

            # Decrypt
            plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext_bytes.decode("utf-8")

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Failed to decrypt data: {e}")

    def generate_token_fingerprint(self, token: str) -> str:
        """
        Generate a fingerprint/hash of a token for identification
        without storing the full token.

        Args:
            token: Token string to fingerprint

        Returns:
            SHA-256 hash of the token (hex string)
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


# Global encryption service instance
encryption_service = EncryptionService()
