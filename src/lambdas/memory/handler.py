"""
Memory Lambda Handler - Memory management endpoint
"""
import json
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.services import MemoryService
from src.utils import get_logger

logger = get_logger(__name__)


def lambda_handler(event, context):
    """
    Handle memory management requests

    Supported operations:
    - GET /memory/{conversation_id} - Get conversation history
    - GET /memory/list?category=X - List memories
    """
    try:
        http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('rawPath', '')
        query_params = event.get('queryStringParameters', {}) or {}

        memory_service = MemoryService()

        # List memories
        if 'list' in path:
            category = query_params.get('category')
            limit = int(query_params.get('limit', 100))

            memories = memory_service.list_memories(category=category, limit=limit)

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'count': len(memories),
                    'memories': [m.to_dict() for m in memories]
                })
            }

        # Get conversation
        elif http_method == 'GET':
            # Extract conversation_id from path
            path_parts = path.split('/')
            if len(path_parts) < 3:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Conversation ID required'})
                }

            conversation_id = path_parts[-1]
            limit = int(query_params.get('limit', 50))

            conversation = memory_service.get_conversation(
                conversation_id=conversation_id,
                limit=limit,
                decrypt=True
            )

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'conversation_id': conversation.conversation_id,
                    'message_count': len(conversation.messages),
                    'messages': [m.to_dict() for m in conversation.messages]
                })
            }

        else:
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Method not allowed'})
            }

    except Exception as e:
        logger.error(f"Memory handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
