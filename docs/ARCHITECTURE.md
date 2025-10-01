# 系統架構說明

## 概述

Text-to-SQL 系統採用模組化設計，遵循 Clean Code 原則，易於擴展和維護。

## 專案結構

```
Text-to-SQL/
├── README.md             # 專案說明
├── CHANGELOG.md          # 變更日誌
├── config.py             # 設定檔（資料庫、Schema）
├── requirements.txt      # 依賴套件
├── pyproject.toml        # 專案設定（pytest、ruff）
├── Makefile              # 常用命令
├── .env.example          # 環境變數範例
├── .gitignore            # Git 忽略規則
│
├── src/                  # 原始碼
│   ├── database/         # 資料庫連接
│   │   └── db_connector.py       # MySQL 連接和查詢執行
│   ├── interfaces/       # 抽象介面
│   │   └── language_model.py     # 語言模型介面
│   ├── models/           # 模型實作
│   │   └── huggingface_model.py  # HuggingFace 模型實作
│   ├── prompts/          # Prompt 模板
│   │   └── text_to_sql_prompt.py # Text-to-SQL Prompt
│   ├── services/         # 業務邏輯
│   │   └── text_to_sql_service.py # Text-to-SQL 服務
│   ├── utils/            # 工具函數
│   │   └── sql_parser.py         # SQL 解析和驗證
│   └── main.py           # CLI 入口
│
├── tests/                # 單元測試
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_model.py
│   ├── test_prompt.py
│   ├── test_service.py
│   └── test_sql_parser.py
│
├── tools/                # 測試工具
│   ├── test_connection.py   # 測試資料庫連接
│   ├── quick_test.py        # 快速 SQL 生成測試
│   ├── test_generation.py   # 完整互動式測試
│   └── list_databases.py    # 探索資料庫
│
├── examples/             # 使用範例
│   ├── basic_usage.py
│   └── streaming_example.py
│
├── docs/                 # 詳細文件
│   ├── SETUP.md              # 安裝設定指南
│   ├── TESTING.md            # 測試工具說明
│   ├── STREAMING_GUIDE.md    # Streaming 功能指南
│   ├── ARCHITECTURE.md       # 系統架構說明（本文件）
│   └── PROJECT_SUMMARY.md    # 專案總結
│
├── scripts/              # 輔助腳本
│   └── unzip_certs.sh
│
└── server-cert/          # SSL 證書
    ├── server-ca.zip
    ├── client-cert.zip
    └── client-key.zip
```

## 系統架構

### 分層架構

```
┌─────────────────────────────────────────┐
│           使用者介面層                    │
│  (CLI / 測試工具 / 程式化使用)             │
└─────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────┐
│           服務層（Service）               │
│        TextToSQLService                 │
│  - convert()          (非 streaming)    │
│  - convert_stream()   (streaming)       │
└─────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
┌──────────────┐      ┌──────────────┐
│   模型層      │      │   工具層      │
│ ILanguageModel│      │  SQLParser   │
│ (抽象介面)    │      │   (驗證/格式化)│
└──────────────┘      └──────────────┘
        │
        ↓
┌──────────────┐
│   實作層      │
│HuggingFaceModel│
│ - generate()  │
│ - generate_   │
│   stream()    │
└──────────────┘
        │
        ↓
┌─────────────────────────────────────────┐
│           資料層                          │
│      DatabaseConnector                  │
│  - get_connection()                     │
│  - execute_query()                      │
└─────────────────────────────────────────┘
```

### 核心元件

#### 1. 介面層（Interfaces）

**ILanguageModel** (`src/interfaces/language_model.py`)

定義語言模型的抽象介面：

```python
class ILanguageModel(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """生成文字"""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """初始化模型"""
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """檢查是否已初始化"""
        pass
```

**設計優勢**：
- 鬆耦合：易於更換不同的模型實作
- 可測試性：可使用 Mock 物件進行測試
- 擴展性：新增模型只需實作介面

#### 2. 模型層（Models）

**HuggingFaceModel** (`src/models/huggingface_model.py`)

HuggingFace 模型的實作：

```python
class HuggingFaceModel(ILanguageModel):
    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-0.5B-Instruct",
        device: str = "cpu",
        temperature: float = 0.1,
        top_p: float = 0.9,
    ):
        ...
    
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """非 streaming 生成"""
        ...
    
    def generate_stream(self, prompt: str, max_tokens: int = 512):
        """Streaming 生成（v1.2.0 新增）"""
        ...
```

**功能**：
- 支援 HuggingFace transformers 模型
- CPU 可運行（使用 `accelerate` 優化）
- 支援 Streaming 和非 Streaming 模式
- 可自訂溫度和 top_p 參數

#### 3. Prompt 層（Prompts）

