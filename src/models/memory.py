"""
Memory data models for long-term storage
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Memory:
    """Represents a stored memory with vector embedding"""

    memory_id: str
    content: str
    embedding: Optional[List[float]] = None
    category: str = 'general'
    created_at: int = 0
    metadata: Optional[Dict[str, Any]] = None
    ttl: Optional[int] = None
    s3_key: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        # Don't include embedding in standard dict (too large)
        if 'embedding' in data and data['embedding']:
            data['embedding_size'] = len(data['embedding'])
            del data['embedding']
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Memory':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    def to_dynamodb_item(self) -> dict:
        """
        Convert to DynamoDB item format

        Returns:
            Dictionary formatted for DynamoDB
        """
        item = {
            'memory_id': self.memory_id,
            'content': self.content,
            'category': self.category,
            'created_at': self.created_at,
        }

        if self.s3_key:
            item['s3_key'] = self.s3_key

        if self.metadata:
            item['metadata'] = self.metadata

        if self.ttl:
            item['ttl'] = self.ttl

        return item

    def to_vector_document(self) -> dict:
        """
        Convert to OpenSearch vector document format

        Returns:
            Dictionary formatted for OpenSearch
        """
        if not self.embedding:
            raise ValueError("Cannot create vector document without embedding")

        return {
            'memory_id': self.memory_id,
            'content': self.content,
            'embedding': self.embedding,
            'category': self.category,
            'created_at': self.created_at,
            'metadata': self.metadata or {}
        }


@dataclass
class SearchResult:
    """Represents a search result from vector search"""

    memory: Memory
    score: float
    rank: int

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'memory': self.memory.to_dict(),
            'score': self.score,
            'rank': self.rank
        }
