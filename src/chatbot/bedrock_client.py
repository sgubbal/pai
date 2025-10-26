"""
Amazon Bedrock client for LLM interactions
"""
import os
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

    def __init__(self, model_id: str = None):
        """
        Initialize Bedrock client

        Args:
            model_id: Bedrock model identifier (optional, defaults to env var or constant)
        """
        # Allow environment variable to override default model
        if model_id is None:
            model_id = os.environ.get('BEDROCK_MODEL_ID', BEDROCK_MODEL_ID)
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
            # Determine model provider
            is_anthropic = 'anthropic' in self.model_id.lower()
            is_amazon = 'amazon' in self.model_id.lower()

            # Prepare request body based on model provider
            if is_anthropic:
                # Claude models format
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": messages
                }
                if system_prompt:
                    request_body["system"] = system_prompt

            elif is_amazon:
                # Amazon Nova/Titan models format - content must be array
                formatted_messages = []
                for msg in messages:
                    formatted_msg = {"role": msg["role"]}
                    # Convert content to array format if it's a string
                    if isinstance(msg.get("content"), str):
                        formatted_msg["content"] = [{"text": msg["content"]}]
                    else:
                        formatted_msg["content"] = msg["content"]
                    formatted_messages.append(formatted_msg)

                request_body = {
                    "messages": formatted_messages,
                    "inferenceConfig": {
                        "maxTokens": max_tokens,
                        "temperature": temperature
                    }
                }
                if system_prompt:
                    request_body["system"] = [{"text": system_prompt}]
            else:
                # Default to Claude format
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": messages
                }
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

            # Log response structure for debugging
            logger.info(f"Bedrock response keys: {list(response_body.keys())}")

            # Extract message content (works for both Claude and Amazon models)
            if 'content' in response_body and isinstance(response_body['content'], list):
                assistant_message = response_body['content'][0].get('text', '')
            elif 'output' in response_body:
                # Some Amazon models use 'output'
                assistant_message = response_body['output'].get('message', {}).get('content', [{}])[0].get('text', '')
            else:
                assistant_message = str(response_body)

            # Extract usage information (different formats for different models)
            usage_raw = response_body.get('usage', {})

            # Normalize to snake_case for consistency
            usage = {
                "input_tokens": usage_raw.get('input_tokens') or usage_raw.get('inputTokens', 0),
                "output_tokens": usage_raw.get('output_tokens') or usage_raw.get('outputTokens', 0)
            }

            return {
                "message": assistant_message,
                "stop_reason": response_body.get('stop_reason') or response_body.get('stopReason'),
                "usage": usage,
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
