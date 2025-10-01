"""Tests for Text-to-SQL prompt templates."""

from src.prompts.text_to_sql_prompt import TextToSQLPrompt


def test_build_prompt_with_schema_and_query():
    schema = "CREATE TABLE users (id INT, name VARCHAR(100));"
    user_query = "查詢所有使用者"

    prompt = TextToSQLPrompt.build_prompt(schema, user_query)

    assert schema in prompt
    assert user_query in prompt
    assert "SQL" in prompt


def test_build_prompt_strips_whitespace():
    schema = "  CREATE TABLE test (id INT);  "
    user_query = "  test query  "

    prompt = TextToSQLPrompt.build_prompt(schema, user_query)

    assert "CREATE TABLE test (id INT);" in prompt
    assert "test query" in prompt
    assert prompt.count("  CREATE TABLE") == 0


def test_get_system_instruction():
    instruction = TextToSQLPrompt.get_system_instruction()

    assert len(instruction) > 0
    assert "SQL" in instruction


def test_get_template():
    template = TextToSQLPrompt.get_template()

    assert "{schema}" in template
    assert "{user_query}" in template
