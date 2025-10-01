# 環境變數設定指南

本專案使用 `.env` 檔案管理所有機密資訊和設定。這份文件說明如何設定和使用環境變數。

## 自動載入 .env

### 方法 1：使用 python-dotenv（推薦）✅

專案已內建 `python-dotenv`，會自動載入 `.env` 檔案。

**工作原理**：
- `config.py` 在最上方呼叫 `load_dotenv()`
- 所有 Python 程式都 import `config.py`
- `.env` 的內容會自動載入到環境變數

**優點**：
- ✅ 自動化，無需手動操作
- ✅ 跨平台（Windows/Mac/Linux）
- ✅ 開發和生產環境一致
- ✅ 程式啟動時自動載入

**使用方式**：
```bash
# 直接運行即可，無需額外設定
python tools/test_generation.py
make gen
```

### 方法 2：Shell 手動載入

如果你想在 Shell 中也能使用這些環境變數：

**Bash/Zsh**:
```bash
# 一次性載入
export $(cat .env | grep -v '^#' | xargs)

# 或使用 source（需要修改格式）
source .env  # 需要 .env 每行都是 export KEY=VALUE
```

**Fish Shell**:
```bash
export (cat .env | grep -v '^#')
```

**缺點**：
- 需要每次開啟終端時手動執行
- 語法在不同 Shell 可能不同

### 方法 3：使用 direnv（進階）

`direnv` 是一個工具，可以在進入專案目錄時自動載入環境變數。

**安裝**：
```bash
# macOS
brew install direnv

# Ubuntu/Debian
sudo apt-get install direnv

# 添加到 shell 設定
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc  # Bash
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc    # Zsh
```

**使用**：
```bash
# 建立 .envrc 檔案
cat > .envrc << 'EOF'
dotenv
EOF

# 允許載入
direnv allow
```

**優點**：
- 進入目錄自動載入
- 離開目錄自動卸載
- 支援多個專案不同設定

**缺點**：
- 需要額外安裝和設定
- 需要學習新工具

### 方法 4：Conda 環境變數

如果使用 Conda，可以將環境變數設定到 Conda 環境中。

**設定**：
```bash
# 啟動 conda 環境
conda activate t2s

# 設定環境變數
conda env config vars set AWS_ACCESS_KEY_ID=your-key
conda env config vars set AWS_SECRET_ACCESS_KEY=your-secret
conda env config vars set GCP_API_KEY=your-api-key

# 重新啟動環境使其生效
conda deactivate
conda activate t2s

# 查看設定
conda env config vars list
```

**優點**：
- 環境變數與 Conda 環境綁定
- 切換環境時自動切換變數
- 不需要 .env 檔案

**缺點**：
- 設定過程繁瑣
- 機密資訊儲存在 Conda 設定中
- 不適合團隊協作

### 方法 5：IDE 設定（PyCharm/VSCode）

**PyCharm**：
1. Run → Edit Configurations
2. Environment variables → 點擊資料夾圖示
3. 選擇 Load from file → 選擇 `.env`

**VSCode**：
在 `.vscode/launch.json` 中設定：
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

**優點**：
- IDE 內建支援
- Debug 時也能使用

**缺點**：
- 只在 IDE 內有效
- 命令列執行無效

## 推薦方案

### 🌟 最佳實踐（目前使用的方法）

**使用 python-dotenv（方法 1）**

這是最簡單且最可靠的方法：

1. `.env` 檔案放在專案根目錄
2. `config.py` 自動載入 `.env`
3. 所有 Python 程式都能讀取

**不需要任何額外操作！** ✨

### 檢查環境變數是否載入

```bash
# 方式 1: 使用 Python
python -c "import config; print(config.DB_HOST)"

# 方式 2: 查看設定摘要
python config.py

# 方式 3: 在程式中檢查
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DB_HOST'))"
```

## .env 檔案範例

