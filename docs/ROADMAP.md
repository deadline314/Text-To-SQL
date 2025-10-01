# Text-to-SQL 開發路線圖

本文件說明專案的長期發展計劃和功能規劃。

## 已完成功能（v1.0 - v1.2）

### v1.0.0 - 核心功能
- ✅ Text-to-SQL 基本轉換
- ✅ HuggingFace 模型整合
- ✅ MySQL 資料庫連接（SSL）
- ✅ 完整的測試工具集
- ✅ 單元測試框架

### v1.1.0 - 使用者體驗優化
- ✅ 繁體中文化
- ✅ 專案結構優化
- ✅ 工具腳本修復
- ✅ 互動式測試工具

### v1.2.0 - Streaming 和設定管理
- ✅ Streaming 即時輸出
- ✅ 集中式設定管理（config.py）
- ✅ 一鍵安裝（make setup-full）
- ✅ 模型設定簡化
- ✅ 優化的 Prompt 設計

## 開發中（v1.3）

### v1.3.0 - 多模型供應商與系統穩定性

#### 目標
擴展模型支援，提升系統穩定性和可靠性。

#### 主要功能

**1. 多模型供應商支援**

支援三種模型供應商：

| Provider | 模型 | 用途 |
|----------|------|------|
| `local` | HuggingFace 模型 | 離線使用、開發測試 |
| `bedrock` | Claude Sonnet 4/4.5 | 高品質生成、企業應用 |
| `genai` | Gemini 2.5 Pro/Flash | 快速響應、成本優化 |

**實作重點**：
- 統一的模型介面設計
- Provider 工廠模式
- 在 `config.py` 中配置
- 環境變數支援

**2. AWS Bedrock 整合**

支援模型：
- Claude Sonnet 4.0
- Claude Sonnet 4.5

功能：
- boto3 SDK 整合
- AWS 認證管理
- 區域選擇
- 成本追蹤（可選）

**3. Google GenAI 整合**

支援模型：
- Gemini 2.5 Pro（高品質）
- Gemini 2.5 Flash（高速度）

功能：
- google-generativeai SDK 整合
- API Key 管理
- 配額管理
- 速率限制處理

**4. 智慧重試機制**

問題場景：
- API 暫時性錯誤（429, 503）
- 網路超時
- 生成格式錯誤

解決方案：
```python
# 配置示例
RETRY_MAX_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 1.0  # 秒
RETRY_MAX_DELAY = 10.0     # 秒
RETRY_EXPONENTIAL_BASE = 2
RETRY_JITTER = True        # 隨機延遲
```

策略：
- 指數退避（Exponential Backoff）
- 隨機抖動（Jitter）避免同時重試
- 針對不同錯誤類型採取不同策略

**5. 輸出驗證與修復**

驗證項目：
- 檢查是否包含 SQL 關鍵字
- 驗證 ```sql``` 格式
- 語法正確性檢查
- 危險語句檢測

修復措施：
- 自動提取 SQL 部分
- 移除描述性文字
- 格式標準化
- 失敗時重新生成

**6. 錯誤處理優化**

錯誤分類：

| 錯誤類型 | 處理策略 |
|---------|---------|
| 暫時性錯誤 | 重試 |
| 格式錯誤 | 修復或重新生成 |
| 認證錯誤 | 立即失敗，提示用戶 |
| 配額超限 | 等待或切換模型 |
| 語法錯誤 | 重新生成 |

#### 設定範例

