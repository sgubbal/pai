"""
Message and Conversation data models
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Message:
    """Represents a single message in a conversation"""

    role: str  # 'user' or 'assistant'
    content: str
    timestamp: int
    message_id: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class Conversation:
    """Represents a conversation with message history"""

    conversation_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: int = 0
    updated_at: int = 0
    metadata: Optional[Dict[str, Any]] = None
    ttl: Optional[int] = None

    def add_message(self, message: Message):
        """Add a message to the conversation"""
        self.messages.append(message)
        self.updated_at = message.timestamp

    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get the most recent N messages"""
        return self.messages[-count:]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['messages'] = [msg.to_dict() for msg in self.messages]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Conversation':
        """Create from dictionary"""
        messages = [Message.from_dict(msg) for msg in data.get('messages', [])]
        conversation_data = {k: v for k, v in data.items() if k != 'messages'}
        return cls(messages=messages, **conversation_data)

    def get_context_window(self, max_messages: int = 20) -> List[Dict[str, str]]:
        """
        Get conversation context for AI model

        Args:
            max_messages: Maximum number of messages to include

        Returns:
            List of message dictionaries for AI model
        """
        recent = self.get_recent_messages(max_messages)
        return [{'role': msg.role, 'content': msg.content} for msg in recent]
