"""Database connection and query execution."""

import ssl
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pymysql

from config import DB_CONFIG


class DatabaseConnector:
    """MySQL database connector with SSL support."""

    @staticmethod
    def _prepare_ssl_config() -> dict[str, Any] | None:
        """Prepare SSL configuration if certificates exist."""
        ssl_ca = Path(DB_CONFIG.ssl_ca)
        ssl_cert = Path(DB_CONFIG.ssl_cert)
        ssl_key = Path(DB_CONFIG.ssl_key)

        if not all([ssl_ca.exists(), ssl_cert.exists(), ssl_key.exists()]):
            return None

        return {
            "ca": str(ssl_ca),
            "cert": str(ssl_cert),
            "key": str(ssl_key),
            "check_hostname": False,
            "verify_mode": ssl.CERT_NONE,
        }

    @staticmethod
    @contextmanager
    def get_connection():
        """
        Get database connection with context manager.

        Yields:
            Connection: PyMySQL connection object
        """
        ssl_config = DatabaseConnector._prepare_ssl_config()

        conn_params = {
            "host": DB_CONFIG.host,
            "port": DB_CONFIG.port,
            "user": DB_CONFIG.user,
            "password": DB_CONFIG.password,
            "charset": DB_CONFIG.charset,
            "ssl": ssl_config,
            "cursorclass": pymysql.cursors.DictCursor,
        }

        if DB_CONFIG.database:
            conn_params["database"] = DB_CONFIG.database

        connection = pymysql.connect(**conn_params)

        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def execute_query(sql: str) -> list[dict[str, Any]]:
        """
        Execute SQL query and return results.

        Args:
            sql: SQL query to execute

        Returns:
            List of result rows as dictionaries
        """
        with DatabaseConnector.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                return results

    @staticmethod
    def test_connection() -> bool:
        """
        Test database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with DatabaseConnector.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
