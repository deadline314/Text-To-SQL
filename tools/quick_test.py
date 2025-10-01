"""Quick test script for SQL generation without user interaction."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import FULL_SCHEMA
from src.models.model_factory import create_model, parse_provider_from_arg
from src.services.text_to_sql_service import TextToSQLService

QUICK_TEST_QUERIES = [
    "查詢所有騰訊帳單",
    "查詢 2024-01 帳期的資料",
    "找出成本超過 1000 的記錄",
]


def main() -> None:
    """快速測試 SQL 生成."""
    print("=" * 80)
    print("快速 SQL 生成測試")
    print("=" * 80)

    # 解析命令列參數
    provider = "local"
    model_id = None

    if len(sys.argv) > 1:
        try:
            arg = " ".join(sys.argv[1:])
            provider, model_id = parse_provider_from_arg(arg)
            print(f"\n使用 Provider: {provider}")
            if model_id:
                print(f"模型: {model_id}")
        except ValueError as e:
            print(f"\n參數錯誤: {e}")
            return

    print("\n初始化模型...")
    try:
        model = create_model(provider=provider, model_id=model_id)
        service = TextToSQLService(model)
        print("✓ 模型初始化完成\n")
    except Exception as e:
        print(f"模型初始化失敗: {e}")
        return

    for i, query in enumerate(QUICK_TEST_QUERIES, 1):
        print(f"\n{i}. 問題: {query}")
        print("-" * 80)
        print("生成的 SQL: ", end="", flush=True)

        try:
            full_response = []
            for token in service.convert_stream(FULL_SCHEMA, query):
                print(token, end="", flush=True)
                full_response.append(token)

            print()

            full_sql = "".join(full_response)
            cleaned_sql = service.sql_parser.clean_sql(full_sql)

            if cleaned_sql != full_sql.strip():
                print(f"清理後: {cleaned_sql}")
        except Exception as e:
            print(f"\n✗ 生成失敗: {e}")

    print("\n" + "=" * 80)
    print("測試完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
