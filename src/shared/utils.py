"""
Shared utility functions
"""
import json
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized API Gateway response

    Args:
        status_code: HTTP status code
        body: Response body dictionary

    Returns:
        API Gateway response dict
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps(body),
    }


def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Create a standardized error response

    Args:
        status_code: HTTP status code
        message: Error message

    Returns:
        API Gateway error response dict
    """
    return create_response(status_code, {"error": message})


def get_ttl_timestamp(days: int) -> int:
    """
    Calculate TTL timestamp for DynamoDB

    Args:
        days: Number of days until expiration

    Returns:
        Unix timestamp
    """
    expiration = datetime.utcnow() + timedelta(days=days)
    return int(expiration.timestamp())


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> tuple[bool, str]:
    """
    Validate that required fields are present in the data

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    return True, ""
