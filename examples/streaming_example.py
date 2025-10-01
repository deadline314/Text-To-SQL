"""Streaming example for Text-to-SQL system."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import FULL_SCHEMA
from src.models.huggingface_model import HuggingFaceModel
from src.services.text_to_sql_service import TextToSQLService


def example_streaming_generation():
    """示範 Streaming 生成功能."""
    print("=" * 80)
    print("Streaming SQL 生成範例")
    print("=" * 80)
    print()

    print("初始化模型...")
    model = HuggingFaceModel(device="cpu")
    service = TextToSQLService(model)
    print("✓ 模型已載入\n")

    queries = [
        "查詢所有騰訊帳單",
        "找出成本超過 1000 的記錄",
        "統計每個帳期的總成本",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{i}. 查詢: {query}")
        print("-" * 80)
        print("生成中: ", end="", flush=True)

        full_response = []
        for token in service.convert_stream(FULL_SCHEMA, query):
            print(token, end="", flush=True)
            full_response.append(token)

        print("\n" + "-" * 80)

        # 清理和格式化
        full_sql = "".join(full_response)
        cleaned_sql = service.sql_parser.clean_sql(full_sql)

        if cleaned_sql != full_sql.strip():
            print("\n清理後的 SQL:")
            print(cleaned_sql)
            print()

    print("\n" + "=" * 80)
    print("範例完成！")


def example_non_streaming_comparison():
    """比較 Streaming 和非 Streaming 模式."""
    print("\n" + "=" * 80)
    print("比較模式")
    print("=" * 80)
    print()

    model = HuggingFaceModel(device="cpu")
    service = TextToSQLService(model)

    query = "查詢 2025-01 帳期的資料"

    print("1. 非 Streaming 模式:")
    print("-" * 80)
    sql = service.convert(FULL_SCHEMA, query)
    print(sql)
    print("-" * 80)
    print()

    print("2. Streaming 模式:")
    print("-" * 80)
    for token in service.convert_stream(FULL_SCHEMA, query):
        print(token, end="", flush=True)
    print("\n" + "-" * 80)


if __name__ == "__main__":
    print("選擇範例：")
    print("1. Streaming 生成範例")
    print("2. Streaming vs 非 Streaming 比較")
    choice = input("\n請選擇 (1 或 2): ").strip()

    if choice == "1":
        example_streaming_generation()
    elif choice == "2":
        example_non_streaming_comparison()
    else:
        print("無效的選擇")
