# 變更日誌

所有重要變更都會記錄在此檔案中。

## [1.2.0] - 2025-10-01

### 新增
- **Streaming 支援**：SQL 生成支援流式輸出
  - 新增 `HuggingFaceModel.generate_stream()` 方法
  - 新增 `TextToSQLService.convert_stream()` 方法
  - 選項 5 現在使用 Streaming 模式
  - 即時顯示生成過程，提供更好的使用者體驗
  - 向後相容，保留原有的非 streaming 方法

- **快速退出功能**
  - 主選單支援 `q` 快速退出
  - 不需要選擇 6 再確認

### 文件
- 新增 `docs/STREAMING_GUIDE.md` - Streaming 功能完整指南
- 新增 `examples/streaming_example.py` - Streaming 使用範例
- 整合並精簡所有 markdown 文件
- 優化專案根目錄和 docs/ 目錄結構

## [1.1.0] - 2025-10-01

### 新增
- **選項 5 重新設計**：即時查詢生成功能
  - 持續互動模式，可連續輸入多個查詢
  - 模型僅載入一次，提高效率
  - 純生成模式，專注於 SQL 品質
  - 支援 quit/q/exit 命令返回主選單

### 修復
- 修復所有 tools/ 腳本的模組導入問題
- 添加 sys.path 修改支援正確的模組解析
- 更新 pyproject.toml 忽略 E402 規則

### 語言
- 將所有簡體中文轉換為繁體中文
- 覆蓋範圍：
  - README.md 和所有文件
  - 代碼註釋
  - 測試工具輸出

### 專案結構優化
- 創建 `tools/` 目錄整合測試工具
  - `test_connection.py` - 測試資料庫連接
  - `quick_test.py` - 快速 SQL 生成測試
  - `test_generation.py` - 完整互動式測試
  - `list_databases.py` - 探索資料庫
  
- 創建 `docs/` 目錄整合文件
  - `SETUP.md` - 安裝設定指南
  - `TESTING.md` - 測試指南
  - `ARCHITECTURE.md` - 系統架構說明
  - `PROJECT_SUMMARY.md` - 專案總結
  - `STREAMING_GUIDE.md` - Streaming 功能指南

- 創建 `examples/` 目錄存放範例
  - `basic_usage.py` - 基本使用範例
  - `streaming_example.py` - Streaming 使用範例

## [1.0.0] - 2025-10-01

### 核心功能
- Text-to-SQL 轉換功能
- 模組化設計，介面抽象
- HuggingFace 模型整合

### 模型
- 支援 Qwen/Qwen2.5-0.5B-Instruct 模型
- CPU 可運行
- 易於更換其他 HuggingFace 模型

### 資料庫
- MySQL 資料庫連接（SSL 加密）
- 支援三個騰訊雲帳單表
  - `tencent_bill` - 騰訊帳單主表
  - `global_bill` - 全球帳單表
  - `global_bill_l3` - 全球帳單明細表
- 查詢執行和結果顯示
- SSL 證書自動解壓功能

### 測試
- 完整的單元測試套件（pytest）
- 測試覆蓋率 > 65%
- 互動式測試工具
- 資料庫探索工具

### 開發工具
- Ruff 代碼風格檢查
- Makefile 命令簡化
- pytest 測試框架
- 環境變數設定支援

### 文件
- 完整的 README
- 詳細的設定指南
- 測試工具說明
- 系統架構文件

## 版本說明

版本號格式：`主版本.次版本.修訂版本`

- **主版本**：重大變更，可能不向後相容
- **次版本**：新增功能，向後相容
- **修訂版本**：錯誤修復，向後相容

## 升級指南

### 從 1.1.0 升級到 1.2.0

1. 更新依賴：
```bash
git pull
make install
```

2. 新功能：
- 使用 `service.convert_stream()` 體驗 Streaming 輸出
- 在 `test_generation.py` 選單中直接輸入 `q` 快速退出

3. 相容性：
- 所有現有代碼無需修改
- 原有的 `convert()` 方法保持不變

### 從 1.0.0 升級到 1.1.0

1. 更新依賴：
```bash
git pull
make install
```

2. 專案結構變更：
- 測試腳本移至 `tools/` 目錄
- 文件移至 `docs/` 目錄
- 更新任何硬編碼的路徑

3. 語言變更：
- 所有輸出現在是繁體中文
- 確認任何文字比對邏輯

## 未來計劃

### 1.3.0（計劃中）

#### 多模型供應商支援
- [ ] **新增 AWS Bedrock 整合**
  - 支援 Claude Sonnet 4.0
  - 支援 Claude Sonnet 4.5
  - 透過 boto3 SDK 連接

- [ ] **新增 Google GenAI 整合**
  - 支援 Gemini 2.5 Pro
  - 支援 Gemini 2.5 Flash
  - 透過 google-generativeai SDK 連接

- [ ] **Provider 選項系統**
  - `local` - 本地 HuggingFace 模型（現有功能）
  - `bedrock` - AWS Bedrock Claude 模型
  - `genai` - Google GenAI Gemini 模型
  - 在 `config.py` 中統一設定

#### 系統穩定性增強
- [ ] **智慧重試機制**
  - 生成失敗時自動重試
  - 隨機延遲避免頻率限制
  - 可配置最大重試次數

- [ ] **輸出驗證與修復**
  - 檢測非 SQL 格式的輸出
  - 自動清理和修正常見格式錯誤
  - 驗證失敗時觸發重試
  - 詳細的錯誤日誌記錄

- [ ] **錯誤處理優化**
  - 區分暫時性錯誤和永久性錯誤
  - 針對不同錯誤類型採取不同策略
  - 友善的錯誤訊息提示

#### 設定管理
- [ ] Provider 相關設定整合到 `config.py`
  - AWS 認證設定
  - Google API Key 設定
  - 重試參數設定
  - 超時設定

### 1.4.0（計劃中）
- [ ] 查詢歷史記錄功能
- [ ] 多模型對比功能（同時使用多個模型生成，選擇最佳結果）
- [ ] SQL 執行計劃分析
- [ ] Web UI 介面

### 1.5.0（規劃中）
- [ ] 查詢優化建議（效能分析）
- [ ] 批次查詢處理
- [ ] 查詢快取機制
- [ ] 自然語言解釋 SQL（SQL to Text）

## 貢獻

如有問題或建議，歡迎提出 Issue 或 Pull Request。
