"""
Configuration management for PAI Agent
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()


class Config:
    """Application configuration"""

    # AWS Configuration
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCOUNT_ID: Optional[str] = os.getenv('AWS_ACCOUNT_ID')

    # Environment
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'dev')

    # DynamoDB Tables
    CONVERSATIONS_TABLE: str = os.getenv('CONVERSATIONS_TABLE', 'pai-conversations-dev')
    MEMORIES_TABLE: str = os.getenv('MEMORIES_TABLE', 'pai-memories-dev')

    # S3 Buckets
    MEMORY_BUCKET: str = os.getenv('MEMORY_BUCKET', 'pai-long-term-memory')

    # KMS
    KMS_KEY_ID: Optional[str] = os.getenv('KMS_KEY_ID')

    # AI Models
    AI_MODEL_ID: str = os.getenv('AI_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    EMBEDDING_MODEL_ID: str = os.getenv('EMBEDDING_MODEL_ID', 'amazon.titan-embed-text-v2:0')

    # Vector Search
    VECTOR_SEARCH_ENDPOINT: Optional[str] = os.getenv('VECTOR_SEARCH_ENDPOINT')
    OPENSEARCH_INDEX_NAME: str = os.getenv('OPENSEARCH_INDEX_NAME', 'pai-memories')
    VECTOR_DIMENSION: int = int(os.getenv('VECTOR_DIMENSION', '1024'))

    # Memory Configuration
    SHORT_TERM_RETENTION_DAYS: int = int(os.getenv('SHORT_TERM_RETENTION_DAYS', '7'))
    LONG_TERM_RETENTION_DAYS: int = int(os.getenv('LONG_TERM_RETENTION_DAYS', '365'))

    # API Configuration
    API_THROTTLE_RATE: int = int(os.getenv('API_THROTTLE_RATE', '10'))
    API_THROTTLE_BURST: int = int(os.getenv('API_THROTTLE_BURST', '20'))

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If required configuration is missing
        """
        required_fields = [
            'CONVERSATIONS_TABLE',
            'MEMORIES_TABLE',
            'MEMORY_BUCKET',
        ]

        missing = [field for field in required_fields if not getattr(cls, field)]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        return True


# Singleton instance
config = Config()
