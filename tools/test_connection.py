"""Simple script to test database connection."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.db_connector import DatabaseConnector


def main() -> None:
    """Test database connection."""
    print("=" * 80)
    print("測試資料庫連接")
    print("=" * 80)
    print()

    print("測試連接...")
    if DatabaseConnector.test_connection():
        print("✓ 資料庫連接成功！")
        print()

        print("執行測試查詢...")
        try:
            result = DatabaseConnector.execute_query("SELECT DATABASE(), VERSION()")
            print(f"  Database: {result[0].get('DATABASE()', 'N/A')}")
            print(f"  Version: {result[0].get('VERSION()', 'N/A')}")
            print()
            print("✓ 查詢執行成功！")
        except Exception as e:
            print(f"✗ 查詢失敗: {e}")
    else:
        print("✗ 資料庫連接失敗")
        print()
        print("請檢查:")
        print("  1. 網路連接")
        print("  2. SSL 證書是否已解壓 (執行 'make setup-certs')")
        print("  3. 資料庫名稱是否已設定 (在 .env 檔案中設定 DB_NAME)")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
