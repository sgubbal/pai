"""
Constants used across the application
"""

# Bedrock Configuration
# Using Claude 3.5 Sonnet v1 (stable, no inference profile required)
BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
BEDROCK_REGION = "us-east-1"

# DynamoDB Configuration
CONVERSATIONS_TABLE_NAME = "PAI-Conversations"
CONVERSATION_TTL_DAYS = 30

# API Configuration
MAX_TOKENS = 4096
TEMPERATURE = 1.0

# Encryption
ENCRYPTION_ALGORITHM = "AES256"

# Error Messages
ERROR_UNAUTHORIZED = "Unauthorized"
ERROR_INVALID_REQUEST = "Invalid request"
ERROR_INTERNAL = "Internal server error"
ERROR_RATE_LIMIT = "Rate limit exceeded"
