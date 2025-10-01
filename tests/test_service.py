"""Tests for Text-to-SQL service."""

from unittest.mock import Mock

from src.services.text_to_sql_service import TextToSQLService


def test_service_initialization():
    mock_model = Mock()
    service = TextToSQLService(mock_model)

    assert service.model == mock_model
    assert service.sql_parser is not None


def test_convert_initializes_model():
    mock_model = Mock()
    mock_model.is_initialized.return_value = False
    mock_model.generate.return_value = "SELECT * FROM users;"

    service = TextToSQLService(mock_model)
    schema = "CREATE TABLE users (id INT);"
    query = "Get all users"

    service.convert(schema, query)

    mock_model.initialize.assert_called_once()


def test_convert_generates_sql():
    mock_model = Mock()
    mock_model.is_initialized.return_value = True
    mock_model.generate.return_value = "SELECT * FROM users;"

    service = TextToSQLService(mock_model)
    schema = "CREATE TABLE users (id INT);"
    query = "Get all users"

    result = service.convert(schema, query)

    mock_model.generate.assert_called_once()
    assert "SELECT" in result


def test_convert_with_max_tokens():
    mock_model = Mock()
    mock_model.is_initialized.return_value = True
    mock_model.generate.return_value = "SELECT * FROM users;"

    service = TextToSQLService(mock_model)
    schema = "CREATE TABLE users (id INT);"
    query = "Get all users"

    service.convert(schema, query, max_tokens=256)

    call_args = mock_model.generate.call_args
    assert call_args[0][1] == 256
