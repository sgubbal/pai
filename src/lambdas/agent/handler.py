"""
Agent Lambda Handler - Main AI agent endpoint
"""
import json
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.models import Message, Conversation, Memory
from src.services import AIService, MemoryService, VectorService
from src.utils import get_logger, generate_id, get_timestamp

logger = get_logger(__name__)


def lambda_handler(event, context):
    """
    Handle chat requests to the AI agent

    Expected event body:
    {
        "message": "User message text",
        "conversation_id": "optional-conversation-id",
        "use_memory": true,  # optional, default true
        "save_to_memory": true  # optional, default true
    }
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        conversation_id = body.get('conversation_id') or generate_id('conv-')
        use_memory = body.get('use_memory', True)
        save_to_memory = body.get('save_to_memory', True)

        if not user_message:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Message is required'})
            }

        logger.info(f"Processing message for conversation {conversation_id}")

        # Initialize services
        ai_service = AIService()
        memory_service = MemoryService()
        vector_service = VectorService()

        # Create user message
        user_msg = Message(
            role='user',
            content=user_message,
            timestamp=get_timestamp(),
            message_id=generate_id('msg-')
        )

        # Save user message to short-term memory
        memory_service.save_message(conversation_id, user_msg, encrypt=True)

        # Get conversation history
        conversation = memory_service.get_conversation(conversation_id, limit=20)
        history = conversation.get_context_window(max_messages=10)

        # Retrieve relevant memories if enabled
        context = ""
        if use_memory:
            try:
                # Generate embedding for the query
                query_embedding = ai_service.generate_embedding(user_message)

                # Search for relevant memories
                search_results = vector_service.search(
                    query_embedding=query_embedding,
                    limit=5,
                    min_score=0.7
                )

                if search_results:
                    context_parts = [
                        "Relevant context from your memory:",
                        ""
                    ]
                    for result in search_results:
                        context_parts.append(f"- {result.memory.content}")

                    context = "\n".join(context_parts)
                    logger.info(f"Retrieved {len(search_results)} relevant memories")

            except Exception as e:
                logger.error(f"Memory retrieval failed: {str(e)}")
                # Continue without context

        # Prepare system prompt
        system_prompt = """You are a helpful personal AI assistant with access to the user's past conversations and memories.
Use the provided context to give more personalized and relevant responses.
If you reference information from the context, acknowledge it naturally."""

        if context:
            system_prompt += f"\n\n{context}"

        # Get AI response
        ai_response = ai_service.chat(
            message=user_message,
            conversation_history=history,
            system_prompt=system_prompt,
            max_tokens=2048
        )

        # Create assistant message
        assistant_msg = Message(
            role='assistant',
            content=ai_response,
            timestamp=get_timestamp(),
            message_id=generate_id('msg-')
        )

        # Save assistant message to short-term memory
        memory_service.save_message(conversation_id, assistant_msg, encrypt=True)

        # Optionally save important exchanges to long-term memory
        if save_to_memory:
            try:
                # Create a summary of the exchange
                exchange_summary = f"User: {user_message}\nAssistant: {ai_response}"

                # Generate embedding
                embedding = ai_service.generate_embedding(exchange_summary)

                # Create memory
                memory = Memory(
                    memory_id=generate_id('mem-'),
                    content=exchange_summary,
                    embedding=embedding,
                    category='conversation',
                    created_at=get_timestamp(),
                    metadata={
                        'conversation_id': conversation_id,
                        'message_ids': [user_msg.message_id, assistant_msg.message_id]
                    }
                )

                # Save to long-term storage
                memory_service.save_memory(memory, save_to_s3=True)

                # Index for vector search
                vector_service.index_memory(memory)

                logger.info(f"Saved exchange to long-term memory: {memory.memory_id}")

            except Exception as e:
                logger.error(f"Failed to save to long-term memory: {str(e)}")
                # Continue even if long-term save fails

        # Return response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'conversation_id': conversation_id,
                'message': ai_response,
                'timestamp': assistant_msg.timestamp,
                'message_id': assistant_msg.message_id
            })
        }

    except Exception as e:
        logger.error(f"Agent handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
