"""Basic usage example for Text-to-SQL system."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import FULL_SCHEMA
from src.models.huggingface_model import HuggingFaceModel
from src.services.text_to_sql_service import TextToSQLService

EXAMPLE_QUERIES = [
    "查詢所有騰訊帳單",
    "找出 2024-01 帳期的全球帳單",
    "統計每個產品的總成本",
    "查詢成本超過 1000 的帳單記錄",
    "找出使用代金券最多的前 10 筆記錄",
]


def main() -> None:
    """Run basic examples."""
    print("初始化 Text-to-SQL 系統...\n")

    model = HuggingFaceModel(device="cpu")
    service = TextToSQLService(model)

    print("資料庫包含以下表格:")
    print("-" * 80)
    print("1. tencent_bill - 騰訊帳單主表")
    print("2. global_bill - 全球帳單表")
    print("3. global_bill_l3 - 全球帳單明細表")
    print("-" * 80)
    print()

    for i, query in enumerate(EXAMPLE_QUERIES, 1):
        print(f"{i}. 問題: {query}")
        print("   生成中...")

        sql = service.convert(FULL_SCHEMA, query)

        print("   生成的 SQL:")
        print(f"   {sql}")
        print()
        print("=" * 80)
        print()


if __name__ == "__main__":
    main()
