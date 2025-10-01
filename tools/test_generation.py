"""Test script for SQL generation functionality."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import FULL_SCHEMA
from src.database.db_connector import DatabaseConnector
from src.models.model_factory import create_model, parse_provider_from_arg
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
        else:
            print("此資料庫沒有表格")
    except Exception as e:
        print(f"✗ 查詢失敗: {e}")
    print("=" * 80)


def test_sql_generation_only(provider: str = "local", model_id: str | None = None) -> None:
    """僅測試 SQL 生成功能（不執行）."""
    print("\n" + "=" * 80)
    print(f"測試 SQL 生成（僅生成，不執行）- Provider: {provider}")
    print("=" * 80)

    print("\n初始化模型 (首次使用需要下載模型，請稍候)...")
    try:
        model = create_model(provider=provider, model_id=model_id)
        service = TextToSQLService(model)
        print("✓ 模型初始化完成\n")
    except Exception as e:
        print(f"\n✗ 模型初始化失敗: {e}")
        return

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'-' * 80}")
        print(f"測試 {i}/{len(TEST_QUERIES)}")
        print(f"問題: {query}")
        print(f"{'-' * 80}")

        try:
            print("生成中...")
            print("\n✓ 生成的 SQL:")
            print("-" * 40)

            full_response = []
            for token in service.convert_stream(FULL_SCHEMA, query):
                print(token, end="", flush=True)
                full_response.append(token)

            print("\n" + "-" * 40)

            full_sql = "".join(full_response)
            cleaned_sql = service.sql_parser.clean_sql(full_sql)

            if cleaned_sql != full_sql.strip():
                print("\n清理後的 SQL:")
                print(cleaned_sql)

        except Exception as e:
            print(f"\n✗ 生成失敗: {e}")

    print("\n" + "=" * 80)
    print("測試完成！")
    print("=" * 80)


def test_sql_generation_with_execution(
    provider: str = "local", model_id: str | None = None
) -> None:
    """測試 SQL 生成並執行（完整流程）."""
    print("\n" + "=" * 80)
    print(f"測試 SQL 生成並執行（完整流程）- Provider: {provider}")
    print("=" * 80)

    print("\n初始化模型 (首次使用需要下載模型，請稍候)...")
    try:
        model = create_model(provider=provider, model_id=model_id)
        service = TextToSQLService(model)
        print("✓ 模型初始化完成\n")
    except Exception as e:
        print(f"\n✗ 模型初始化失敗: {e}")
        return

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'-' * 80}")
        print(f"測試 {i}/{len(TEST_QUERIES)}")
        print(f"問題: {query}")
        print(f"{'-' * 80}")

        try:
            print("生成中...")
            print("\n生成的 SQL:")
            print("-" * 40)

            full_response = []
            for token in service.convert_stream(FULL_SCHEMA, query):
                print(token, end="", flush=True)
                full_response.append(token)

            print("\n" + "-" * 40)

            full_sql = "".join(full_response)
            sql = service.sql_parser.clean_sql(full_sql)

            if sql != full_sql.strip():
                print("\n清理後的 SQL:")
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


def interactive_query_generation(provider: str = "local", model_id: str | None = None) -> None:
    """即時查詢生成（連續輸入，只生成不執行）."""
    print("\n" + "=" * 80)
    print(f"即時查詢生成 - Provider: {provider}")
    print("=" * 80)
    print("輸入您的問題，系統會生成對應的 SQL（不執行）")
    print("輸入 'quit', 'q', 或 'exit' 返回主選單")
    print("=" * 80)

    model = None
    service = None

    try:
        while True:
            query = input("\n問題 (輸入 q 返回): ").strip()

            if query.lower() in ["quit", "q", "exit", ""]:
                if model:
                    print("清理模型資源...")
                    model.cleanup()
                print("返回主選單")
                break

            try:
                if not query:
                    continue

                if model is None:
                    print("初始化模型（僅需一次）...")
                    model = create_model(provider=provider, model_id=model_id)
                    service = TextToSQLService(model)
                    print("✓ 模型已載入\n")

                print("生成中...")
                print("-" * 80)

                full_response = []
                for token in service.convert_stream(FULL_SCHEMA, query):
                    print(token, end="", flush=True)
                    full_response.append(token)

                print("\n" + "-" * 80)

                full_sql = "".join(full_response)
                cleaned_sql = service.sql_parser.clean_sql(full_sql)

                if cleaned_sql != full_sql.strip():
                    print("\n清理後的 SQL:")
                    print(cleaned_sql)

            except Exception as e:
                print(f"\n✗ 生成失敗: {e}")

    except KeyboardInterrupt:
        if model:
            model.cleanup()
        print("\n\n已中斷，返回主選單")


def print_usage() -> None:
    """顯示使用說明."""
    print("\n" + "=" * 80)
    print("使用方式:")
    print("=" * 80)
    print("基本使用（本地模型）:")
    print("  python tools/test_generation.py")
    print("  make gen")
    print()
    print("使用 AWS Bedrock（預設模型）:")
    print("  python tools/test_generation.py -bedrock")
    print("  make gen ARGS=-bedrock")
    print()
    print("使用 AWS Bedrock（指定模型）:")
    print("  python tools/test_generation.py -bedrock us.anthropic.claude-sonnet-4-v1:0")
    print('  make gen ARGS="-bedrock us.anthropic.claude-sonnet-4-v1:0"')
    print()
    print("使用 Google GenAI（預設模型）:")
    print("  python tools/test_generation.py -genai")
    print("  make gen ARGS=-genai")
    print()
    print("使用 Google GenAI（指定模型）:")
    print("  python tools/test_generation.py -genai gemini-2.5-flash")
    print('  make gen ARGS="-genai gemini-2.5-flash"')
    print("=" * 80)


def main() -> None:
    """主函數."""
    # 解析命令列參數
    provider = "local"
    model_id = None

    if len(sys.argv) > 1:
        try:
            arg = " ".join(sys.argv[1:])
            provider, model_id = parse_provider_from_arg(arg)
            print(f"\n✓ 使用 Provider: {provider}")
            if model_id:
                print(f"✓ 模型: {model_id}")
        except ValueError as e:
            print(f"\n✗ 參數錯誤: {e}")
            print_usage()
            return

    while True:
        print("\n選擇操作:")
        print("1. 查看可用的資料庫")
        print("2. 查看指定資料庫的表格")
        print("3. 測試 SQL 生成（不執行）")
        print("4. 測試 SQL 生成並執行")
        print("5. 即時查詢生成（輸入文字生成 SQL）")
        print("6. 顯示使用說明")
        print("7. 退出")

        choice = input("\n請輸入選項 (1-7 或 q 退出): ").strip()

        if choice.lower() in ["q", "quit", "exit"]:
            print("\n再見！")
            break

        if choice == "1":
            show_available_databases()
        elif choice == "2":
            db_name = input("請輸入資料庫名稱: ").strip()
            if db_name:
                show_tables_in_database(db_name)
        elif choice == "3":
            test_sql_generation_only(provider=provider, model_id=model_id)
        elif choice == "4":
            test_sql_generation_with_execution(provider=provider, model_id=model_id)
        elif choice == "5":
            interactive_query_generation(provider=provider, model_id=model_id)
        elif choice == "6":
            print_usage()
        elif choice == "7":
            print("\n再見！")
            break
        else:
            print("無效的選項，請重試。")


if __name__ == "__main__":
    main()
