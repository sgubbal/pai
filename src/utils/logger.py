"""
Logging utility for PAI Agent
"""
import logging
import os
import json
from datetime import datetime

# Configure logging level from environment
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Only add handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_event(logger: logging.Logger, event_type: str, data: dict):
    """
    Log structured event data

    Args:
        logger: Logger instance
        event_type: Type of event (e.g., 'API_CALL', 'MEMORY_SAVE')
        data: Event data dictionary
    """
    event = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'data': data
    }
    logger.info(json.dumps(event))


def log_error(logger: logging.Logger, error: Exception, context: dict = None):
    """
    Log error with context

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context data
    """
    error_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context or {}
    }
    logger.error(json.dumps(error_data))
