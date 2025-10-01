"""Simple script to list all databases and tables."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.db_connector import DatabaseConnector


def main() -> None:
    """列出所有資料庫和表格."""
    print("=" * 80)
    print("資料庫探索工具")
    print("=" * 80)

    print("\n測試連接...")
    if not DatabaseConnector.test_connection():
        print("✗ 資料庫連接失敗")
        return

    print("✓ 連接成功\n")

    print("=" * 80)
    print("所有資料庫:")
    print("=" * 80)

    try:
        databases = DatabaseConnector.execute_query("SHOW DATABASES")
        for i, db in enumerate(databases, 1):
            db_name = db.get("Database", "")
            print(f"{i}. {db_name}")

        print("\n" + "=" * 80)
        db_choice = input("\n輸入資料庫編號查看表格 (直接按 Enter 跳過): ").strip()

        if db_choice.isdigit():
            idx = int(db_choice) - 1
            if 0 <= idx < len(databases):
                db_name = databases[idx].get("Database", "")
                print(f"\n資料庫: {db_name}")
                print("=" * 80)

                DatabaseConnector.execute_query(f"USE {db_name}")
                tables = DatabaseConnector.execute_query("SHOW TABLES")

                if tables:
                    for i, table in enumerate(tables, 1):
                        table_name = list(table.values())[0]
                        try:
                            count_result = DatabaseConnector.execute_query(
                                f"SELECT COUNT(*) as count FROM {table_name}"
                            )
                            count = count_result[0]["count"]
                            print(f"{i}. {table_name} ({count} 筆資料)")

                            show_sample = input(f"   查看 {table_name} 的範例資料？(y/n): ").strip()
                            if show_sample.lower() == "y":
                                sample = DatabaseConnector.execute_query(
                                    f"SELECT * FROM {table_name} LIMIT 3"
                                )
                                print("\n   前 3 筆資料:")
                                for idx, row in enumerate(sample, 1):
                                    print(f"   {idx}. {row}")
                                print()
                        except Exception as e:
                            print(f"{i}. {table_name} (查詢失敗: {e})")
                else:
                    print("(沒有表格)")

    except Exception as e:
        print(f"✗ 查詢失敗: {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
