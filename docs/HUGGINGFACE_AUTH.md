# HuggingFace 授權指南

本文檔說明如何授權存取 HuggingFace 上的 gated models（需要授權的模型）。

## 📋 什麼是 Gated Model？

某些模型（如 Google Gemma 系列）需要使用者明確同意使用條款才能下載。這些模型被稱為 "gated models"。

### 需要授權的模型

| 模型 | 大小 | 質量 | 授權要求 |
|------|------|------|----------|
| `google/gemma-3-1b-it` | 2GB | ⭐⭐⭐ | ✓ 需要 |
| `google/gemma-2-2b-it` | 4GB | ⭐⭐⭐⭐ | ✓ 需要 |
| `meta-llama/Llama-2-7b` | 13GB | ⭐⭐⭐⭐⭐ | ✓ 需要 |

### 無需授權的模型（推薦）

| 模型 | 大小 | 質量 | 授權要求 |
|------|------|------|----------|
| `Qwen/Qwen3-0.6B` | 600MB | ⭐⭐ | ✗ 無需 |
| `Qwen/Qwen2.5-1.5B-Instruct` | 3GB | ⭐⭐⭐⭐ | ✗ 無需 |
| `Qwen/Qwen2.5-3B-Instruct` | 6GB | ⭐⭐⭐⭐⭐ | ✗ 無需 |

## 🔑 如何授權 Gated Models

### 步驟 1：申請模型存取權限

1. 訪問模型頁面（以 Gemma 3 1B 為例）：
   ```
   https://huggingface.co/google/gemma-3-1b-it
   ```

2. 登入您的 HuggingFace 帳號
   - 如果沒有帳號，請先註冊：https://huggingface.co/join

3. 點擊 **"Request Access"** 按鈕
   - 閱讀並同意 Google 的使用條款
   - 通常會立即獲得批准（instant approval）

4. 等待批准通知
   - 大部分模型會立即批准
   - 某些模型可能需要 1-2 天人工審核

### 步驟 2：取得 API Token

1. 訪問 Token 設定頁面：
   ```
   https://huggingface.co/settings/tokens
   ```

2. 點擊 **"New token"** 按鈕

3. 設定 Token：
   - **Name**: 例如 `text-to-sql-local`
   - **Type**: 選擇 **"Read"** 權限
   - **Expiration**: 選擇過期時間（建議選擇 "Never"）

4. 點擊 **"Generate token"**

5. **立即複製 Token**（只會顯示一次！）
   ```
   hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 步驟 3：在本地登入 HuggingFace

#### 方法 1：使用 CLI 登入（推薦）

```bash
# 安裝 huggingface-cli（如果尚未安裝）
pip install huggingface-hub

# 登入
huggingface-cli login
```

系統會提示輸入您的 Token，貼上後按 Enter。

登入成功後會顯示：
```
Login successful
Your token has been saved to ~/.cache/huggingface/token
```

#### 方法 2：設定環境變數

**臨時設定（當前終端有效）：**
```bash
export HUGGING_FACE_HUB_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**永久設定（推薦）：**

在專案的 `.env` 檔案中新增：
```bash
HUGGING_FACE_HUB_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

或在系統環境變數中設定：
```bash
# macOS/Linux - 編輯 ~/.bashrc 或 ~/.zshrc
echo 'export HUGGING_FACE_HUB_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' >> ~/.zshrc
source ~/.zshrc

# macOS/Linux - 或使用專案 .env（需要 python-dotenv）
echo 'HUGGING_FACE_HUB_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' >> .env
```

#### 方法 3：在程式碼中設定

修改 `src/models/huggingface_model.py`，在 `initialize` 方法中新增：

```python
from huggingface_hub import login

def initialize(self):
    """Initialize the model and tokenizer."""
    try:
        # 如果環境變數中有 token，自動登入
        import os
        token = os.getenv("HUGGING_FACE_HUB_TOKEN")
        if token:
            login(token=token, add_to_git_credential=False)
        
        # 原有的初始化程式碼...
        print(f"正在載入模型：{self.model_name}")
        # ...
```

### 步驟 4：驗證授權

```bash
# 測試是否能存取 gated model
python -c "
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('google/gemma-3-1b-it')
print('✓ 授權成功！')
"
```

如果顯示 `✓ 授權成功！`，表示授權設定正確。

## 🚀 使用 Gated Models

### 在 config.py 中設定

```python
# config.py
MODEL_NAME = "google/gemma-3-1b-it"  # 或其他 gated model
```

### 重啟後端

```bash
make web-stop
make web-backend
```

### 首次使用

- 模型會自動下載到 `~/.cache/huggingface/hub/`
- 下載時間取決於模型大小和網速
- 之後使用會直接載入本地快取

## ❌ 常見錯誤

### 錯誤 1：401 Client Error

```
401 Client Error: Cannot access gated repo for url
```

**原因**：未申請模型存取權限或未登入

**解決**：
1. 確認已在 HuggingFace 上申請並獲得存取權限
2. 執行 `huggingface-cli login` 並輸入 Token

### 錯誤 2：403 Forbidden

```
403 Client Error: Forbidden for url
```

**原因**：申請尚未批准或 Token 權限不足

**解決**：
1. 檢查 HuggingFace 信箱是否收到批准通知
2. 確認 Token 類型為 "Read" 權限
3. 重新生成 Token 並登入

### 錯誤 3：Token not found

```
Token is required but not found
```

**原因**：Token 未正確設定

**解決**：
```bash
# 重新登入
huggingface-cli logout
huggingface-cli login

# 或檢查環境變數
echo $HUGGING_FACE_HUB_TOKEN
```

### 錯誤 4：OSError - Disk quota exceeded

```
OSError: [Errno 122] Disk quota exceeded
```

**原因**：磁碟空間不足

**解決**：
1. 清理舊模型快取：
   ```bash
   # 查看快取大小
   du -sh ~/.cache/huggingface/hub/
   
   # 刪除特定模型
   rm -rf ~/.cache/huggingface/hub/models--xxx
   
   # 或使用 huggingface-cli 清理
   huggingface-cli delete-cache
   ```

## 🔒 安全注意事項

1. **不要將 Token 提交到 Git**
   - 確保 `.env` 在 `.gitignore` 中
   - 不要在程式碼中硬編碼 Token

2. **定期更換 Token**
   - 建議每 3-6 個月更換一次
   - 如果懷疑洩露，立即撤銷舊 Token

3. **使用最小權限**
   - 如果只需要下載模型，使用 "Read" 權限即可
   - 避免使用 "Write" 權限

4. **撤銷不需要的 Token**
   - 在 https://huggingface.co/settings/tokens 管理 Token
   - 刪除不再使用的 Token

## 📚 參考資源

- [HuggingFace 官方文檔 - Gated Models](https://huggingface.co/docs/hub/models-gated)
- [HuggingFace Hub Python Library](https://huggingface.co/docs/huggingface_hub/index)
- [Gemma 模型卡片](https://huggingface.co/google/gemma-3-1b-it)

## 💡 建議

如果您只是想快速測試 Text-to-SQL 功能，建議使用無需授權的模型：

1. **快速測試**：`Qwen/Qwen3-0.6B`（600MB，無需授權）
2. **平衡選擇**：`Qwen/Qwen2.5-1.5B-Instruct`（3GB，質量優秀，無需授權）✅ **推薦**
3. **最佳質量**：`Qwen/Qwen2.5-3B-Instruct`（6GB，最高質量，無需授權）

這些模型的質量與 Gemma 相當，且無需額外的授權步驟。

