"""
Lambda authorizer for API key validation
"""
import os
import json
import boto3
import logging
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
secrets_client = boto3.client('secretsmanager')

# Environment variables
API_KEY_SECRET_ARN = os.environ.get('API_KEY_SECRET_ARN')


def get_api_key_from_secrets() -> str:
    """
    Retrieve API key from AWS Secrets Manager

    Returns:
        API key string
    """
    try:
        response = secrets_client.get_secret_value(SecretId=API_KEY_SECRET_ARN)
        secret = json.loads(response['SecretString'])
        return secret.get('api_key', '')
    except Exception as e:
        logger.error(f"Error retrieving API key: {str(e)}")
        raise


def generate_policy(principal_id: str, effect: str, resource: str) -> Dict[str, Any]:
    """
    Generate IAM policy for API Gateway

    Args:
        principal_id: User identifier
        effect: 'Allow' or 'Deny'
        resource: API Gateway resource ARN

    Returns:
        IAM policy document
    """
    auth_response = {
        'principalId': principal_id
    }

    if effect and resource:
        policy_document = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
        auth_response['policyDocument'] = policy_document

    return auth_response


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda authorizer handler

    Args:
        event: API Gateway authorizer event
        context: Lambda context

    Returns:
        IAM policy document
    """
    try:
        # Extract API key from header
        token = event.get('authorizationToken', '')

        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        # Get valid API key from Secrets Manager
        valid_api_key = get_api_key_from_secrets()

        # Validate API key
        if token and token == valid_api_key:
            logger.info("API key validation successful")
            return generate_policy('user', 'Allow', event['methodArn'])
        else:
            logger.warning("API key validation failed")
            return generate_policy('user', 'Deny', event['methodArn'])

    except Exception as e:
        logger.error(f"Authorization error: {str(e)}")
        # Deny access on error
        return generate_policy('user', 'Deny', event['methodArn'])
