"""
Search Lambda Handler - Semantic search endpoint
"""
import json
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.services import AIService, VectorService
from src.utils import get_logger

logger = get_logger(__name__)


def lambda_handler(event, context):
    """
    Handle semantic search requests

    Expected event body:
    {
        "query": "Search query text",
        "limit": 10,  # optional, default 10
        "category": "optional-category",  # optional
        "min_score": 0.5  # optional, default 0.5
    }
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        limit = body.get('limit', 10)
        category = body.get('category')
        min_score = body.get('min_score', 0.5)

        if not query:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Query is required'})
            }

        logger.info(f"Processing search query: {query[:50]}...")

        # Initialize services
        ai_service = AIService()
        vector_service = VectorService()

        # Generate query embedding
        query_embedding = ai_service.generate_embedding(query)

        # Search for similar memories
        results = vector_service.search(
            query_embedding=query_embedding,
            limit=limit,
            category=category,
            min_score=min_score
        )

        # Return results
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'query': query,
                'count': len(results),
                'results': [r.to_dict() for r in results]
            })
        }

    except Exception as e:
        logger.error(f"Search handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
