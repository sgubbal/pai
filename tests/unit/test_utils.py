"""
Unit tests for shared utilities
"""
import pytest
from src.shared.utils import create_response, create_error_response, validate_required_fields


def test_create_response():
    """Test create_response function"""
    response = create_response(200, {"message": "success"})

    assert response["statusCode"] == 200
    assert "body" in response
    assert "headers" in response
    assert response["headers"]["Content-Type"] == "application/json"


def test_create_error_response():
    """Test create_error_response function"""
    response = create_error_response(400, "Bad request")

    assert response["statusCode"] == 400
    assert '"error": "Bad request"' in response["body"]


def test_validate_required_fields_success():
    """Test validate_required_fields with valid data"""
    data = {"field1": "value1", "field2": "value2"}
    is_valid, error_msg = validate_required_fields(data, ["field1", "field2"])

    assert is_valid is True
    assert error_msg == ""


def test_validate_required_fields_missing():
    """Test validate_required_fields with missing fields"""
    data = {"field1": "value1"}
    is_valid, error_msg = validate_required_fields(data, ["field1", "field2"])

    assert is_valid is False
    assert "Missing required fields" in error_msg
    assert "field2" in error_msg
