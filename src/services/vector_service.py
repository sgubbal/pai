"""
Vector Service for semantic search using OpenSearch Serverless
"""
import json
from typing import List, Dict, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from ..models import Memory, SearchResult
from ..utils import get_logger, config

logger = get_logger(__name__)


class VectorService:
    """Handles vector storage and semantic search"""

    def __init__(self):
        """Initialize vector service"""
        self.index_name = config.OPENSEARCH_INDEX_NAME

        # Skip initialization if no endpoint configured
        if not config.VECTOR_SEARCH_ENDPOINT:
            logger.warning("Vector search endpoint not configured")
            self.client = None
            return

        # Get AWS credentials for signing requests
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            config.AWS_REGION,
            'aoss',
            session_token=credentials.token
        )

        # Extract host from endpoint URL
        host = config.VECTOR_SEARCH_ENDPOINT.replace('https://', '').replace('http://', '')

        # Initialize OpenSearch client
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30
        )

    def create_index(self, dimension: int = None) -> bool:
        """
        Create the vector search index

        Args:
            dimension: Vector dimension (defaults to config)

        Returns:
            True if successful
        """
        if not self.client:
            logger.error("Vector search client not initialized")
            return False

        try:
            dimension = dimension or config.VECTOR_DIMENSION

            index_body = {
                'settings': {
                    'index': {
                        'knn': True,
                        'knn.algo_param.ef_search': 512
                    }
                },
                'mappings': {
                    'properties': {
                        'memory_id': {'type': 'keyword'},
                        'content': {'type': 'text'},
                        'category': {'type': 'keyword'},
                        'created_at': {'type': 'long'},
                        'metadata': {'type': 'object'},
                        'embedding': {
                            'type': 'knn_vector',
                            'dimension': dimension,
                            'method': {
                                'name': 'hnsw',
                                'space_type': 'cosinesimil',
                                'engine': 'nmslib',
                                'parameters': {
                                    'ef_construction': 512,
                                    'm': 16
                                }
                            }
                        }
                    }
                }
            }

            if self.client.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} already exists")
                return True

            self.client.indices.create(index=self.index_name, body=index_body)
            logger.info(f"Created index {self.index_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            return False

    def index_memory(self, memory: Memory) -> bool:
        """
        Index a memory for vector search

        Args:
            memory: Memory object with embedding

        Returns:
            True if successful
        """
        if not self.client:
            logger.warning("Vector search client not initialized, skipping indexing")
            return False

        try:
            if not memory.embedding:
                logger.error("Memory has no embedding")
                return False

            document = memory.to_vector_document()

            self.client.index(
                index=self.index_name,
                id=memory.memory_id,
                body=document,
                refresh=True
            )

            logger.info(f"Indexed memory {memory.memory_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to index memory: {str(e)}")
            return False

    def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        category: Optional[str] = None,
        min_score: float = 0.5
    ) -> List[SearchResult]:
        """
        Search for similar memories using vector similarity

        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            category: Optional category filter
            min_score: Minimum similarity score (0-1)

        Returns:
            List of SearchResult objects
        """
        if not self.client:
            logger.warning("Vector search client not initialized")
            return []

        try:
            # Build query
            knn_query = {
                'size': limit,
                'query': {
                    'knn': {
                        'embedding': {
                            'vector': query_embedding,
                            'k': limit
                        }
                    }
                }
            }

            # Add category filter if specified
            if category:
                knn_query['query'] = {
                    'bool': {
                        'must': [knn_query['query']],
                        'filter': [
                            {'term': {'category': category}}
                        ]
                    }
                }

            # Execute search
            response = self.client.search(
                index=self.index_name,
                body=knn_query
            )

            # Parse results
            results = []
            for rank, hit in enumerate(response['hits']['hits']):
                score = hit['_score']

                # Filter by minimum score
                if score < min_score:
                    continue

                source = hit['_source']

                memory = Memory(
                    memory_id=source['memory_id'],
                    content=source['content'],
                    category=source.get('category', 'general'),
                    created_at=source.get('created_at', 0),
                    metadata=source.get('metadata')
                )

                result = SearchResult(
                    memory=memory,
                    score=score,
                    rank=rank + 1
                )
                results.append(result)

            logger.info(f"Found {len(results)} search results")
            return results

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory from the vector index

        Args:
            memory_id: Memory identifier

        Returns:
            True if successful
        """
        if not self.client:
            return False

        try:
            self.client.delete(
                index=self.index_name,
                id=memory_id
            )

            logger.info(f"Deleted memory {memory_id} from index")
            return True

        except Exception as e:
            logger.error(f"Failed to delete memory: {str(e)}")
            return False
