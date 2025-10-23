"""
Personal AI Chatbot - Main Chat Handler (Phase 1)
Handles chat requests, manages conversation history, calls Bedrock
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError

# Environment variables
TABLE_NAME = os.environ.get('CONVERSATIONS_TABLE')
MODEL_ID = os.environ.get('AI_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Initialize AWS clients with explicit credentials
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
bedrock = boto3.client(
    'bedrock-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Constants
MAX_HISTORY_MESSAGES = 10
TTL_DAYS = 30


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for chat requests"""
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        conversation_id = body.get('conversation_id', 'default')
        user_message = body.get('message', '')
        
        if not user_message:
            return response(400, {'error': 'Message is required'})
        
        print(f"Processing chat request - conversation_id: {conversation_id}")
        
        # Load conversation history
        history = load_conversation_history(conversation_id)
        
        # Save user message
        save_message(conversation_id, 'user', user_message)
        
        # Build messages for Claude
        messages = build_messages(history, user_message)
        
        # Call Bedrock
        assistant_response = call_bedrock(messages)
        
        # Save assistant response
        save_message(conversation_id, 'assistant', assistant_response)
        
        return response(200, {
            'conversation_id': conversation_id,
            'message': assistant_response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error', 'details': str(e)})


def load_conversation_history(conversation_id: str) -> list:
    """Load recent conversation history from DynamoDB"""
    try:
        table = dynamodb.Table(TABLE_NAME)
        response = table.query(
            KeyConditionExpression='conversation_id = :cid',
            ExpressionAttributeValues={':cid': conversation_id},
            ScanIndexForward=False,  # Most recent first
            Limit=MAX_HISTORY_MESSAGES
        )
        
        # Reverse to get chronological order
        items = list(reversed(response.get('Items', [])))
        return items
        
    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return []


def save_message(conversation_id: str, role: str, content: str):
    """Save message to DynamoDB"""
    try:
        table = dynamodb.Table(TABLE_NAME)
        timestamp = datetime.utcnow().isoformat()
        ttl = int((datetime.utcnow() + timedelta(days=TTL_DAYS)).timestamp())
        
        table.put_item(
            Item={
                'conversation_id': conversation_id,
                'timestamp': timestamp,
                'role': role,
                'content': content,
                'ttl': ttl
            }
        )
        print(f"Saved {role} message to DynamoDB")
        
    except ClientError as e:
        print(f"Error saving message: {e}")


def build_messages(history: list, user_message: str) -> list:
    """Build messages array for Claude API"""
    messages = []
    
    # Add history
    for item in history:
        messages.append({
            'role': item['role'],
            'content': item['content']
        })
    
    # Add current user message
    messages.append({
        'role': 'user',
        'content': user_message
    })
    
    return messages


def call_bedrock(messages: list) -> str:
    """Call Bedrock API with Claude model"""
    try:
        # Prepare request
        request_body = {
            'anthropic_version': 'bedrock-2023-05-31',
            'messages': messages,
            'max_tokens': 2048,
            'temperature': 0.7,
            'top_p': 0.9
        }
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        assistant_message = response_body['content'][0]['text']
        
        print(f"Bedrock response received ({len(assistant_message)} chars)")
        return assistant_message
        
    except ClientError as e:
        print(f"Bedrock error: {e}")
        return "I'm sorry, I encountered an error processing your request."


def response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Format API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }
