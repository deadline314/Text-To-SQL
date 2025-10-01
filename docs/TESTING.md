# 測試指南

本專案提供完整的測試工具集，幫助你驗證 Text-to-SQL 功能。

## 測試工具總覽

| 工具 | 功能 | 使用時機 |
|------|------|----------|
| `test_connection.py` | 測試資料庫連接 | 首次設定、排查問題 |
| `quick_test.py` | 快速 SQL 生成測試 | 驗證功能正常 |
| `test_generation.py` | 完整互動式測試 | 日常開發、深度測試 |
| `list_databases.py` | 探索資料庫結構 | 了解資料庫內容 |

## 快速開始

### 1. 測試資料庫連接

```bash
python tools/test_connection.py
```

**功能**：
- 驗證資料庫連接是否正常
- 顯示 MySQL 版本
- 最基礎的測試，建議最先執行

**預期輸出**：
```
測試資料庫連接...
✓ 資料庫連接成功！
✓ 查詢執行成功！
Version: 8.0.26-google
```

### 2. 快速 SQL 生成測試

```bash
python tools/quick_test.py
```

**功能**：
- 快速測試 SQL 生成功能
- 自動運行 3 個預設查詢
- 不需要互動，適合快速驗證

**測試查詢**：
1. 查詢所有騰訊帳單
2. 查詢 2025-01 帳期的資料
3. 統計每個帳期的總成本

**預期輸出**：
```
測試 1/3: 查詢所有騰訊帳單
生成的 SQL:
SELECT * FROM tencent_bill;
---
測試 2/3: 查詢 2025-01 帳期的資料
生成的 SQL:
SELECT * FROM tencent_bill WHERE bill_month = '2025-01';
---
測試 3/3: 統計每個帳期的總成本
生成的 SQL:
SELECT bill_month, SUM(cost) as total_cost 
FROM tencent_bill 
GROUP BY bill_month;
```

### 3. 完整測試工具（推薦）

```bash
python tools/test_generation.py
```

**功能**：
- 完整的互動式測試工具
- 支援自訂查詢
- 可選擇生成或執行 SQL
- 最推薦使用的測試工具

### 4. 探索資料庫

```bash
python tools/list_databases.py
```

**功能**：
- 列出所有可用的資料庫
- 查看每個資料庫中的表格
- 顯示表格的資料筆數
- 查看表格的範例資料

## test_generation.py 詳細說明

這是最完整的互動式測試工具，提供六個選項。

### 主選單

```
選擇操作:
1. 查看所有資料庫
2. 查看指定資料庫的表格
3. 測試 SQL 生成（僅生成）
4. 測試 SQL 生成並執行（完整流程）
5. 即時查詢生成（輸入文字生成 SQL）
6. 退出

請輸入選項 (1-6 或 q 退出):
```

**快速退出**：直接輸入 `q` 即可退出，不需要選擇 6。

### 選項 1：查看所有資料庫

**功能**：列出伺服器上所有可用的資料庫。

**使用場景**：
- 首次使用，了解有哪些資料庫
- 選擇要查詢的目標資料庫

**輸出範例**：
```
可用的資料庫:
1. information_schema
2. mysql
3. performance_schema
4. staging-client-tls
5. sys
```

### 選項 2：查看指定資料庫的表格

**功能**：查看指定資料庫中的所有表格及其資料筆數。

**使用方式**：
```
請輸入資料庫名稱: staging-client-tls
```

**輸出範例**：
```
資料庫 'staging-client-tls' 中的表格:
1. tencent_bill (123 筆)
2. global_bill (456 筆)
3. global_bill_l3 (789 筆)
```

**使用場景**：
- 確認表格名稱
- 查看資料量
- 規劃查詢策略

### 選項 3：測試 SQL 生成（僅生成）

**功能**：僅生成 SQL，不執行。適合驗證 SQL 語法和品質。

**測試查詢**：
1. 查詢所有騰訊帳單
2. 查詢 2025-01 帳期的資料
3. 統計每個帳期的總成本

**使用場景**：
- 驗證 SQL 生成品質
- 學習生成的 SQL 語法
- 安全測試（不影響資料庫）

**輸出範例**：
```
測試 1/3: 查詢所有騰訊帳單
生成的 SQL:
SELECT * FROM tencent_bill;
---
```

### 選項 4：測試 SQL 生成並執行（完整流程）

**功能**：生成 SQL 並執行，顯示查詢結果。

**流程**：
1. 生成 SQL
2. 顯示生成的 SQL
3. 詢問是否執行
4. 執行並顯示結果（前 5 筆）

**使用場景**：
- 完整功能測試
- 驗證查詢結果正確性
- 實際應用模擬

**輸出範例**：
```
測試 1/3: 查詢所有騰訊帳單
生成的 SQL:
SELECT * FROM tencent_bill;

是否執行這個查詢? (y/n): y

執行結果:
查詢成功！找到 123 筆資料
前 5 筆資料:
{'id': '...', 'tencent_id': '...', 'cost': 1234.56, ...}
{'id': '...', 'tencent_id': '...', 'cost': 2345.67, ...}
...
```

### 選項 5：即時查詢生成（Streaming 模式）

**功能**：持續互動模式，支援自訂查詢，使用 Streaming 即時顯示生成過程。

**特點**：
- 可連續輸入多個查詢
- 模型僅載入一次（首次輸入時）
- 即時顯示生成過程
- 純生成模式，不執行 SQL
- 輸入 `quit`、`q` 或 `exit` 返回主選單

