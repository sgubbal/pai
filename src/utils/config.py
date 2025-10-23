"""
Configuration management for PAI Agent - Phase 1 MVP
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()


class Config:
    """Application configuration for Phase 1"""

    # AWS Configuration
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Environment
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'dev')

    # DynamoDB Table for Phase 1
    CONVERSATIONS_TABLE: str = os.getenv('CONVERSATIONS_TABLE', 'pai-conversations-dev')

    # AI Model for Phase 1
    AI_MODEL_ID: str = os.getenv('AI_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

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
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY'
        ]

        missing = [field for field in required_fields if not getattr(cls, field)]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        return True


# Singleton instance
config = Config()
