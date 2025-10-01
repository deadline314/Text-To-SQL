"""Main entry point for Text-to-SQL CLI."""

from config import FULL_SCHEMA
from src.database.db_connector import DatabaseConnector
from src.models.huggingface_model import HuggingFaceModel
from src.services.text_to_sql_service import TextToSQLService


def main() -> None:
    """Run the Text-to-SQL CLI."""
    print("初始化 Text-to-SQL 系統...")

    model = HuggingFaceModel(device="cpu")
    service = TextToSQLService(model)

    print("系統初始化完成！\n")
    print("資料庫 Schema:")
    print("=" * 80)
    print("1. tencent_bill - 騰訊帳單主表")
    print("2. global_bill - 全球帳單表")
    print("3. global_bill_l3 - 全球帳單明細表")
    print("=" * 80)
    print()

    print("測試資料庫連接...")
    if DatabaseConnector.test_connection():
        print("✓ 資料庫連接成功！\n")
    else:
        print("✗ 資料庫連接失敗（可能需要配置 SSL 證書）\n")

    print("範例查詢：")
    print("- 查詢 2024-01 的所有騰訊帳單")
    print("- 找出成本超過 1000 的全球帳單")
    print("- 統計每個產品的總成本")
    print()
    print("=" * 80)
    print()

    while True:
        prompt_text = "請輸入您的查詢問題 (輸入 'quit' 結束, 'exec' 執行上次生成的SQL): "
        user_query = input(prompt_text).strip()

        if user_query.lower() == "quit":
            print("感謝使用！")
            break

        if not user_query:
            print("請輸入有效的查詢問題\n")
            continue

        print("\n生成中...")
        sql = service.convert(FULL_SCHEMA, user_query)

        print("\n生成的 SQL:")
        print("-" * 80)
        print(sql)
        print("-" * 80)

        execute = input("\n是否執行此 SQL？(y/n): ").strip().lower()
        if execute == "y":
            try:
                results = DatabaseConnector.execute_query(sql)
                print(f"\n查詢結果 ({len(results)} 筆):")
                print("-" * 80)
                for i, row in enumerate(results[:10], 1):
                    print(f"{i}. {row}")
                if len(results) > 10:
                    print(f"... 還有 {len(results) - 10} 筆資料")
                print("-" * 80)
            except Exception as e:
                print(f"\n執行錯誤: {e}")

        print()


if __name__ == "__main__":
    main()