**TextToSQLPrompt** (`src/prompts/text_to_sql_prompt.py`)

管理 Text-to-SQL 的 Prompt 模板：

```python
class TextToSQLPrompt:
    SYSTEM_INSTRUCTION = """
    你是一個 SQL 專家...
    """
    
    @staticmethod
    def build_prompt(schema: str, user_query: str) -> str:
        """建立完整的 prompt"""
        ...
```

**設計**：
- Schema 和使用者查詢作為變數
- 清晰的指令和限制
- 可輕鬆調整和優化

#### 4. 服務層（Services）

**TextToSQLService** (`src/services/text_to_sql_service.py`)

核心業務邏輯：

```python
class TextToSQLService:
    def convert(self, schema: str, user_query: str, max_tokens: int = 512) -> str:
        """轉換自然語言為 SQL"""
        prompt = TextToSQLPrompt.build_prompt(schema, user_query)
        raw_output = self.model.generate(prompt, max_tokens)
        sql = self.sql_parser.clean_sql(raw_output)
        return sql
    
    def convert_stream(self, schema: str, user_query: str, max_tokens: int = 512):
        """Streaming 模式轉換（v1.2.0 新增）"""
        ...
```

**職責**：
- 協調 Prompt、模型、解析器
- 提供統一的 API
- 處理業務邏輯

#### 5. 工具層（Utils）

**SQLParser** (`src/utils/sql_parser.py`)

SQL 解析和驗證：

```python
class SQLParser:
    @staticmethod
    def extract_sql(text: str) -> str:
        """從文字中提取 SQL"""
        ...
    
    @staticmethod
    def validate_sql(sql: str) -> bool:
        """驗證 SQL 語法"""
        ...
    
    @staticmethod
    def format_sql(sql: str) -> str:
        """格式化 SQL"""
        ...
    
    @staticmethod
    def clean_sql(raw_output: str) -> str:
        """清理和格式化 SQL"""
        ...
```

**功能**：
- 從模型輸出中提取 SQL
- 驗證語法正確性
- 格式化輸出

#### 6. 資料層（Database）

**DatabaseConnector** (`src/database/db_connector.py`)

資料庫連接和查詢執行：

```python
class DatabaseConnector:
    @staticmethod
    def get_connection():
        """獲取資料庫連接（context manager）"""
        ...
    
    @staticmethod
    def execute_query(query: str, database: str | None = None):
        """執行查詢並返回結果"""
        ...
    
    @staticmethod
    def test_connection() -> bool:
        """測試連接"""
        ...
```

**功能**：
- MySQL 連接管理（SSL 支援）
- 查詢執行和結果處理
- 連接測試

## 設計模式

### 1. 介面隔離原則（Interface Segregation）

使用 `ILanguageModel` 介面隔離模型實作，允許：
- 輕鬆替換不同的模型
- 使用 Mock 進行測試
- 獨立開發和測試

### 2. 依賴注入（Dependency Injection）

服務層接受介面而非具體實作：

```python
class TextToSQLService:
    def __init__(self, model: ILanguageModel):
        self.model = model  # 依賴注入
```

**優點**：
- 鬆耦合
- 可測試性高
- 易於擴展

### 3. 單一職責原則（Single Responsibility）

每個類別只負責一件事：
- `TextToSQLPrompt` - Prompt 管理
- `HuggingFaceModel` - 模型操作
- `SQLParser` - SQL 處理
- `DatabaseConnector` - 資料庫操作

### 4. 策略模式（Strategy Pattern）

不同的模型實作可以互換：

```python
# 使用 HuggingFace 模型
model = HuggingFaceModel()

# 或使用自訂模型
model = CustomModel()

# 服務層不需要改變
service = TextToSQLService(model)
```

## 資料流程

### 非 Streaming 模式

```
使用者輸入
    ↓
build_prompt(schema, query)  # 建立 prompt
    ↓
model.generate(prompt)       # 生成文字
    ↓
sql_parser.clean_sql()       # 清理和驗證
    ↓
返回 SQL
```

### Streaming 模式（v1.2.0）

```
使用者輸入
    ↓
build_prompt(schema, query)  # 建立 prompt
    ↓
model.generate_stream(prompt)  # Streaming 生成
    ↓                          ↓
    ↓                     即時產出 token
    ↓                          ↓
    ↓                     使用者看到即時輸出
    ↓
收集完整輸出
    ↓
sql_parser.clean_sql()       # 清理和驗證
    ↓
返回清理後的 SQL
```

## 設定管理

### config.py

集中管理所有設定：

```python
@dataclass
class DatabaseConfig:
    """資料庫設定"""
    host: str
    port: int
    user: str
    password: str
    database: str
    ...

# Schema 定義
TENCENT_BILL_SCHEMA = "..."
GLOBAL_BILL_SCHEMA = "..."
GLOBAL_BILL_L3_SCHEMA = "..."
FULL_SCHEMA = TENCENT_BILL_SCHEMA + ...
```

