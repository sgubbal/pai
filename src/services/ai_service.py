"""
AI Service for interacting with AWS Bedrock
"""
import json
import boto3
from typing import List, Dict, Optional
from ..utils import get_logger, config

logger = get_logger(__name__)


class AIService:
    """Handles interactions with AWS Bedrock AI models"""

    def __init__(self, model_id: Optional[str] = None, embedding_model_id: Optional[str] = None):
        """
        Initialize AI service

        Args:
            model_id: Bedrock model ID for chat
            embedding_model_id: Bedrock model ID for embeddings
        """
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=config.AWS_REGION)
        self.model_id = model_id or config.AI_MODEL_ID
        self.embedding_model_id = embedding_model_id or config.EMBEDDING_MODEL_ID

    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048
    ) -> str:
        """
        Send a chat message to the AI model

        Args:
            message: User message
            conversation_history: Previous conversation messages
            system_prompt: System prompt to guide the AI
            max_tokens: Maximum tokens in response

        Returns:
            AI response text
        """
        try:
            # Prepare messages
            messages = conversation_history or []
            messages.append({'role': 'user', 'content': message})

            # Prepare request body based on model
            if 'claude' in self.model_id.lower():
                request_body = {
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': max_tokens,
                    'messages': messages
                }

                if system_prompt:
                    request_body['system'] = system_prompt

            else:
                # Generic format
                request_body = {
                    'messages': messages,
                    'max_tokens': max_tokens
                }

            # Invoke model
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())

            # Extract text based on model response format
            if 'content' in response_body:
                # Claude format
                content = response_body['content']
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get('text', '')
                return str(content)
            elif 'completion' in response_body:
                # Older format
                return response_body['completion']
            else:
                logger.error(f"Unexpected response format: {response_body.keys()}")
                return str(response_body)

        except Exception as e:
            logger.error(f"AI chat failed: {str(e)}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text

        Args:
            text: Text to embed

        Returns:
            Vector embedding as list of floats
        """
        try:
            # Prepare request based on model
            if 'titan' in self.embedding_model_id.lower():
                request_body = {
                    'inputText': text
                }
            else:
                request_body = {
                    'text': text
                }

            # Invoke model
            response = self.bedrock_client.invoke_model(
                modelId=self.embedding_model_id,
                body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())

            # Extract embedding based on model response format
            if 'embedding' in response_body:
                embedding = response_body['embedding']
            elif 'embeddings' in response_body:
                embedding = response_body['embeddings'][0]
            else:
                logger.error(f"Unexpected embedding response format: {response_body.keys()}")
                raise ValueError("Could not extract embedding from response")

            logger.debug(f"Generated embedding of dimension {len(embedding)}")
            return embedding

        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise

    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of vector embeddings
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)

        return embeddings
