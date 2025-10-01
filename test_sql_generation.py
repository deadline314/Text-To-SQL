"""Test script for SQL generation functionality."""

from config import FULL_SCHEMA
from src.database.db_connector import DatabaseConnector
from src.models.huggingface_model import HuggingFaceModel
from src.services.text_to_sql_service import TextToSQLService

TEST_QUERIES = [
    "查詢10筆騰訊帳單",
    "查詢 2025-01 帳期的資料",
    "找出成本超過 1000 的記錄",
    "統計一個月內的每個帳期的總成本",
    "查詢代金券使用最多的前 5 筆記錄",
]


def show_available_databases() -> None:
    """顯示所有可用的資料庫."""
    print("\n" + "=" * 80)
    print("可用的資料庫:")
    print("=" * 80)
    try:
        databases = DatabaseConnector.execute_query("SHOW DATABASES")
        for i, db in enumerate(databases, 1):
            db_name = db.get("Database", "")
            print(f"{i}. {db_name}")
    except Exception as e:
        print(f"✗ 查詢失敗: {e}")
    print("=" * 80)


def show_tables_in_database(database_name: str) -> None:
    """顯示指定資料庫中的表格."""
    print("\n" + "=" * 80)
    print(f"資料庫 '{database_name}' 中的表格:")
    print("=" * 80)
    try:
        DatabaseConnector.execute_query(f"USE {database_name}")
        tables = DatabaseConnector.execute_query("SHOW TABLES")
        if tables:
            for i, table in enumerate(tables, 1):
                table_name = list(table.values())[0]
                print(f"{i}. {table_name}")

                try:
                    count_result = DatabaseConnector.execute_query(
                        f"SELECT COUNT(*) as count FROM {table_name}"
                    )
                    count = count_result[0]["count"]
                    print(f"   (共 {count} 筆資料)")
                except Exception:
                    pass
        else:
            print("(沒有表格)")
    except Exception as e:
        print(f"✗ 查詢失敗: {e}")
    print("=" * 80)


def test_sql_generation_only() -> None:
    """僅測試 SQL 生成功能（不執行）."""
    print("\n" + "=" * 80)
    print("測試 SQL 生成（僅生成，不執行）")
    print("=" * 80)

    print("\n初始化模型 (首次使用需要下載模型，請稍候)...")
    model = HuggingFaceModel(device="cpu")
    service = TextToSQLService(model)
    print("✓ 模型初始化完成\n")

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'-' * 80}")
        print(f"測試 {i}/{len(TEST_QUERIES)}")
        print(f"問題: {query}")
        print(f"{'-' * 80}")

        try:
            print("生成中...")
            sql = service.convert(FULL_SCHEMA, query)

            print("\n✓ 生成的 SQL:")
            print(sql)

        except Exception as e:
            print(f"\n✗ 生成失敗: {e}")

    print("\n" + "=" * 80)
    print("測試完成！")
    print("=" * 80)


def test_sql_generation_with_execution() -> None:
    """測試 SQL 生成並執行（完整流程）."""
    print("\n" + "=" * 80)
    print("測試 SQL 生成並執行（完整流程）")
    print("=" * 80)

    print("\n初始化模型 (首次使用需要下載模型，請稍候)...")
    model = HuggingFaceModel(device="cpu")
    service = TextToSQLService(model)
    print("✓ 模型初始化完成\n")

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'-' * 80}")
        print(f"測試 {i}/{len(TEST_QUERIES)}")
        print(f"問題: {query}")
        print(f"{'-' * 80}")

        try:
            print("生成中...")
            sql = service.convert(FULL_SCHEMA, query)

            print("\n生成的 SQL:")
            print(sql)

            user_input = input("\n是否執行此 SQL？(y/n/s=跳過全部): ").strip().lower()

            if user_input == "s":
                print("跳過剩餘測試")
                break

            if user_input == "y":
                try:
                    results = DatabaseConnector.execute_query(sql)
                    print(f"\n✓ 查詢成功！返回 {len(results)} 筆資料")

                    if results:
                        print("\n前 3 筆資料:")
                        for idx, row in enumerate(results[:3], 1):
                            print(f"{idx}. {row}")
                except Exception as e:
                    print(f"\n✗ 執行失敗: {e}")

        except Exception as e:
            print(f"\n✗ 生成失敗: {e}")

    print("\n" + "=" * 80)
    print("測試完成！")
    print("=" * 80)


def main() -> None:
    """主程式."""
    print("=" * 80)
    print("Text-to-SQL 測試工具")
    print("=" * 80)

    print("\n1. 測試資料庫連接")
    if not DatabaseConnector.test_connection():
        print("✗ 資料庫連接失敗，請先修復連接問題")
        return

    print("✓ 資料庫連接成功")

    while True:
        print("\n選擇操作:")
        print("1. 查看所有資料庫")
        print("2. 查看指定資料庫的表格")
        print("3. 測試 SQL 生成（僅生成）")
        print("4. 測試 SQL 生成並執行（完整流程）")
        print("5. 自訂查詢測試")
        print("6. 退出")

        choice = input("\n請輸入選項 (1-6): ").strip()

        if choice == "1":
            show_available_databases()

        elif choice == "2":
            db_name = input("請輸入資料庫名稱: ").strip()
            if db_name:
                show_tables_in_database(db_name)

        elif choice == "3":
            test_sql_generation_only()

        elif choice == "4":
            test_sql_generation_with_execution()

        elif choice == "5":
            custom_query = input("\n請輸入您的查詢問題: ").strip()
            if custom_query:
                print("\n初始化模型...")
                model = HuggingFaceModel(device="cpu")
                service = TextToSQLService(model)

                print("生成中...")
                sql = service.convert(FULL_SCHEMA, custom_query)

                print("\n生成的 SQL:")
                print(sql)

                execute = input("\n是否執行？(y/n): ").strip().lower()
                if execute == "y":
                    try:
                        results = DatabaseConnector.execute_query(sql)
                        print(f"\n✓ 查詢成功！返回 {len(results)} 筆資料")
                        if results:
                            print("\n前 5 筆資料:")
                            for idx, row in enumerate(results[:5], 1):
                                print(f"{idx}. {row}")
                    except Exception as e:
                        print(f"\n✗ 執行失敗: {e}")

        elif choice == "6":
            print("\n再見！")
            break

        else:
            print("\n無效的選項，請重新選擇")


if __name__ == "__main__":
    main()