```python
# config.py

# Provider 選擇
MODEL_PROVIDER = "local"  # "local", "bedrock", "genai"

# Local Provider (HuggingFace)
LOCAL_MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
LOCAL_MODEL_DEVICE = "cpu"

# Bedrock Provider
BEDROCK_MODEL_ID = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
BEDROCK_REGION = "us-east-1"
AWS_PROFILE = "default"  # 或使用環境變數

# GenAI Provider
GENAI_MODEL_NAME = "gemini-2.5-pro"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 重試設定
RETRY_ENABLED = True
RETRY_MAX_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 1.0
RETRY_MAX_DELAY = 10.0
RETRY_EXPONENTIAL_BASE = 2
RETRY_JITTER = True

# 超時設定
REQUEST_TIMEOUT = 30  # 秒
GENERATION_TIMEOUT = 60  # 秒

# 驗證設定
VALIDATE_SQL_OUTPUT = True
AUTO_RETRY_ON_VALIDATION_FAILURE = True
```

#### 技術債務
- [ ] 統一的錯誤處理機制
- [ ] 日誌系統改進
- [ ] 效能監控和指標收集

#### 測試計劃
- [ ] Provider 切換測試
- [ ] 重試機制測試
- [ ] 錯誤處理測試
- [ ] 整合測試（所有 Provider）

#### 文件更新
- [ ] Provider 使用指南
- [ ] 錯誤處理最佳實踐
- [ ] 成本優化建議
- [ ] 故障排除指南

## 未來版本

### v1.4.0 - 資料庫擴展與 UI

**主要功能**：
- 支援 PostgreSQL
- 支援 SQLite
- 支援 MongoDB（NoSQL to SQL 概念轉換）
- Web UI 介面
- 查詢歷史記錄
- 多模型對比（同時使用多個模型，選擇最佳結果）

**預期時程**：2-3 個月

### v1.5.0 - 智慧化與優化

**主要功能**：
- 自動 Schema 學習（從查詢歷史中學習常見模式）
- 查詢優化建議（效能分析）
- 批次查詢處理
- 查詢快取機制
- SQL to Text（自然語言解釋 SQL）
- 查詢推薦系統

**預期時程**：3-4 個月

### v2.0.0 - 企業級功能

**主要功能**：
- 多租戶支援
- 權限管理系統
- 審計日誌
- 查詢審批流程
- 資料脫敏
- 企業級認證（SSO、LDAP）
- API 限流和配額管理
- 高可用性部署

**預期時程**：6+ 個月

## 長期願景

### 技術願景
- 成為最易用的 Text-to-SQL 解決方案
- 支援所有主流資料庫和模型
- 企業級的穩定性和安全性
- 高度可擴展的架構

### 產品願景
- 降低 SQL 學習門檻
- 提升資料分析效率
- 促進資料民主化
- 安全可控的資料訪問

## 貢獻指南

### 如何參與

1. **提出需求**：在 GitHub Issues 提出功能需求
2. **實作功能**：選擇 Roadmap 中的功能進行開發
3. **提交 PR**：遵循代碼規範提交 Pull Request
4. **測試驗證**：確保測試覆蓋率和功能正確性

### 開發優先級

**高優先級**（v1.3）：
- 多模型供應商支援
- 系統穩定性

**中優先級**（v1.4）：
- 資料庫擴展
- Web UI

**低優先級**（v1.5+）：
- 進階功能
- 企業功能

## 技術棧演進

### 當前技術棧
- Python 3.10+
- HuggingFace Transformers
- PyTorch
- MySQL (pymysql)
- pytest

### v1.3 新增
- boto3（AWS SDK）
- google-generativeai（Google GenAI SDK）
- tenacity（重試機制）

### v1.4 計劃
- FastAPI（Web API）
- React（Web UI）
- PostgreSQL, SQLite 驅動
- Redis（快取）

## 反饋與討論

歡迎在以下渠道提供反饋：
- GitHub Issues：功能需求和 Bug 報告
- GitHub Discussions：設計討論和問題交流

## 總結

Text-to-SQL 專案致力於提供強大、穩定、易用的自然語言轉 SQL 解決方案。
我們歡迎社群的參與和貢獻，共同打造更好的產品！

---

**最後更新**：2025-10-01  
**當前版本**：v1.2.0  
**下一版本**：v1.3.0（開發中）

