"""
Conversation history manager with DynamoDB
"""
import uuid
import boto3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.shared.constants import CONVERSATIONS_TABLE_NAME, CONVERSATION_TTL_DAYS
from src.shared.utils import get_ttl_timestamp
from src.shared.encryption import EncryptionManager

logger = logging.getLogger()
dynamodb = boto3.resource('dynamodb')


class ConversationManager:
    """
    Manages conversation history in DynamoDB
    """

    def __init__(self, table_name: str = CONVERSATIONS_TABLE_NAME, encryption_manager: Optional[EncryptionManager] = None):
        """
        Initialize conversation manager

        Args:
            table_name: DynamoDB table name
            encryption_manager: Optional encryption manager for E2E encryption
        """
        self.table = dynamodb.Table(table_name)
        self.encryption_manager = encryption_manager

    def create_conversation(self, user_id: str, initial_message: Dict[str, str]) -> str:
        """
        Create a new conversation

        Args:
            user_id: User identifier
            initial_message: First message dictionary

        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        messages = [initial_message]

        # Encrypt if encryption manager is available
        if self.encryption_manager:
            for msg in messages:
                msg['content'] = self.encryption_manager.encrypt(msg['content'])

        try:
            self.table.put_item(
                Item={
                    'conversation_id': conversation_id,
                    'user_id': user_id,
                    'created_at': timestamp,
                    'updated_at': timestamp,
                    'messages': messages,
                    'ttl': get_ttl_timestamp(CONVERSATION_TTL_DAYS)
                }
            )

            logger.info(f"Created conversation: {conversation_id}")
            return conversation_id

        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a conversation by ID

        Args:
            conversation_id: Conversation identifier

        Returns:
            Conversation data or None
        """
        try:
            response = self.table.get_item(
                Key={'conversation_id': conversation_id}
            )

            conversation = response.get('Item')

            # Decrypt if encryption manager is available
            if conversation and self.encryption_manager:
                for msg in conversation.get('messages', []):
                    msg['content'] = self.encryption_manager.decrypt(msg['content'])

            return conversation

        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            return None

    def add_message(self, conversation_id: str, message: Dict[str, str]) -> bool:
        """
        Add a message to an existing conversation

        Args:
            conversation_id: Conversation identifier
            message: Message dictionary

        Returns:
            Success boolean
        """
        try:
            # Encrypt if encryption manager is available
            encrypted_content = message['content']
            if self.encryption_manager:
                encrypted_content = self.encryption_manager.encrypt(message['content'])

            self.table.update_item(
                Key={'conversation_id': conversation_id},
                UpdateExpression='SET messages = list_append(messages, :msg), updated_at = :timestamp',
                ExpressionAttributeValues={
                    ':msg': [{
                        'role': message['role'],
                        'content': encrypted_content,
                        'timestamp': datetime.utcnow().isoformat()
                    }],
                    ':timestamp': datetime.utcnow().isoformat()
                }
            )

            logger.info(f"Added message to conversation: {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return False

    def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation history (last N messages)

        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages to return

        Returns:
            List of messages
        """
        conversation = self.get_conversation(conversation_id)

        if not conversation:
            return []

        messages = conversation.get('messages', [])

        # Return last N messages
        return messages[-limit:] if len(messages) > limit else messages
