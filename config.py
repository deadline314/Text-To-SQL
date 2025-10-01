"""Configuration for Text-to-SQL system.

所有系統設定都在此檔案中管理：
- 資料庫連接設定
- 模型設定
- 其他常數設定

修改此檔案即可更換模型或調整參數，無需修改程式碼。
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent


# ============================================================================
# 模型設定 (Model Configuration)
# ============================================================================

# 模型名稱 - 可以是任何 HuggingFace 模型
# MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
# MODEL_NAME = "Qwen/Qwen3-0.6B"
# MODEL_NAME = "google/gemma-3-1b-it"  # Google Gemma 3 1B（需要 HF 授權）
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"  # 更大的模型，更準確（無需授權）
# MODEL_NAME = "google/gemma-2-2b-it"  # Google Gemma 2 2B（需要 HF 授權）
# MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"  # 最大的模型，需要更多資源

# 運行裝置
MODEL_DEVICE = "cpu"  # 選項: "cpu", "cuda", "mps" (Apple Silicon)

# 生成參數
MODEL_TEMPERATURE = 0.1  # 溫度: 0.0-1.0，越低越保守，SQL 生成建議使用低值
MODEL_TOP_P = 0.9  # Top-p 採樣: 0.0-1.0
MODEL_MAX_TOKENS = 512  # 最大生成 token 數

# 允許透過環境變數覆蓋（可選）
MODEL_NAME = os.getenv("MODEL_NAME", MODEL_NAME)
MODEL_DEVICE = os.getenv("MODEL_DEVICE", MODEL_DEVICE)
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", str(MODEL_TEMPERATURE)))
MODEL_TOP_P = float(os.getenv("MODEL_TOP_P", str(MODEL_TOP_P)))


# ============================================================================
# v1.3.0+ Provider 設定 (Multi-Provider Support)
# ============================================================================

# Provider 選擇: "local", "bedrock", "genai"
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "local")

# AWS Bedrock 設定 (需要安裝: pip install boto3 botocore)
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
BEDROCK_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# Google GenAI 設定 (需要安裝: pip install google-generativeai)
GENAI_MODEL_NAME = os.getenv("GENAI_MODEL_NAME", "gemini-2.5-flash")
GOOGLE_API_KEY = os.getenv("GCP_API_KEY", "")

# 重試機制設定 (需要安裝: pip install tenacity)
RETRY_ENABLED = True
RETRY_MAX_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 1.0  # 秒
RETRY_MAX_DELAY = 10.0  # 秒
RETRY_EXPONENTIAL_BASE = 2
RETRY_JITTER = True  # 隨機抖動

# 超時設定
REQUEST_TIMEOUT = 30  # 秒
GENERATION_TIMEOUT = 60  # 秒

# 驗證設make
VALIDATE_SQL_OUTPUT = True
AUTO_RETRY_ON_VALIDATION_FAILURE = True


# ============================================================================
# 資料庫設定 (Database Configuration)
# ============================================================================


@dataclass
class DatabaseConfig:
    """Database connection configuration."""

    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "0000"))
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "")
    database: str = os.getenv("DB_NAME", "")
    ssl_ca: str = os.getenv("DB_SSL_CA", str(BASE_DIR / "server-cert" / "server-ca.pem"))
    ssl_cert: str = os.getenv("DB_SSL_CERT", str(BASE_DIR / "server-cert" / "client-cert.pem"))
    ssl_key: str = os.getenv("DB_SSL_KEY", str(BASE_DIR / "server-cert" / "client-key.pem"))
    charset: str = "utf8mb4"


DB_CONFIG = DatabaseConfig()


# ============================================================================
# SQL 解析設定 (SQL Parser Configuration)
# ============================================================================

# SQL 格式化設定
SQL_FORMAT_REINDENT = True  # 是否重新縮排
SQL_FORMAT_KEYWORD_CASE = "upper"  # 關鍵字大小寫: "upper", "lower", "capitalize"

# SQL 驗證設定
VALID_SQL_TYPES = [
    "SELECT",
    "INSERT",
    "UPDATE",
    "DELETE",
    "CREATE",
    "ALTER",
    "DROP",
    "TRUNCATE",
]


# ============================================================================
# Schema 定義 (Database Schema Definitions)
# ============================================================================

# ruff: noqa: E501
TENCENT_BILL_SCHEMA = """
CREATE TABLE tencent_bill (
  id char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'UUID()' COMMENT '主鍵 UUID',
  tencent_id varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'tencent帳號 ID',
  client_profile_id varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '綁定client',
  tencent_type varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'CHINA/GLOBAL',
  coupon decimal(20,10) DEFAULT NULL COMMENT 'VoucherPayAmount 總和',
  balance decimal(20,10) DEFAULT NULL COMMENT '餘額',
  cost decimal(20,10) DEFAULT NULL COMMENT 'cost合計',
  cost_at_list decimal(20,10) NOT NULL DEFAULT '0.0000000000' COMMENT '成本牌價',
  bill_month char(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '帳期',
  currency char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '幣別',
  created_date datetime DEFAULT CURRENT_TIMESTAMP COMMENT '異動時間',
  note varchar(100) DEFAULT NULL COMMENT '備註',
  PRIMARY KEY (`id`),
  UNIQUE KEY unique_01 (`tencent_id`,`client_profile_id`,`bill_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

GLOBAL_BILL_SCHEMA = """
CREATE TABLE global_bill (
  id char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'UUID()' COMMENT '主鍵 UUID',
  tencent_global_account_id varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'tencent帳號 ID',
  business_code_name varchar(100) DEFAULT NULL COMMENT 'ProductName/產品名稱/經銷商平台-客戶帳單',
  bill_month char(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '帳期',
  cost decimal(20,10) DEFAULT NULL COMMENT '每個產品細項總和減去voucher_pay_amount',
  cost_at_list decimal(20,10) NOT NULL DEFAULT '0.0000000000' COMMENT '成本牌價',
  voucher_pay_amount decimal(20,10) DEFAULT NULL COMMENT '每個產品細項的voucher_pay_amount總和',
  created_date datetime DEFAULT CURRENT_TIMESTAMP COMMENT '新增時間',
  currency varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '幣別',
  note varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '備註',
  PRIMARY KEY (`id`),
  UNIQUE KEY unique_01 (`tencent_global_account_id`,`business_code_name`,`bill_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

GLOBAL_BILL_L3_SCHEMA = """
CREATE TABLE global_bill_l3 (
  id char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'UUID()' COMMENT '主鍵 UUID',
  bill_month char(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '帳期',
  bill_id varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'tencent帳號 ID',
  sub_product_name varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'SubproductName 騰訊雲產品子類別',
  product_name varchar(100) DEFAULT NULL COMMENT 'ComponentName/產品細項名稱/經銷商平台-客戶帳單',
  contract_price decimal(20,10) DEFAULT NULL COMMENT 'ComponentListPrice/牌價/經銷商平台-客戶帳單',
  region varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '區域',
  used_amount decimal(20,10) DEFAULT NULL COMMENT 'ComponentUsage/用量/經銷商平台-客戶帳單',
  used_amount_unit varchar(64) DEFAULT NULL COMMENT 'ComponentPriceMeasurementUnit/用量單位/經銷商平台-客戶帳單',
  real_cost decimal(20,10) DEFAULT NULL COMMENT 'OriginalCost/代金券前金額/經銷商平台-客戶帳單',
  voucher_pay_amount decimal(20,10) DEFAULT NULL COMMENT 'CustomerVoucherDeduction/代金券額度/經銷商平台-客戶帳單',
  total_cost decimal(20,10) DEFAULT NULL COMMENT 'TotalCost/代金券後金額/經銷商平台-客戶帳單',
  original_real_cost decimal(20,10) NOT NULL DEFAULT '0.0000000000' COMMENT '原廠牌價',
  cost_at_list decimal(20,10) NOT NULL DEFAULT '0.0000000000' COMMENT 'Component Contracted Price 成本牌價',
  timespan decimal(20,10) DEFAULT NULL COMMENT 'UsageDuration/使用時長/經銷商平台-客戶帳單',
  note varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '備註',
  create_time datetime DEFAULT NULL COMMENT '建立時間',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

# 完整 Schema（組合所有表格）
FULL_SCHEMA = f"""{TENCENT_BILL_SCHEMA}

{GLOBAL_BILL_SCHEMA}

{GLOBAL_BILL_L3_SCHEMA}
"""


# ============================================================================
# 系統常數 (System Constants)
# ============================================================================

# 應用程式資訊
APP_NAME = "Text-to-SQL"
APP_VERSION = "1.2.0"

# 預設查詢（用於測試）
DEFAULT_TEST_QUERIES = [
    "查詢所有騰訊帳單",
    "查詢 2025-01 帳期的資料",
    "統計每個帳期的總成本",
]

# 快取設定
CACHE_DIR = BASE_DIR / ".cache"
MODEL_CACHE_DIR = CACHE_DIR / "models"

# 日誌設定
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# ============================================================================
# 設定摘要輸出（開發時可用於檢查）
# ============================================================================


def print_config_summary():
    """列印當前設定摘要（用於除錯）."""
    print("=" * 80)
    print(f"{APP_NAME} v{APP_VERSION} - 設定摘要")
    print("=" * 80)
    print("\n[模型設定]")
    print(f"  模型名稱: {MODEL_NAME}")
    print(f"  運行裝置: {MODEL_DEVICE}")
    print(f"  溫度: {MODEL_TEMPERATURE}")
    print(f"  Top-p: {MODEL_TOP_P}")
    print(f"  最大 Tokens: {MODEL_MAX_TOKENS}")
    print("\n[資料庫設定]")
    print(f"  主機: {DB_CONFIG.host}")
    print(f"  端口: {DB_CONFIG.port}")
    print(f"  使用者: {DB_CONFIG.user}")
    print(f"  資料庫: {DB_CONFIG.database or '(未指定)'}")
    print(f"  SSL: {'啟用' if DB_CONFIG.ssl_ca else '停用'}")
    print("=" * 80)


if __name__ == "__main__":
    # 當直接執行 config.py 時顯示設定摘要
    print_config_summary()