**使用方式**：
```
請輸入查詢問題: 查詢所有騰訊帳單
生成中
--------------------------------------------------------------------------------
SELECT * FROM tencent_bill;  # 逐字即時顯示
--------------------------------------------------------------------------------

請輸入查詢問題: 查詢 2025-01 帳期的資料
生成中
--------------------------------------------------------------------------------
SELECT * FROM tencent_bill WHERE bill_month = '2025-01';
--------------------------------------------------------------------------------

請輸入查詢問題: quit
返回主選單...
```

**使用場景**：
- 快速測試多個查詢
- 即時看到生成過程
- 調試和優化 prompt
- 探索模型能力

**優勢**：
- 模型只載入一次，之後生成很快
- 即時反饋，更好的使用體驗
- 可以持續測試，不需要重複選擇選單
- Streaming 顯示讓過程透明

### 選項 6：退出

正常退出程式。

**替代方式**：在主選單直接輸入 `q` 也可以退出。

## 使用建議

### 首次使用流程

1. **測試連接**（必須）
   ```bash
   python tools/test_connection.py
   ```

2. **探索資料庫**（建議）
   ```bash
   python tools/list_databases.py
   # 或在 test_generation.py 中選擇選項 1 和 2
   ```

3. **快速測試**（建議）
   ```bash
   python tools/quick_test.py
   ```

4. **完整測試**（深度測試）
   ```bash
   python tools/test_generation.py
   # 選擇選項 3 或 4
   ```

5. **自訂查詢**（實際使用）
   ```bash
   python tools/test_generation.py
   # 選擇選項 5，持續測試
   ```

### 日常開發流程

```bash
# 1. 修復代碼風格
make fix

# 2. 運行單元測試
make test

# 3. 快速功能測試
python tools/quick_test.py

# 4. 自訂查詢測試
python tools/test_generation.py  # 選項 5
```

### 問題排查流程

如果遇到問題，按順序檢查：

1. **連接問題**
   ```bash
   python tools/test_connection.py
   ```
   檢查：SSL 證書、網路、設定檔

2. **SQL 生成問題**
   ```bash
   python tools/test_generation.py  # 選項 3
   ```
   檢查：生成的 SQL 語法、邏輯

3. **查詢執行問題**
   ```bash
   python tools/test_generation.py  # 選項 4
   ```
   檢查：SQL 執行結果、資料庫狀態

## 測試技巧

### 1. 測試 SQL 品質

使用選項 3 僅生成 SQL，專注於驗證語法和邏輯：
```bash
python tools/test_generation.py  # 選項 3
```

### 2. 快速迭代測試

使用選項 5 持續測試多個查詢：
```bash
python tools/test_generation.py  # 選項 5
# 連續輸入多個查詢，快速驗證
```

### 3. 完整流程驗證

使用選項 4 驗證從生成到執行的完整流程：
```bash
python tools/test_generation.py  # 選項 4
```

### 4. Streaming 體驗

選項 5 現在使用 Streaming 模式，可以即時看到生成過程：
- 觀察模型的生成邏輯
- 提前發現錯誤
- 更好的互動體驗

## 常見問題

### Q: 首次運行很慢？

**A**: 首次使用會下載 Qwen/Qwen2.5-0.5B-Instruct 模型（約 1GB），請耐心等待。之後會使用快取，速度會快很多。

### Q: 連接失敗？

**A**: 檢查清單：
1. SSL 證書是否已解壓：`make setup-certs`
2. 網路是否正常
3. `.env` 設定是否正確
4. 資料庫名稱是否存在（可以留空）

### Q: SQL 生成不正確？

**A**: 改進建議：
1. 使用更明確的表述
2. 指定完整的表格名稱
3. 參考 Schema 說明
4. 使用選項 5 多次測試不同表述

### Q: 如何測試自訂查詢？

**A**: 使用選項 5：
```bash
python tools/test_generation.py  # 選項 5
請輸入查詢問題: <你的查詢>
```

### Q: 選項 5 的模型載入時間？

**A**: 模型僅在第一次輸入查詢時載入一次，之後的查詢會直接使用已載入的模型，速度很快。

### Q: Streaming 沒有逐字顯示？

**A**: 確保：
1. 使用選項 5（Streaming 模式）
2. 終端支援即時輸出
3. 沒有重定向輸出

## 進階使用

### 批次測試

修改 `tools/quick_test.py` 添加更多測試查詢：

```python
queries = [
    "查詢所有騰訊帳單",
    "查詢 2025-01 帳期的資料",
    "統計每個帳期的總成本",
    # 添加更多查詢
    "查詢成本超過 1000 的記錄",
    "找出使用最多的產品",
]
```

### 自動化測試

整合到 CI/CD 流程：

```bash
# 在 CI 腳本中
make setup
python tools/test_connection.py || exit 1
python tools/quick_test.py || exit 1
make test || exit 1
```

### 效能測試

使用選項 5 測試多次生成的時間：
```bash
python tools/test_generation.py  # 選項 5
# 輸入同一查詢多次，觀察時間
```

## 測試覆蓋率

查看單元測試覆蓋率：
```bash
make test
# 會顯示覆蓋率報告
```

目標覆蓋率：> 65%

## 相關文件

- [Streaming 功能指南](STREAMING_GUIDE.md) - 選項 5 的詳細說明
- [系統架構](ARCHITECTURE.md) - 了解系統設計
- [安裝設定](SETUP.md) - 安裝和設定指南

## 總結

測試工具使用順序：
1. `test_connection.py` - 驗證連接 ✓
2. `list_databases.py` - 了解資料庫 ✓
3. `quick_test.py` - 快速驗證 ✓
4. `test_generation.py` 選項 3 - SQL 品質 ✓
5. `test_generation.py` 選項 5 - 持續測試 ✓
6. `test_generation.py` 選項 4 - 完整流程 ✓

推薦日常使用：`test_generation.py` 選項 5（Streaming 模式）
