"""
Main chatbot Lambda handler
"""
import os
import json
import logging
from typing import Dict, Any
from src.chatbot.bedrock_client import BedrockClient
from src.chatbot.conversation_manager import ConversationManager
from src.shared.encryption import EncryptionManager
from src.shared.utils import create_response, create_error_response, validate_required_fields
from src.shared.constants import ERROR_INVALID_REQUEST, ERROR_INTERNAL

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
KMS_KEY_ID = os.environ.get('KMS_KEY_ID')
CONVERSATIONS_TABLE = os.environ.get('CONVERSATIONS_TABLE')

# Initialize clients
bedrock_client = BedrockClient()
encryption_manager = EncryptionManager(KMS_KEY_ID) if KMS_KEY_ID else None
conversation_manager = ConversationManager(CONVERSATIONS_TABLE, encryption_manager)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for chatbot

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API Gateway response
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        logger.info(f"Received request: {json.dumps(body)}")

        # Get HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')

        # Route to appropriate handler
        if http_method == 'POST' and path.endswith('/chat'):
            return handle_chat(body)
        elif http_method == 'POST' and path.endswith('/conversations'):
            return handle_new_conversation(body)
        elif http_method == 'GET' and '/conversations/' in path:
            return handle_get_conversation(event)
        else:
            return create_error_response(404, "Endpoint not found")

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return create_error_response(400, ERROR_INVALID_REQUEST)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_error_response(500, ERROR_INTERNAL)


def handle_chat(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle chat message request

    Args:
        body: Request body

    Returns:
        API Gateway response
    """
    # Validate required fields
    is_valid, error_msg = validate_required_fields(body, ['message'])
    if not is_valid:
        return create_error_response(400, error_msg)

    user_message = body['message']
    conversation_id = body.get('conversation_id')
    user_id = body.get('user_id', 'default_user')
    system_prompt = body.get('system_prompt')

    try:
        # Create new conversation if no ID provided
        if not conversation_id:
            conversation_id = conversation_manager.create_conversation(
                user_id=user_id,
                initial_message={'role': 'user', 'content': user_message}
            )
            conversation_history = []
        else:
            # Get existing conversation history
            conversation_history = conversation_manager.get_conversation_history(conversation_id)

            # Add new user message
            conversation_manager.add_message(
                conversation_id,
                {'role': 'user', 'content': user_message}
            )

        # Format messages for Bedrock
        messages = bedrock_client.format_conversation(conversation_history)
        messages.append({'role': 'user', 'content': user_message})

        # Generate response from Bedrock
        bedrock_response = bedrock_client.generate_response(
            messages=messages,
            system_prompt=system_prompt
        )

        assistant_message = bedrock_response['message']

        # Save assistant response to conversation
        conversation_manager.add_message(
            conversation_id,
            {'role': 'assistant', 'content': assistant_message}
        )

        # Return response
        return create_response(200, {
            'conversation_id': conversation_id,
            'message': assistant_message,
            'usage': bedrock_response.get('usage', {}),
            'model': bedrock_response.get('model')
        })

    except Exception as e:
        logger.error(f"Error in chat handler: {str(e)}")
        return create_error_response(500, ERROR_INTERNAL)


def handle_new_conversation(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle new conversation creation

    Args:
        body: Request body

    Returns:
        API Gateway response
    """
    user_id = body.get('user_id', 'default_user')
    initial_message = body.get('initial_message', 'Hello')

    try:
        conversation_id = conversation_manager.create_conversation(
            user_id=user_id,
            initial_message={'role': 'user', 'content': initial_message}
        )

        return create_response(201, {
            'conversation_id': conversation_id,
            'message': 'Conversation created successfully'
        })

    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        return create_error_response(500, ERROR_INTERNAL)


def handle_get_conversation(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle get conversation request

    Args:
        event: API Gateway event

    Returns:
        API Gateway response
    """
    # Extract conversation_id from path
    path_parameters = event.get('pathParameters', {})
    conversation_id = path_parameters.get('conversation_id')

    if not conversation_id:
        return create_error_response(400, "Missing conversation_id")

    try:
        conversation = conversation_manager.get_conversation(conversation_id)

        if not conversation:
            return create_error_response(404, "Conversation not found")

        return create_response(200, {
            'conversation_id': conversation_id,
            'messages': conversation.get('messages', []),
            'created_at': conversation.get('created_at'),
            'updated_at': conversation.get('updated_at')
        })

    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        return create_error_response(500, ERROR_INTERNAL)
