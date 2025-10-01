"""Tests for SQL parser utilities."""

from src.utils.sql_parser import SQLParser


def test_extract_sql_from_code_block():
    text = "```sql\nSELECT * FROM users;\n```"
    result = SQLParser.extract_sql(text)
    assert result == "SELECT * FROM users;"


def test_extract_sql_from_plain_text():
    text = "Here is the query: SELECT * FROM users WHERE age > 18;"
    result = SQLParser.extract_sql(text)
    assert "SELECT * FROM users WHERE age > 18;" in result


def test_extract_sql_with_semicolon():
    text = "SELECT id, name FROM users;\nSome other text"
    result = SQLParser.extract_sql(text)
    assert "SELECT id, name FROM users;" in result


def test_validate_sql_valid_select():
    sql = "SELECT * FROM users;"
    assert SQLParser.validate_sql(sql) is True


def test_validate_sql_valid_insert():
    sql = "INSERT INTO users (name) VALUES ('test');"
    assert SQLParser.validate_sql(sql) is True


def test_validate_sql_invalid():
    sql = "This is not SQL"
    assert SQLParser.validate_sql(sql) is False


def test_format_sql():
    sql = "select * from users where age>18"
    formatted = SQLParser.format_sql(sql)
    assert "SELECT" in formatted
    assert "FROM" in formatted


def test_clean_sql():
    text = "```sql\nselect * from users;\n```"
    cleaned = SQLParser.clean_sql(text)
    assert "SELECT" in cleaned
    assert "FROM" in cleaned