```bash
# ============================================================================
# 資料庫設定 (Database Configuration)
# ============================================================================
DB_HOST=localhost
DB_PORT=0000
DB_USER=user
DB_PASSWORD=your-password
# DB_NAME=  # 留空表示不指定資料庫

# SSL 證書路徑
DB_SSL_CA=./server-cert/server-ca.pem
DB_SSL_CERT=./server-cert/client-cert.pem
DB_SSL_KEY=./server-cert/client-key.pem

# ============================================================================
# AWS Bedrock 設定 (AWS Bedrock Configuration)
# ============================================================================
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
# BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# ============================================================================
# Google GenAI 設定 (Google GenAI Configuration)
# ============================================================================
GCP_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# GENAI_MODEL_NAME=gemini-2.5-flash

# ============================================================================
# 模型設定 (Model Configuration) - 可選
# ============================================================================
# MODEL_NAME=Qwen/Qwen2.5-0.5B-Instruct
# MODEL_DEVICE=cpu
# MODEL_TEMPERATURE=0.1
# MODEL_TOP_P=0.9
# MODEL_PROVIDER=local
```

## 常見問題

### Q: .env 檔案在哪裡？

A: 在專案根目錄（與 `config.py` 同一層）。

### Q: 為什麼我的環境變數沒有載入？

A: 檢查以下幾點：
1. `.env` 檔案是否存在
2. 檔案格式是否正確（`KEY=VALUE`，無空格）
3. 是否有註解符號 `#` 在行首
4. 檔案編碼是否為 UTF-8
5. 是否有執行 `load_dotenv()`

### Q: 可以有多個 .env 檔案嗎？

A: 可以！常見的做法：
- `.env` - 本地開發
- `.env.production` - 生產環境
- `.env.test` - 測試環境

在 `config.py` 中指定：
```python
from dotenv import load_dotenv

# 根據環境載入不同檔案
env = os.getenv("ENV", "development")
if env == "production":
    load_dotenv(".env.production")
elif env == "test":
    load_dotenv(".env.test")
else:
    load_dotenv()  # 預設 .env
```

### Q: .env 中的值可以有空格嗎？

A: 可以，但建議使用引號：
```bash
# 沒有空格
DB_HOST=localhost

# 有空格，使用引號
DB_PASSWORD="my password with spaces"
DB_NOTE='This is a note'
```

### Q: 如何在不同環境使用不同設定？

A: 方法 1 - 使用環境變數覆蓋：
```bash
# .env 有預設值
DB_HOST=localhost

# 在特定環境覆蓋
export DB_HOST=production-server
python tools/test_generation.py
```

方法 2 - 使用不同的 .env 檔案（見上方）

### Q: .env 會被提交到 Git 嗎？

A: **不會！** `.env` 已在 `.gitignore` 中，確保機密資訊不會外洩。

### Q: 團隊成員如何獲得 .env 設定？

A: 
1. 分享 `.env.example`（無機密資訊）
2. 團隊成員複製並填入自己的值：
   ```bash
   cp .env.example .env
   # 然後編輯 .env
   ```
3. 透過安全管道（如密碼管理器）分享真實的機密資訊

## 安全性建議

1. ✅ **永遠不要提交 .env 到 Git**
2. ✅ **定期輪換 API Keys 和密碼**
3. ✅ **不同環境使用不同的 credentials**
4. ✅ **限制 API Key 的權限範圍**
5. ✅ **使用密碼管理器儲存機密資訊**
6. ❌ **不要在程式碼中硬編碼機密資訊**
7. ❌ **不要在日誌中輸出機密資訊**
8. ❌ **不要透過不安全的管道分享機密資訊**

## 生產環境建議

在生產環境中，建議使用更安全的方式管理機密資訊：

1. **AWS Secrets Manager**
2. **Google Secret Manager**
3. **Azure Key Vault**
4. **HashiCorp Vault**
5. **Kubernetes Secrets**

但對於開發和小型專案，`.env` + `python-dotenv` 已經足夠安全且方便。

## 總結

**本專案使用 python-dotenv，已經自動載入 .env，無需額外設定！**

只需要：
1. 複製 `.env.example` 到 `.env`
2. 填入你的機密資訊
3. 執行程式即可

簡單、安全、有效！✨

---

**相關文件**：
- [README.md](../README.md)
- [SETUP.md](SETUP.md)
- [PROVIDER_GUIDE.md](PROVIDER_GUIDE.md)

