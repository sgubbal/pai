"""
End-to-end encryption utilities using AWS KMS
"""
import base64
import boto3
import logging
from typing import Optional

logger = logging.getLogger()
kms_client = boto3.client('kms')


class EncryptionManager:
    """
    Manages encryption and decryption using AWS KMS
    """

    def __init__(self, kms_key_id: str):
        """
        Initialize encryption manager

        Args:
            kms_key_id: AWS KMS key ID or ARN
        """
        self.kms_key_id = kms_key_id

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt data using KMS

        Args:
            plaintext: String to encrypt

        Returns:
            Base64 encoded encrypted data
        """
        try:
            response = kms_client.encrypt(
                KeyId=self.kms_key_id,
                Plaintext=plaintext.encode('utf-8')
            )

            # Return base64 encoded ciphertext
            return base64.b64encode(response['CiphertextBlob']).decode('utf-8')

        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt data using KMS

        Args:
            ciphertext: Base64 encoded encrypted data

        Returns:
            Decrypted plaintext string
        """
        try:
            # Decode base64
            ciphertext_blob = base64.b64decode(ciphertext)

            response = kms_client.decrypt(
                CiphertextBlob=ciphertext_blob,
                KeyId=self.kms_key_id
            )

            return response['Plaintext'].decode('utf-8')

        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise

    def encrypt_conversation(self, conversation_data: dict) -> dict:
        """
        Encrypt sensitive fields in conversation data

        Args:
            conversation_data: Dictionary containing conversation data

        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = conversation_data.copy()

        # Encrypt message content
        if 'messages' in encrypted_data:
            for message in encrypted_data['messages']:
                if 'content' in message:
                    message['content'] = self.encrypt(message['content'])

        return encrypted_data

    def decrypt_conversation(self, encrypted_data: dict) -> dict:
        """
        Decrypt sensitive fields in conversation data

        Args:
            encrypted_data: Dictionary containing encrypted conversation data

        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = encrypted_data.copy()

        # Decrypt message content
        if 'messages' in decrypted_data:
            for message in decrypted_data['messages']:
                if 'content' in message:
                    message['content'] = self.decrypt(message['content'])

        return decrypted_data
