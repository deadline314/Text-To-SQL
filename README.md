# Text-to-SQL

將自然語言轉換為 SQL 查詢的系統。

## 特點

- 模組化設計，易於擴展和維護
- 支援 MySQL 資料庫連接（SSL 加密）
- 使用輕量級中文模型（CPU 可運行）
- Streaming 即時輸出，提供更好的使用者體驗
- 完整的測試工具集
- 純 SQL 輸出，自動驗證和格式化
- **集中式設定管理** - 所有設定都在 `config.py` 中

## 快速開始

### 1. 環境需求

- Python 3.10+
- Conda（建議）
- 約 2GB 磁碟空間（模型）
- 網路連接（首次下載模型）

### 2. 安裝

#### 方式 1：一鍵完成（推薦）⭐

```bash
make setup-full
conda activate t2s
```

這會自動：
- 建立 conda 環境 `t2s`
- 安裝所有依賴
- 解壓 SSL 證書

#### 方式 2：手動步驟

```bash
# 建立 conda 環境
make conda-env
# 或手動：conda create -n t2s python=3.10

# 啟動環境
conda activate t2s

# 安裝依賴和證書
make setup
```

### 3. 設定模型（可選）

所有設定都在 **`config.py`** 檔案中：

```python
# 編輯 config.py

# 更換模型（取消註解想用的模型）
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
# MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"  # 更大的模型
# MODEL_NAME = "google/gemma-2-2b-it"        # Google Gemma

# 調整參數
MODEL_DEVICE = "cpu"          # 或 "cuda", "mps"
MODEL_TEMPERATURE = 0.1       # 越低越保守
MODEL_TOP_P = 0.9
```

### 4. 測試連接

```bash
python tools/test_connection.py
```

如果看到「✓ 資料庫連接成功！」表示設定完成。

### 5. 開始使用

```bash
# 快速運行（推薦）
make gen

# 或使用其他工具
python tools/quick_test.py          # 快速測試
python tools/test_generation.py    # 完整測試
python -m src.main                  # 互動式 CLI
```

## 設定管理

### 所有設定都在 config.py

所有系統設定、常數、參數都集中在根目錄的 **`config.py`** 檔案中管理：

```python
# config.py 結構

# 1. 模型設定
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
MODEL_DEVICE = "cpu"
MODEL_TEMPERATURE = 0.1
MODEL_TOP_P = 0.9
MODEL_MAX_TOKENS = 512

# 2. 資料庫設定
DB_CONFIG = DatabaseConfig(...)

# 3. SQL 解析設定
SQL_FORMAT_REINDENT = True
SQL_FORMAT_KEYWORD_CASE = "upper"
VALID_SQL_TYPES = ["SELECT", "INSERT", ...]

# 4. Schema 定義
TENCENT_BILL_SCHEMA = "..."
GLOBAL_BILL_SCHEMA = "..."
FULL_SCHEMA = "..."

# 5. 系統常數
APP_NAME = "Text-to-SQL"
APP_VERSION = "1.2.0"
DEFAULT_TEST_QUERIES = [...]
CACHE_DIR = ...
LOG_LEVEL = "INFO"
```

### 查看當前設定

```bash
python config.py
```

輸出：
```
================================================================================
Text-to-SQL v1.2.0 - 設定摘要
================================================================================

[模型設定]
  模型名稱: Qwen/Qwen2.5-0.5B-Instruct
  運行裝置: cpu
  溫度: 0.1
  Top-p: 0.9
  最大 Tokens: 512

[資料庫設定]
  使用者: user
  資料庫: (未指定)
  SSL: 啟用
================================================================================
```

### 更換模型

只需編輯 `config.py`：

```python
# 方式 1：直接修改
MODEL_NAME = "google/gemma-2-2b-it"

# 方式 2：取消註解預設選項
# MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"  # 使用這個
# MODEL_NAME = "google/gemma-2-2b-it"
```

或透過環境變數（`.env`）：

```bash
MODEL_NAME=google/gemma-2-2b-it
```

## 使用方法

### 基本使用

```python
from config import FULL_SCHEMA
from src.models.huggingface_model import HuggingFaceModel
from src.services.text_to_sql_service import TextToSQLService

# 初始化（自動使用 config.py 的設定）
model = HuggingFaceModel()
service = TextToSQLService(model)

# 轉換查詢
sql = service.convert(FULL_SCHEMA, "查詢 2025-01 帳期的帳單")
print(sql)
# 輸出: SELECT * FROM tencent_bill WHERE bill_month = '2025-01';
```

### Streaming 模式

```python
# 即時顯示生成過程
for token in service.convert_stream(FULL_SCHEMA, "查詢所有帳單"):
    print(token, end="", flush=True)
```

### 執行查詢

```python
from src.database.db_connector import DatabaseConnector

# 執行 SQL
results = DatabaseConnector.execute_query(sql)
print(f"查詢結果: {len(results)} 筆")

# 顯示結果
for row in results[:5]:
    print(row)
```

## 專案結構

