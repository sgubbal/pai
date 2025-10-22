"""
Encryption service using AWS KMS
"""
import base64
import boto3
from typing import Optional
from ..utils import get_logger, config

logger = get_logger(__name__)


class EncryptionService:
    """Handles encryption/decryption using AWS KMS"""

    def __init__(self, kms_key_id: Optional[str] = None):
        """
        Initialize encryption service

        Args:
            kms_key_id: KMS key ID (defaults to config value)
        """
        self.kms_client = boto3.client('kms', region_name=config.AWS_REGION)
        self.kms_key_id = kms_key_id or config.KMS_KEY_ID

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using KMS

        Args:
            plaintext: Text to encrypt

        Returns:
            Base64-encoded ciphertext
        """
        try:
            if not self.kms_key_id:
                logger.warning("KMS key not configured, returning plaintext")
                return plaintext

            response = self.kms_client.encrypt(
                KeyId=self.kms_key_id,
                Plaintext=plaintext.encode('utf-8')
            )

            ciphertext = base64.b64encode(response['CiphertextBlob']).decode('utf-8')
            logger.debug(f"Encrypted {len(plaintext)} bytes")
            return ciphertext

        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext using KMS

        Args:
            ciphertext: Base64-encoded ciphertext

        Returns:
            Decrypted plaintext
        """
        try:
            if not self.kms_key_id:
                logger.warning("KMS key not configured, returning ciphertext as-is")
                return ciphertext

            ciphertext_blob = base64.b64decode(ciphertext.encode('utf-8'))

            response = self.kms_client.decrypt(
                CiphertextBlob=ciphertext_blob,
                KeyId=self.kms_key_id
            )

            plaintext = response['Plaintext'].decode('utf-8')
            logger.debug(f"Decrypted to {len(plaintext)} bytes")
            return plaintext

        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

    def generate_data_key(self) -> dict:
        """
        Generate a data encryption key

        Returns:
            Dictionary with plaintext and ciphertext keys
        """
        try:
            response = self.kms_client.generate_data_key(
                KeyId=self.kms_key_id,
                KeySpec='AES_256'
            )

            return {
                'plaintext': base64.b64encode(response['Plaintext']).decode('utf-8'),
                'ciphertext': base64.b64encode(response['CiphertextBlob']).decode('utf-8')
            }

        except Exception as e:
            logger.error(f"Data key generation failed: {str(e)}")
            raise