### 環境變數

使用 `.env` 覆蓋預設值：

```bash
DB_HOST=your_host
DB_PORT=0000
DB_USER=your_user
DB_PASSWORD=your_password
```

## 測試架構

### 單元測試（tests/）

每個模組都有對應的測試：

```
tests/
├── test_config.py        # 設定測試
├── test_database.py      # 資料庫測試
├── test_model.py         # 模型測試
├── test_prompt.py        # Prompt 測試
├── test_service.py       # 服務測試
└── test_sql_parser.py    # SQL 解析器測試
```

使用 pytest 框架：
```bash
make test                    # 運行所有測試
make test scope=test_model.py  # 運行特定測試
```

### 整合測試（tools/）

實際環境測試：

```
tools/
├── test_connection.py    # 連接測試
├── quick_test.py         # 快速功能測試
├── test_generation.py    # 完整互動測試
└── list_databases.py     # 資料庫探索
```

## 擴展指南

### 新增模型

1. 實作 `ILanguageModel` 介面：

```python
from src.interfaces.language_model import ILanguageModel

class CustomModel(ILanguageModel):
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        # 實作生成邏輯
        pass
    
    def initialize(self) -> None:
        # 實作初始化邏輯
        pass
    
    def is_initialized(self) -> bool:
        return self._initialized
```

2. 使用新模型：

```python
model = CustomModel()
service = TextToSQLService(model)
```

### 新增資料庫支援

修改 `DatabaseConnector` 支援其他資料庫：

```python
@staticmethod
def get_connection(db_type="mysql"):
    if db_type == "mysql":
        return pymysql.connect(...)
    elif db_type == "postgresql":
        return psycopg2.connect(...)
```

### 新增 Prompt 策略

創建新的 Prompt 類別：

```python
class CustomPrompt:
    @staticmethod
    def build_prompt(schema: str, user_query: str) -> str:
        # 自訂 prompt 邏輯
        return f"Custom: {user_query} for {schema}"
```

## 效能優化

### 模型快取

模型只初始化一次：

```python
model = HuggingFaceModel()
service = TextToSQLService(model)

# 多次查詢重用同一模型
sql1 = service.convert(schema, query1)
sql2 = service.convert(schema, query2)
```

### 連接池

使用 context manager 管理連接：

```python
with DatabaseConnector.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
```

### Streaming 優化

使用 `accelerate` 和 `device_map="auto"` 優化模型載入：

```python
self.model = AutoModelForCausalLM.from_pretrained(
    self.model_name, 
    torch_dtype="auto", 
    device_map="auto"  # 自動裝置分配
)
```

## 安全性

### SSL 連接

資料庫連接使用 SSL 加密：

```python
ssl_config = {
    "ca": ssl_ca_path,
    "cert": ssl_cert_path,
    "key": ssl_key_path,
}
connection = pymysql.connect(..., ssl=ssl_config)
```

### SQL 注入防護

雖然是生成 SQL，但建議：
1. 驗證生成的 SQL 語法
2. 使用 prepared statements 執行
3. 限制使用者權限

### 環境變數

敏感資訊存於 `.env`：
- 資料庫密碼
- API Keys（如需）
- 不提交到 Git

## 程式碼品質

### Linting

使用 Ruff：

```bash
make fix  # 自動修復風格問題
```

設定（`pyproject.toml`）：
- 行長度: 100
- Python 版本: 3.10+

### 測試覆蓋率

目標: > 65%

```bash
make test  # 顯示覆蓋率報告
```

### 文件

每個模組都有 docstring：

```python
def convert(self, schema: str, user_query: str, max_tokens: int = 512) -> str:
    """
    轉換自然語言查詢為 SQL。

    Args:
        schema: 資料庫 schema 描述
        user_query: 使用者的自然語言查詢
        max_tokens: 最大生成 token 數

    Returns:
        生成的 SQL 查詢
    """
```

## 相關文件

- [README.md](../README.md) - 專案概覽和快速開始
- [SETUP.md](SETUP.md) - 安裝設定指南
- [TESTING.md](TESTING.md) - 測試工具說明
- [STREAMING_GUIDE.md](STREAMING_GUIDE.md) - Streaming 功能指南
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 專案總結

## 總結

Text-to-SQL 系統採用：
- **模組化設計**：易於維護和擴展
- **介面抽象**：鬆耦合，可替換元件
- **分層架構**：清晰的職責劃分
- **完整測試**：單元測試和整合測試
- **良好文件**：詳細的說明和範例

這樣的架構確保系統：
- 易於理解
- 容易測試
- 方便擴展
- 穩定可靠