```
Text-to-SQL/
├── config.py             # ⭐ 所有設定都在這裡
├── README.md             # 專案說明
├── CHANGELOG.md          # 變更日誌
├── requirements.txt      # 依賴套件
├── Makefile              # 常用命令
│
├── src/                  # 原始碼
│   ├── database/         # 資料庫連接
│   ├── interfaces/       # 抽象介面
│   ├── models/           # 模型實作（從 config.py 讀取設定）
│   ├── prompts/          # Prompt 模板
│   ├── services/         # 業務邏輯
│   ├── utils/            # 工具函數
│   └── main.py           # CLI 入口
│
├── tests/                # 單元測試
├── tools/                # 測試工具
│   ├── test_connection.py
│   ├── quick_test.py
│   ├── test_generation.py
│   └── list_databases.py
│
├── examples/             # 使用範例
├── docs/                 # 詳細文件
└── scripts/              # 輔助腳本
```

## 測試工具

| 工具 | 功能 | 使用時機 |
|------|------|----------|
| `make gen` | 互動式測試工具（快捷方式） | 日常使用 |
| `test_connection.py` | 測試資料庫連接 | 首次設定、排查問題 |
| `quick_test.py` | 快速 SQL 生成測試 | 驗證功能正常 |
| `test_generation.py` | 完整互動式測試 | 深度測試 |
| `list_databases.py` | 探索資料庫結構 | 了解資料庫內容 |

詳見 [測試指南](docs/TESTING.md)

## 資料庫設定

系統預設連接騰訊雲 MySQL。所有設定在 **`config.py`** 中：

### Schema 說明

系統使用三個騰訊雲帳單表（定義在 `config.py`）：

**tencent_bill** - 騰訊帳單主表
**global_bill** - 全球帳單表
**global_bill_l3** - 全球帳單明細表

完整 Schema 定義見 `config.py`

## 開發

### Makefile 命令

#### 安裝設定
```bash
make setup-full    # ⭐ 一鍵完成（conda env + 安裝 + 證書）
make conda-env     # 建立 conda 環境
make install       # 安裝依賴
make setup-certs   # 解壓 SSL 證書
make setup         # 安裝 + 證書（不建立 conda env）
```

#### 開發使用
```bash
make gen           # 運行互動式測試工具
make fix           # 修復代碼風格
make test          # 運行測試
make clean         # 清理快取
make help          # 查看所有命令
```

### 運行測試

```bash
# 修復代碼風格（運行測試前必須執行）
make fix

# 運行所有測試
make test

# 運行特定測試
make test scope=test_model.py
```

### 代碼風格

使用 Ruff 進行代碼檢查：
- 行長度限制: 100 字元
- Python 版本: 3.10+
- 自動格式化: `make fix`

## 詳細文件

- [安裝設定指南](docs/SETUP.md) - 詳細的安裝步驟和設定說明
- [測試工具說明](docs/TESTING.md) - 所有測試工具的使用方法
- [Streaming 功能](docs/STREAMING_GUIDE.md) - Streaming 功能的完整指南
- [系統架構](docs/ARCHITECTURE.md) - 系統設計和架構說明
- [專案總結](docs/PROJECT_SUMMARY.md) - 專案概覽和功能總結
- [開發路線圖](docs/ROADMAP.md) - 未來功能規劃和版本計劃

**注意**: `docs/MODEL_CONFIG.md` 已整合到本檔案和 `config.py` 中。

## 常見問題

### SSL 證書錯誤
```bash
make setup-certs  # 解壓證書檔案
```

### 連接失敗
1. 確認 SSL 證書已解壓
2. 檢查網路連接
3. 確認 `.env` 設定正確

### 更換模型
直接編輯 **`config.py`**：
```python
MODEL_NAME = "google/gemma-2-2b-it"  # 修改這一行
```

### 模型下載慢
首次使用會下載模型（約 1GB），請耐心等待。

### SQL 生成不正確
1. 使用更明確的表述
2. 指定完整的表格名稱
3. 參考 Schema 說明調整查詢
4. 在 `config.py` 調整 `MODEL_TEMPERATURE`（降低值）

### 模組導入錯誤
確保在專案根目錄運行腳本，或使用 `tools/` 目錄下的工具腳本。

### 查看當前設定
```bash
python config.py  # 顯示所有設定
```

## 主要依賴

- `transformers` - HuggingFace 模型
- `torch` - PyTorch 框架
- `accelerate` - 模型加速和裝置管理
- `pymysql` - MySQL 連接
- `sqlparse` - SQL 解析和驗證
- `cryptography` - SSL 支援
- `pytest` - 測試框架
- `ruff` - 代碼風格檢查

完整依賴見 `requirements.txt`

## 變更日誌

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新歷史。

## 設定哲學

本專案採用 **集中式設定管理**：
- ✅ 所有設定集中在 `config.py`
- ✅ 一個檔案管理所有參數
- ✅ 無需在多個地方修改
- ✅ 清晰的註解和分區
- ✅ 支援環境變數覆蓋（可選）
- ✅ 可執行 `python config.py` 查看當前設定

修改任何設定，只需編輯 `config.py` 即可！

## License

請參閱 [LICENSE](LICENSE) 檔案。
