"""
Amazon Bedrock client for LLM interactions
"""
import json
import boto3
import logging
from typing import List, Dict, Any
from src.shared.constants import BEDROCK_MODEL_ID, BEDROCK_REGION, MAX_TOKENS, TEMPERATURE

logger = logging.getLogger()
bedrock_runtime = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)


class BedrockClient:
    """
    Client for interacting with Amazon Bedrock
    """

    def __init__(self, model_id: str = BEDROCK_MODEL_ID):
        """
        Initialize Bedrock client

        Args:
            model_id: Bedrock model identifier
        """
        self.model_id = model_id

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE
    ) -> Dict[str, Any]:
        """
        Generate a response from Bedrock

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Prepare request body for Claude models
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            # Add system prompt if provided
            if system_prompt:
                request_body["system"] = system_prompt

            # Invoke Bedrock model
            response = bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json',
                accept='application/json'
            )

            # Parse response
            response_body = json.loads(response['body'].read())

            # Extract message content
            assistant_message = response_body.get('content', [{}])[0].get('text', '')

            return {
                "message": assistant_message,
                "stop_reason": response_body.get('stop_reason'),
                "usage": response_body.get('usage', {}),
                "model": self.model_id
            }

        except Exception as e:
            logger.error(f"Bedrock invocation error: {str(e)}")
            raise

    def format_conversation(self, conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Format conversation history for Bedrock API

        Args:
            conversation_history: List of messages

        Returns:
            Formatted messages list
        """
        formatted_messages = []

        for msg in conversation_history:
            if msg.get('role') in ['user', 'assistant']:
                formatted_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })

        return formatted_messages
