# Multi-Provider 使用指南

本指南說明如何在 Text-to-SQL 專案中使用不同的模型供應商（Provider）。

## 目錄

- [支援的 Provider](#支援的-provider)
- [安裝依賴](#安裝依賴)
- [設定方式](#設定方式)
- [使用方法](#使用方法)
- [錯誤排除](#錯誤排除)

## 支援的 Provider

### 1. Local (本地 HuggingFace 模型)

**特點**：
- 完全離線運行
- 無需 API 費用
- CPU 可運行
- 適合開發和測試

**預設模型**：`Qwen/Qwen2.5-0.5B-Instruct`

### 2. Bedrock (AWS Claude 模型)

**特點**：
- 高品質 SQL 生成
- 支援 Streaming
- 需要 AWS 帳號
- 按使用量付費

**支援模型**：
- `us.anthropic.claude-sonnet-4-20250514-v1:0` (Claude Sonnet 4)
- `global.anthropic.claude-sonnet-4-5-20250929-v1:0` (Claude Sonnet 4.5)

### 3. GenAI (Google Gemini 模型)

**特點**：
- 快速響應
- 成本優化
- 需要 Google Cloud 專案
- 按使用量付費

**支援模型**：
- `gemini-2.5-pro` (高品質)
- `gemini-2.5-flash` (高速度)

## 安裝依賴

### Local Provider（預設已安裝）

```bash
# 基本依賴已在 requirements.txt 中
pip install -r requirements.txt
```

### AWS Bedrock

```bash
# 安裝 Bedrock 依賴
pip install boto3 botocore tenacity

# 或使用 Makefile
make install-bedrock
```

### Google GenAI

```bash
# 安裝 GenAI 依賴
pip install google-generativeai tenacity

# 或使用 Makefile
make install-genai
```

### 所有 Provider

```bash
pip install boto3 botocore google-generativeai tenacity
```

## 設定方式

### 方法 1：修改 config.py（推薦）

編輯 `config.py` 檔案：

```python
# Provider 選擇
MODEL_PROVIDER = "bedrock"  # "local", "bedrock", "genai"

# AWS Bedrock 設定
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
BEDROCK_REGION = "us-east-1"

# Google GenAI 設定
GENAI_MODEL_NAME = "gemini-2.5-pro"
GOOGLE_API_KEY = "your-api-key"
```

### 方法 2：使用環境變數

編輯 `.env` 檔案：

```bash
# Provider 選擇
MODEL_PROVIDER=bedrock

# AWS 設定
AWS_REGION=us-east-1
AWS_PROFILE=default

# Google 設定
GOOGLE_API_KEY=your-api-key-here
```

### 方法 3：命令列參數（最靈活）

使用命令列參數臨時切換 Provider，不需要修改設定檔。

## 使用方法

### 1. 使用本地模型（預設）

```bash
# 使用預設本地模型
python tools/test_generation.py

# 或
make gen
```

### 2. 使用 AWS Bedrock

**使用預設模型**：

```bash
python tools/test_generation.py -bedrock

# 或
make gen ARGS=-bedrock
```

**指定模型**：

```bash
python tools/test_generation.py -bedrock us.anthropic.claude-sonnet-4-20250514-v1:0

# 或
make gen ARGS="-bedrock us.anthropic.claude-sonnet-4-20250514-v1:0"
```

**AWS 認證設定**：

方式 1：使用 AWS CLI 設定檔

```bash
aws configure --profile your-profile
export AWS_PROFILE=your-profile
```

方式 2：使用環境變數

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1
```

### 3. 使用 Google GenAI

**使用預設模型**：

```bash
python tools/test_generation.py -genai

# 或
make gen ARGS=-genai
```

**指定模型**：

```bash
python tools/test_generation.py -genai gemini-2.5-flash

# 或
make gen ARGS="-genai gemini-2.5-flash"
```

**API Key 設定**：

在 `.env` 檔案中設定：

```bash
GOOGLE_API_KEY=your-api-key-here
```

或使用環境變數：

```bash
export GOOGLE_API_KEY=your-api-key-here
```

### 4. Quick Test 工具

```bash
# 本地模型
python tools/quick_test.py

# AWS Bedrock
python tools/quick_test.py -bedrock

# Google GenAI
python tools/quick_test.py -genai gemini-2.5-flash
```

### 5. 程式化使用

```python
from src.models.model_factory import create_model
from src.services.text_to_sql_service import TextToSQLService

# 建立模型
model = create_model(
    provider="bedrock",
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0"
)

# 建立服務
service = TextToSQLService(model)

# 生成 SQL
schema = "CREATE TABLE users (id INT, name VARCHAR(100));"
query = "查詢所有使用者"
sql = service.convert(schema, query)
print(sql)

# Streaming 生成
for token in service.convert_stream(schema, query):
    print(token, end="", flush=True)
```

## 錯誤排除

### 1. boto3 未安裝

**錯誤訊息**：
```
boto3 is not installed. Install with: pip install boto3 botocore
```

**解決方法**：
```bash
pip install boto3 botocore tenacity
```

### 2. google-generativeai 未安裝

**錯誤訊息**：
```
google-generativeai is not installed. Install with: pip install google-generativeai
```

**解決方法**：
```bash
pip install google-generativeai tenacity
```

### 3. AWS 認證失敗

**錯誤訊息**：
```
Failed to initialize Bedrock client: Unable to locate credentials
```

**解決方法**：
1. 設定 AWS 認證：
   ```bash
   aws configure
   ```

2. 或設定環境變數：
   ```bash
   export AWS_ACCESS_KEY_ID=your-key
   export AWS_SECRET_ACCESS_KEY=your-secret
   ```

3. 檢查 IAM 權限（需要 `bedrock:InvokeModel` 權限）

### 4. Google API Key 未設定

**錯誤訊息**：
```
Google API key is required. Set GOOGLE_API_KEY in .env or pass api_key parameter.
```

**解決方法**：
1. 在 `.env` 中設定：
   ```bash
   GOOGLE_API_KEY=your-api-key
   ```

2. 或使用環境變數：
   ```bash
   export GOOGLE_API_KEY=your-api-key
   ```

### 5. 區域不支援

**錯誤訊息**：
```
Could not connect to the endpoint URL
```

**解決方法**：
確認模型在該區域可用，並更新設定：

```python
# config.py
BEDROCK_REGION = "us-east-1"  # 或其他支援的區域
```

常見的 Bedrock 區域：
- `us-east-1` (US East)
- `us-west-2` (US West)
- `eu-west-1` (EU Ireland)
- `ap-southeast-1` (Singapore)

### 6. 參數格式錯誤

**錯誤訊息**：
```
Invalid provider: xxx. Valid options: local, bedrock, genai
```

**解決方法**：
確認參數格式正確：

```bash
# 正確
python tools/test_generation.py -bedrock
python tools/test_generation.py -bedrock model-id
python tools/test_generation.py -genai

# 錯誤
python tools/test_generation.py bedrock  # 缺少 -
python tools/test_generation.py --bedrock  # 使用 -- 而非 -
```

## 成本考量

### AWS Bedrock

Claude Sonnet 4 價格（以 us-east-1 為例）：
- Input: ~$3 / 1M tokens
- Output: ~$15 / 1M tokens

估算：
- 每次 SQL 生成約 500-1000 tokens
- 100 次生成 ≈ $0.10 - $0.20

### Google GenAI

Gemini 2.5 價格：
- Pro: ~$3.5 / 1M input tokens, ~$10.5 / 1M output tokens
- Flash: ~$0.075 / 1M input tokens, ~$0.30 / 1M output tokens

估算：
- Flash 更適合高頻使用
- 100 次生成（Flash）≈ $0.01 - $0.03

### 本地模型

- 完全免費
- 僅需 GPU/CPU 運算資源

## 效能比較

| Provider | 品質 | 速度 | 成本 | 離線 |
|----------|------|------|------|------|
| Local    | ⭐⭐⭐ | ⭐⭐ | 免費 | ✅ |
| Bedrock  | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 中等 | ❌ |
| GenAI (Pro) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 中等 | ❌ |
| GenAI (Flash) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 低 | ❌ |

## 建議使用場景

### 開發和測試
- **推薦**: Local
- **原因**: 免費、快速迭代、無需網路

### 生產環境（高品質）
- **推薦**: Bedrock (Claude Sonnet 4.5) 或 GenAI (Gemini 2.5 Pro)
- **原因**: 最高品質的 SQL 生成

### 生產環境（高頻率）
- **推薦**: GenAI (Gemini 2.5 Flash)
- **原因**: 成本低、速度快、品質穩定

### 離線環境
- **推薦**: Local
- **原因**: 唯一選擇

## 進階設定

### 重試機制

在 `config.py` 中設定：

```python
# 重試設定（適用於 Bedrock 和 GenAI）
RETRY_ENABLED = True
RETRY_MAX_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 1.0  # 秒
RETRY_MAX_DELAY = 10.0
RETRY_EXPONENTIAL_BASE = 2
RETRY_JITTER = True  # 隨機抖動
```

### 超時設定

```python
REQUEST_TIMEOUT = 30  # 秒
GENERATION_TIMEOUT = 60  # 秒
```

### 驗證設定

```python
VALIDATE_SQL_OUTPUT = True  # 自動驗證 SQL 格式
AUTO_RETRY_ON_VALIDATION_FAILURE = True  # 失敗時重試
```

## 相關文件

- [README.md](../README.md) - 專案總覽
- [ROADMAP.md](ROADMAP.md) - 開發路線圖
- [SETUP.md](SETUP.md) - 安裝設定指南
- [TESTING.md](TESTING.md) - 測試工具說明

## 支援

如有問題或建議，請：
1. 查看本文件的錯誤排除章節
2. 檢查 [FAQ](../README.md#常見問題)
3. 提交 GitHub Issue

---

**最後更新**：2025-10-01  
**適用版本**：v1.3.0+

