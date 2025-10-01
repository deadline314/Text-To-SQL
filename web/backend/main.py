"""FastAPI backend for Text-to-SQL Web UI."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import config
from src.models.model_factory import create_model
from src.services.text_to_sql_service import TextToSQLService

app = FastAPI(
    title="Text-to-SQL API",
    description="Convert natural language to SQL queries",
    version="1.4.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SQLGenerationRequest(BaseModel):
    """SQL generation request model."""

    query: str
    provider: str = "local"
    model_id: str | None = None
    stream: bool = True


class SQLGenerationResponse(BaseModel):
    """SQL generation response model."""

    sql: str
    cleaned_sql: str
    provider: str
    model_id: str


class ProviderInfo(BaseModel):
    """Provider information model."""

    id: str
    name: str
    description: str
    default_model: str
    available: bool
    requires_api_key: bool


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Text-to-SQL API",
        "version": "1.4.0",
        "docs": "/docs",
    }


@app.get("/api/providers", response_model=list[ProviderInfo])
async def get_providers():
    """Get available providers."""
    providers = [
        ProviderInfo(
            id="local",
            name="Local (HuggingFace)",
            description="本地 CPU 模型，免費且離線可用",
            default_model=config.MODEL_NAME,
            available=True,
            requires_api_key=False,
        ),
        ProviderInfo(
            id="bedrock",
            name="AWS Bedrock (Claude)",
            description="AWS Claude 模型，高品質 SQL 生成",
            default_model=config.BEDROCK_MODEL_ID,
            available=bool(config.AWS_ACCESS_KEY_ID),
            requires_api_key=True,
        ),
        ProviderInfo(
            id="genai",
            name="Google GenAI (Gemini)",
            description="Google Gemini 模型，快速且經濟",
            default_model=config.GENAI_MODEL_NAME,
            available=bool(config.GOOGLE_API_KEY),
            requires_api_key=True,
        ),
    ]
    return providers


@app.get("/api/schema")
async def get_schema():
    """Get database schema with detailed column information."""

    # Helper function to create column dict
    def col(name: str, typ: str, null: str, key: str, comm: str) -> dict:
        return {"name": name, "type": typ, "nullable": null, "key": key, "comment": comm}

    tencent_bill_cols = [
        col("id", "char(32)", "NO", "PRI", "主鍵 UUID"),
        col("tencent_id", "varchar(36)", "YES", "", "tencent帳號 ID"),
        col("client_profile_id", "varchar(36)", "YES", "", "綁定client"),
        col("tencent_type", "varchar(20)", "YES", "", "CHINA/GLOBAL"),
        col("coupon", "decimal(20,10)", "YES", "", "VoucherPayAmount 總和"),
        col("balance", "decimal(20,10)", "YES", "", "餘額"),
        col("cost", "decimal(20,10)", "YES", "", "cost合計"),
        col("cost_at_list", "decimal(20,10)", "NO", "", "成本牌價"),
        col("bill_month", "char(7)", "YES", "", "帳期"),
        col("currency", "char(10)", "YES", "", "幣別"),
        col("created_date", "datetime", "YES", "", "異動時間"),
        col("note", "varchar(100)", "YES", "", "備註"),
    ]

    global_bill_cols = [
        col("id", "char(32)", "NO", "PRI", "主鍵 UUID"),
        col("tencent_global_account_id", "varchar(36)", "YES", "", "tencent帳號 ID"),
        col("business_code_name", "varchar(100)", "YES", "", "ProductName/產品名稱"),
        col("bill_month", "char(7)", "YES", "", "帳期"),
        col("cost", "decimal(20,10)", "YES", "", "每個產品細項總和"),
        col("cost_at_list", "decimal(20,10)", "NO", "", "成本牌價"),
        col("voucher_pay_amount", "decimal(20,10)", "YES", "", "代金券總和"),
        col("created_date", "datetime", "YES", "", "新增時間"),
        col("currency", "varchar(10)", "YES", "", "幣別"),
        col("note", "varchar(100)", "YES", "", "備註"),
    ]

    global_bill_l3_cols = [
        col("id", "char(32)", "NO", "PRI", "主鍵 UUID"),
        col("bill_month", "char(7)", "YES", "", "帳期"),
        col("bill_id", "varchar(36)", "YES", "", "tencent帳號 ID"),
        col("sub_product_name", "varchar(100)", "YES", "", "騰訊雲產品子類別"),
        col("product_name", "varchar(100)", "YES", "", "產品細項名稱"),
        col("contract_price", "decimal(20,10)", "YES", "", "牌價"),
        col("region", "varchar(100)", "YES", "", "區域"),
        col("used_amount", "decimal(20,10)", "YES", "", "用量"),
        col("used_amount_unit", "varchar(64)", "YES", "", "用量單位"),
        col("real_cost", "decimal(20,10)", "YES", "", "代金券前金額"),
        col("voucher_pay_amount", "decimal(20,10)", "YES", "", "代金券額度"),
        col("total_cost", "decimal(20,10)", "YES", "", "代金券後金額"),
        col("original_real_cost", "decimal(20,10)", "NO", "", "原廠牌價"),
        col("cost_at_list", "decimal(20,10)", "NO", "", "成本牌價"),
        col("timespan", "decimal(20,10)", "YES", "", "使用時長"),
        col("note", "varchar(100)", "YES", "", "備註"),
        col("create_time", "datetime", "YES", "", "建立時間"),
    ]

    return {
        "schema": config.FULL_SCHEMA,
        "tables": [
            {"name": "tencent_bill", "comment": "騰訊帳單主表", "columns": tencent_bill_cols},
            {
                "name": "global_bill",
                "comment": "全球帳單彙總表",
                "columns": global_bill_cols,
            },
            {
                "name": "global_bill_l3",
                "comment": "全球帳單明細表 (L3 層級)",
                "columns": global_bill_l3_cols,
            },
        ],
    }


@app.post("/api/generate")
async def generate_sql(request: SQLGenerationRequest):
    """Generate SQL from natural language query."""
    try:
        # Create model
        model = create_model(provider=request.provider, model_id=request.model_id)
        service = TextToSQLService(model)

        if request.stream:
            # Streaming response
            async def generate():
                full_response = []
                try:
                    for token in service.convert_stream(config.FULL_SCHEMA, request.query):
                        full_response.append(token)
                        yield f"data: {token}\n\n"

                    # Send final cleaned SQL
                    full_sql = "".join(full_response)
                    cleaned_sql = service.sql_parser.clean_sql(full_sql)
                    yield "data: [DONE]\n\n"
                    yield f"data: {cleaned_sql}\n\n"
                except Exception as e:
                    yield f"data: [ERROR] {str(e)}\n\n"

            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            # Non-streaming response
            cleaned_sql = service.convert(config.FULL_SCHEMA, request.query)

            return SQLGenerationResponse(
                sql=cleaned_sql,
                cleaned_sql=cleaned_sql,
                provider=request.provider,
                model_id=request.model_id or "default",
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/execute")
async def execute_sql(request: dict):
    """Execute SQL query and return results."""
    try:
        sql = request.get("sql", "").strip()
        if not sql:
            raise HTTPException(status_code=400, detail="SQL 查詢不能為空")

        # Import database connector
        from src.database.db_connector import DatabaseConnector

        db_connector = DatabaseConnector()

        # Execute query
        results = db_connector.execute_query(sql)

        # Get column names from results
        columns = list(results[0].keys()) if results else []

        # Convert datetime objects to strings for JSON serialization
        from datetime import date, datetime

        serializable_results = []
        for row in results:
            serializable_row = {}
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    serializable_row[key] = value.isoformat()
                elif value is None:
                    serializable_row[key] = None
                else:
                    serializable_row[key] = (
                        str(value) if not isinstance(value, (int, float, bool, str)) else value
                    )
            serializable_results.append(serializable_row)

        return {
            "success": True,
            "columns": columns,
            "rows": serializable_results,
            "row_count": len(serializable_results),
        }

    except Exception as e:
        error_msg = str(e)
        # Extract more detailed error information
        if "pymysql" in error_msg or "MySQL" in error_msg:
            error_type = "資料庫錯誤"
        elif "SQL" in error_msg.upper():
            error_type = "SQL 語法錯誤"
        else:
            error_type = "執行錯誤"

        raise HTTPException(status_code=500, detail=f"{error_type}: {error_msg}") from e


@app.post("/api/auto-execute")
async def auto_execute(request: SQLGenerationRequest):
    """Automatically generate SQL and execute with retry mechanism (streaming)."""
    import json

    from fastapi.responses import StreamingResponse

    from src.database.db_connector import DatabaseConnector
    from src.utils.sql_parser import SQLParser

    async def generate_stream():
        try:
            max_retries = request.dict().get("max_retries", 5)
            db_connector = DatabaseConnector()
            sql_parser = SQLParser()

            original_query = request.query
            error_history = []

            # First attempt uses the standard prompt (same as manual generation)
            from src.prompts.text_to_sql_prompt import TextToSQLPrompt

            current_prompt = TextToSQLPrompt.build_prompt(config.FULL_SCHEMA, original_query)

            # Send start notification
            start_data = {
                "type": "start",
                "message": "開始自動執行",
                "max_retries": max_retries,
            }
            yield f"data: {json.dumps(start_data)}\n\n"

            for attempt in range(1, max_retries + 1):
                try:
                    # Send generating status
                    generating_data = {
                        "type": "generating",
                        "attempt": attempt,
                        "status": "生成 SQL 中...",
                    }
                    yield f"data: {json.dumps(generating_data)}\n\n"

                    # Generate SQL using streaming to avoid blocking
                    model = create_model(provider=request.provider, model_id=request.model_id)
                    service = TextToSQLService(model)

                    if not model.is_initialized():
                        model.initialize()

                    # current_prompt is already a complete prompt (built earlier)
                    prompt = current_prompt

                    # Use threading + queue for non-blocking streaming
                    import asyncio
                    import queue
                    import threading

                    full_response = []
                    token_count = 0

                    if hasattr(model, "generate_stream"):
                        # Create queue for token communication
                        token_queue = queue.Queue()

                        # Function to run in background thread
                        def generate_in_thread():
                            try:
                                for token in model.generate_stream(prompt, max_tokens=512):
                                    token_queue.put(("token", token))
                                token_queue.put(("done", None))
                            except Exception as e:
                                token_queue.put(("error", str(e)))

                        # Start generation in background thread
                        gen_thread = threading.Thread(target=generate_in_thread)
                        gen_thread.start()

                        # Poll queue and yield progress
                        while True:
                            try:
                                msg_type, msg_data = token_queue.get(timeout=0.1)

                                if msg_type == "token":
                                    full_response.append(msg_data)
                                    token_count += 1

                                    # Send progress update every 10 tokens
                                    if token_count % 10 == 0:
                                        progress_data = {
                                            "type": "generating",
                                            "attempt": attempt,
                                            "status": f"生成 SQL 中... ({token_count} tokens)",
                                        }
                                        yield f"data: {json.dumps(progress_data)}\n\n"
                                        await asyncio.sleep(0)  # Allow other tasks to run

                                elif msg_type == "done":
                                    break

                                elif msg_type == "error":
                                    raise Exception(f"生成失敗: {msg_data}")

                            except queue.Empty:
                                # Queue is empty, send heartbeat to keep connection alive
                                await asyncio.sleep(0.1)
                                continue

                        gen_thread.join(timeout=5)

                    else:
                        # Fallback to non-streaming
                        full_response.append(model.generate(prompt, max_tokens=512))

                    raw_sql = "".join(full_response)
                    cleaned_sql = sql_parser.clean_sql(raw_sql)

                    # Validate SQL before execution
                    if not cleaned_sql or not cleaned_sql.strip():
                        raise Exception(
                            f"SQL 清理失敗，無法提取有效的 SQL。原始輸出: {raw_sql[:200]}"
                        )

                    # Send generated SQL
                    generated_data = {
                        "type": "generated",
                        "attempt": attempt,
                        "sql": cleaned_sql,
                        "raw_sql": raw_sql[:500],  # Include raw for debugging
                        "status": "SQL 已生成",
                    }
                    yield f"data: {json.dumps(generated_data)}\n\n"

                    # Send executing status
                    executing_data = {
                        "type": "executing",
                        "attempt": attempt,
                        "sql": cleaned_sql,
                        "status": "執行中...",
                    }
                    yield f"data: {json.dumps(executing_data)}\n\n"

                    # Execute SQL
                    print(f"[DEBUG] Executing SQL: {cleaned_sql}")
                    results = db_connector.execute_query(cleaned_sql)
                    print(f"[DEBUG] Query returned {len(results)} rows")
                    columns = list(results[0].keys()) if results else []

                    # Convert datetime objects to strings for JSON serialization
                    from datetime import date, datetime

                    serializable_results = []
                    for row in results:
                        serializable_row = {}
                        for key, value in row.items():
                            if isinstance(value, (date, datetime)):
                                serializable_row[key] = value.isoformat()
                            elif value is None:
                                serializable_row[key] = None
                            else:
                                serializable_row[key] = (
                                    str(value)
                                    if not isinstance(value, (int, float, bool, str))
                                    else value
                                )
                        serializable_results.append(serializable_row)

                    # Success!
                    success_data = {
                        "type": "success",
                        "attempt": attempt,
                        "sql": cleaned_sql,
                        "status": "完成",
                        "result": {
                            "columns": columns,
                            "rows": serializable_results,
                            "row_count": len(serializable_results),
                        },
                    }
                    print(f"[DEBUG] Sending success event: attempt={attempt}, rows={len(results)}")
                    yield f"data: {json.dumps(success_data)}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                except Exception as e:
                    error_msg = str(e)
                    current_sql = cleaned_sql if "cleaned_sql" in locals() else "SQL 生成失敗"

                    print(f"[DEBUG] Exception caught: {error_msg}")
                    print(f"[DEBUG] Current SQL: {current_sql}")

                    # Record error history
                    error_history.append(
                        {"attempt": attempt, "sql": current_sql, "error": error_msg}
                    )

                    # Send error update immediately with prompt for debugging
                    error_data = {
                        "type": "error",
                        "attempt": attempt,
                        "sql": current_sql,
                        "error": error_msg,
                        "prompt": prompt,  # Include the actual prompt sent to LLM
                        "is_final": attempt >= max_retries,
                    }
                    print(
                        f"[DEBUG] Sending error event: attempt={attempt}, error={error_msg[:100]}"
                    )
                    yield f"data: {json.dumps(error_data)}\n\n"

                    # If this is the last attempt, end the stream
                    if attempt >= max_retries:
                        final_error = {
                            "type": "final_error",
                            "message": f"在 {max_retries} 次嘗試後仍然失敗。最後錯誤: {error_msg}",
                        }
                        yield f"data: {json.dumps(final_error)}\n\n"
                        yield "data: [DONE]\n\n"
                        return

                    # Use the same prompt building method as first attempt
                    # This ensures consistent quality
                    current_prompt = TextToSQLPrompt.build_retry_prompt(
                        config.FULL_SCHEMA, original_query, error_history
                    )

        except Exception as e:
            error_response = {"type": "fatal_error", "message": str(e)}
            yield f"data: {json.dumps(error_response)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.get("/api/examples")
async def get_examples():
    """Get example queries."""
    return {
        "examples": config.DEFAULT_TEST_QUERIES,
        "categories": [
            {
                "name": "基本查詢",
                "queries": [
                    "查詢所有騰訊帳單",
                    "查詢 2024-01 帳期的資料",
                    "找出成本超過 1000 的記錄",
                ],
            },
            {
                "name": "統計分析",
                "queries": [
                    "統計每個帳期的總成本",
                    "查詢代金券使用最多的前 5 筆記錄",
                    "計算平均成本",
                ],
            },
            {
                "name": "複雜查詢",
                "queries": [
                    "查詢成本超過平均值的帳單",
                    "統計每個區域的使用量",
                    "找出成本最高的產品",
                ],
            },
        ],
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.4.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
