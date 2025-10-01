"""Prompt template for Text-to-SQL conversion."""

SYSTEM_INSTRUCTION = """你是一個專業的 SQL 專家。
根據提供的資料庫 schema 和使用者的自然語言問題，生成精確的 SQL 查詢語句。

重要提醒：
- schema 中的欄位名稱和表格名稱必須完全一致（包括大小寫、底線）
- 不要使用 schema 中不存在的欄位
- 不要自己發明或猜測欄位名稱

關鍵要求：
1. 仔細檢查欄位名稱是否「完全一致」存在於提供的 schema 中
2. 確認表格名稱拼寫正確（包括大小寫）
3. 如果需要 JOIN，確保表格別名正確且一致
4. 使用正確的 SQL 語法（MySQL 8.0）
5. 只輸出 SQL 語句，不要包含任何解釋或其他文字
6. SQL 必須用 ```sql 和 ``` 包起來

常見錯誤（請避免）：
- 使用不存在的欄位名稱（如：schema 中是 bill_month 但用了 month）
- 表格別名不一致（如：FROM table1 AS T1 但 WHERE 用 T2.column）
- 欄位名稱拼寫錯誤或大小寫錯誤
- 忘記在 GROUP BY 中包含所有非聚合欄位
- 日期格式錯誤（MySQL 使用 'YYYY-MM-DD' 或 'YYYY-MM'）
- 使用錯誤的聚合函數或語法

輸出格式範例：
```sql
SELECT * FROM table_name WHERE condition;
```


```sql
SELECT column1, column2 FROM table_name WHERE condition;
```

請遵守此格式，不要輸出任何描述性文字。
"""

PROMPT_TEMPLATE = """### 資料庫Schema:
{schema}

### 使用者問題:
{user_query}

### SQL查詢:
"""


class TextToSQLPrompt:
    """Text-to-SQL prompt template manager."""

    @staticmethod
    def build_prompt(schema: str, user_query: str) -> str:
        """
        Build a complete prompt for Text-to-SQL conversion.

        Args:
            schema: Database schema description
            user_query: User's natural language query

        Returns:
            Complete prompt string
        """
        full_prompt = (
            SYSTEM_INSTRUCTION.strip()
            + "\n\n"
            + PROMPT_TEMPLATE.format(schema=schema.strip(), user_query=user_query.strip())
        )
        return full_prompt

    @staticmethod
    def build_retry_prompt(schema: str, user_query: str, error_history: list[dict]) -> str:
        """
        Build a retry prompt with error history.

        Args:
            schema: Database schema description
            user_query: User's natural language query
            error_history: List of previous attempts with errors
                          [{"attempt": 1, "sql": "...", "error": "..."}]

        Returns:
            Complete retry prompt string
        """
        # Build error history section
        history_section = ""
        if len(error_history) > 0:
            history_section = "\n### 歷史錯誤記錄：\n"
            for i, err_record in enumerate(error_history, 1):
                history_section += f"\n第 {err_record['attempt']} 次嘗試：\n"
                history_section += f"生成的 SQL:\n```sql\n{err_record['sql']}\n```\n\n"
                history_section += f"錯誤訊息:\n{err_record['error']}\n"
                if i < len(error_history):
                    history_section += "\n" + "-" * 60 + "\n"

            history_section += "\n⚠️ 請根據上述錯誤，特別注意欄位名稱的正確性和 SQL 語法。\n"

        # Build retry prompt with same system instruction
        retry_template = f"""### 資料庫Schema:
{{schema}}

{{history_section}}

### 使用者問題:
{{user_query}}

### 分析步驟：
1. 檢查上述錯誤中的問題
2. 在 schema 中尋找正確的欄位名稱
3. 確認表格別名一致性
4. 避免重複相同的錯誤

### SQL查詢:
"""

        full_prompt = (
            SYSTEM_INSTRUCTION.strip()
            + "\n\n"
            + retry_template.format(
                schema=schema.strip(),
                user_query=user_query.strip(),
                history_section=history_section,
            )
        )
        return full_prompt

    @staticmethod
    def get_system_instruction() -> str:
        """Get the system instruction for the model."""
        return SYSTEM_INSTRUCTION.strip()

    @staticmethod
    def get_template() -> str:
        """Get the prompt template."""
        return PROMPT_TEMPLATE
