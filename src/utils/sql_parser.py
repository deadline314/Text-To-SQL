"""SQL parsing and validation utilities."""

import re

import sqlparse


class SQLParser:
    """SQL parser and validator for Text-to-SQL output."""

    @staticmethod
    def extract_sql(text: str) -> str:
        """
        Extract SQL statement from generated text.

        Args:
            text: Generated text that may contain SQL

        Returns:
            Extracted SQL statement
        """
        text = text.strip()

        sql_block_pattern = r"```sql\s*(.*?)\s*```"
        match = re.search(sql_block_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        code_block_pattern = r"```\s*(.*?)\s*```"
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]
        for keyword in sql_keywords:
            if keyword in text.upper():
                lines = text.split("\n")
                sql_lines = []
                in_sql = False

                for line in lines:
                    if any(kw in line.upper() for kw in sql_keywords):
                        in_sql = True

                    if in_sql:
                        sql_lines.append(line)

                        if line.strip().endswith(";"):
                            break

                return "\n".join(sql_lines).strip()

        return text

    @staticmethod
    def validate_sql(sql: str) -> bool:
        """
        Validate if the string is a valid SQL statement.

        Args:
            sql: SQL statement to validate

        Returns:
            True if valid SQL, False otherwise
        """
        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                return False

            statement = parsed[0]
            stmt_type = statement.get_type()

            if stmt_type is None:
                return False

            valid_types = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]
            return stmt_type.upper() in valid_types

        except Exception:
            return False

    @staticmethod
    def format_sql(sql: str) -> str:
        """
        Format SQL statement for better readability.

        Args:
            sql: SQL statement to format

        Returns:
            Formatted SQL statement
        """
        return sqlparse.format(sql, reindent=True, keyword_case="upper")

    @staticmethod
    def clean_sql(sql: str) -> str:
        """
        Clean and extract pure SQL from text.

        Args:
            sql: Raw SQL text

        Returns:
            Cleaned SQL statement
        """
        extracted = SQLParser.extract_sql(sql)
        if SQLParser.validate_sql(extracted):
            return SQLParser.format_sql(extracted)
        return extracted
