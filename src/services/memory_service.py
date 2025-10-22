"""
Memory Service for managing conversations and memories
"""
import json
import boto3
from typing import List, Optional, Dict
from decimal import Decimal
from ..models import Conversation, Message, Memory
from ..utils import get_logger, config, generate_id, get_timestamp, get_ttl
from .encryption import EncryptionService

logger = get_logger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder for DynamoDB Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class MemoryService:
    """Handles short-term and long-term memory storage"""

    def __init__(self):
        """Initialize memory service"""
        self.dynamodb = boto3.resource('dynamodb', region_name=config.AWS_REGION)
        self.s3_client = boto3.client('s3', region_name=config.AWS_REGION)
        self.conversations_table = self.dynamodb.Table(config.CONVERSATIONS_TABLE)
        self.memories_table = self.dynamodb.Table(config.MEMORIES_TABLE)
        self.encryption = EncryptionService()

    def save_message(
        self,
        conversation_id: str,
        message: Message,
        encrypt: bool = True
    ) -> None:
        """
        Save a message to short-term memory (DynamoDB)

        Args:
            conversation_id: Conversation identifier
            message: Message to save
            encrypt: Whether to encrypt the content
        """
        try:
            content = message.content
            if encrypt:
                content = self.encryption.encrypt(content)

            item = {
                'conversation_id': conversation_id,
                'timestamp': message.timestamp,
                'message_id': message.message_id,
                'role': message.role,
                'content': content,
                'encrypted': encrypt,
                'ttl': get_ttl(config.SHORT_TERM_RETENTION_DAYS)
            }

            if message.metadata:
                item['metadata'] = message.metadata

            self.conversations_table.put_item(Item=item)
            logger.info(f"Saved message {message.message_id} to conversation {conversation_id}")

        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}")
            raise

    def get_conversation(
        self,
        conversation_id: str,
        limit: int = 50,
        decrypt: bool = True
    ) -> Conversation:
        """
        Retrieve a conversation from short-term memory

        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages to retrieve
            decrypt: Whether to decrypt encrypted content

        Returns:
            Conversation object with messages
        """
        try:
            response = self.conversations_table.query(
                KeyConditionExpression='conversation_id = :cid',
                ExpressionAttributeValues={':cid': conversation_id},
                Limit=limit,
                ScanIndexForward=False  # Get most recent first
            )

            items = response.get('Items', [])
            messages = []

            for item in reversed(items):  # Reverse to chronological order
                content = item['content']

                # Decrypt if needed
                if item.get('encrypted', False) and decrypt:
                    try:
                        content = self.encryption.decrypt(content)
                    except Exception as e:
                        logger.error(f"Failed to decrypt message: {str(e)}")

                message = Message(
                    role=item['role'],
                    content=content,
                    timestamp=int(item['timestamp']),
                    message_id=item['message_id'],
                    metadata=item.get('metadata')
                )
                messages.append(message)

            conversation = Conversation(
                conversation_id=conversation_id,
                messages=messages,
                created_at=messages[0].timestamp if messages else 0,
                updated_at=messages[-1].timestamp if messages else 0
            )

            logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
            return conversation

        except Exception as e:
            logger.error(f"Failed to get conversation: {str(e)}")
            # Return empty conversation on error
            return Conversation(conversation_id=conversation_id)

    def save_memory(
        self,
        memory: Memory,
        save_to_s3: bool = True
    ) -> None:
        """
        Save a memory to long-term storage

        Args:
            memory: Memory object to save
            save_to_s3: Whether to save full content to S3
        """
        try:
            # Save to DynamoDB
            item = memory.to_dynamodb_item()
            item['ttl'] = get_ttl(config.LONG_TERM_RETENTION_DAYS)

            self.memories_table.put_item(Item=item)

            # Save to S3 if requested
            if save_to_s3:
                s3_key = f"memories/{memory.memory_id}.json"
                content = json.dumps(memory.to_dict(), cls=DecimalEncoder)

                # Encrypt before saving to S3
                encrypted_content = self.encryption.encrypt(content)

                self.s3_client.put_object(
                    Bucket=config.MEMORY_BUCKET,
                    Key=s3_key,
                    Body=encrypted_content.encode('utf-8'),
                    ContentType='application/json'
                )

                # Update DynamoDB with S3 key
                self.memories_table.update_item(
                    Key={'memory_id': memory.memory_id},
                    UpdateExpression='SET s3_key = :s3_key',
                    ExpressionAttributeValues={':s3_key': s3_key}
                )

            logger.info(f"Saved memory {memory.memory_id}")

        except Exception as e:
            logger.error(f"Failed to save memory: {str(e)}")
            raise

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a memory from storage

        Args:
            memory_id: Memory identifier

        Returns:
            Memory object or None if not found
        """
        try:
            response = self.memories_table.get_item(
                Key={'memory_id': memory_id}
            )

            if 'Item' not in response:
                return None

            item = response['Item']

            # If full content is in S3, retrieve it
            if 's3_key' in item:
                s3_response = self.s3_client.get_object(
                    Bucket=config.MEMORY_BUCKET,
                    Key=item['s3_key']
                )
                encrypted_content = s3_response['Body'].read().decode('utf-8')
                content = self.encryption.decrypt(encrypted_content)
                full_data = json.loads(content)

                # Merge with DynamoDB metadata
                item.update(full_data)

            memory = Memory.from_dict(dict(item))
            logger.info(f"Retrieved memory {memory_id}")
            return memory

        except Exception as e:
            logger.error(f"Failed to get memory: {str(e)}")
            return None

    def list_memories(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Memory]:
        """
        List memories, optionally filtered by category

        Args:
            category: Optional category filter
            limit: Maximum number of memories to return

        Returns:
            List of Memory objects
        """
        try:
            if category:
                response = self.memories_table.query(
                    IndexName='category-created_at-index',
                    KeyConditionExpression='category = :cat',
                    ExpressionAttributeValues={':cat': category},
                    Limit=limit,
                    ScanIndexForward=False
                )
            else:
                response = self.memories_table.scan(Limit=limit)

            items = response.get('Items', [])
            memories = [Memory.from_dict(dict(item)) for item in items]

            logger.info(f"Listed {len(memories)} memories")
            return memories

        except Exception as e:
            logger.error(f"Failed to list memories: {str(e)}")
            return []
