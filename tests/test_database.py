"""Tests for database connector."""

from unittest.mock import MagicMock, patch

from src.database.db_connector import DatabaseConnector


@patch("src.database.db_connector.pymysql")
def test_get_connection(mock_pymysql):
    mock_conn = MagicMock()
    mock_pymysql.connect.return_value = mock_conn

    with DatabaseConnector.get_connection() as conn:
        assert conn == mock_conn

    mock_conn.close.assert_called_once()


@patch("src.database.db_connector.pymysql")
def test_execute_query(mock_pymysql):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = None

    mock_pymysql.connect.return_value = mock_conn

    results = DatabaseConnector.execute_query("SELECT * FROM test")

    assert len(results) == 1
    assert results[0]["name"] == "test"
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test")


@patch("src.database.db_connector.pymysql")
def test_test_connection_success(mock_pymysql):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = None

    mock_pymysql.connect.return_value = mock_conn

    result = DatabaseConnector.test_connection()

    assert result is True
    mock_cursor.execute.assert_called_once_with("SELECT 1")


@patch("src.database.db_connector.pymysql")
def test_test_connection_failure(mock_pymysql):
    mock_pymysql.connect.side_effect = Exception("Connection failed")

    result = DatabaseConnector.test_connection()

    assert result is False
