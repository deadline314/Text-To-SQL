"""Text-to-SQL conversion service."""

from collections.abc import Generator

from src.interfaces.language_model import ILanguageModel
from src.prompts.text_to_sql_prompt import TextToSQLPrompt
from src.utils.sql_parser import SQLParser


class TextToSQLService:
    """Service for converting natural language to SQL queries."""

    def __init__(self, model: ILanguageModel):
        """
        Initialize the Text-to-SQL service.

        Args:
            model: Language model implementation
        """
        self.model = model
        self.sql_parser = SQLParser()

    def convert(self, schema: str, user_query: str, max_tokens: int = 512) -> str:
        """
        Convert natural language query to SQL.

        Args:
            schema: Database schema description
            user_query: User's natural language query
            max_tokens: Maximum tokens to generate

        Returns:
            Generated SQL query
        """
        if not self.model.is_initialized():
            self.model.initialize()

        prompt = TextToSQLPrompt.build_prompt(schema, user_query)
        raw_output = self.model.generate(prompt, max_tokens)
        sql = self.sql_parser.clean_sql(raw_output)

        return sql

    def convert_stream(
        self, schema: str, user_query: str, max_tokens: int = 1000
    ) -> Generator[str, None, None]:
        """
        Convert natural language query to SQL with streaming output.

        Args:
            schema: Database schema description
            user_query: User's natural language query
            max_tokens: Maximum tokens to generate

        Yields:
            Generated text tokens
        """
        if not self.model.is_initialized():
            self.model.initialize()

        prompt = TextToSQLPrompt.build_prompt(schema, user_query)

        if hasattr(self.model, "generate_stream"):
            yield from self.model.generate_stream(prompt, max_tokens)
        else:
            raw_output = self.model.generate(prompt, max_tokens)
            yield raw_output
