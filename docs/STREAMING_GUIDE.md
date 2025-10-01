# Streaming 功能指南

## 概述

Streaming 功能讓 SQL 生成過程能夠即時顯示，提供更好的使用者體驗。使用者可以看到模型逐字生成 SQL，而不是等待完整結果。

## 功能特點

1. **即時反饋**：即時看到生成過程
2. **更好的體驗**：減少等待時的不確定感
3. **可中斷**：可以提前看到結果並決定是否繼續
4. **向後兼容**：不影響現有的非 streaming 功能

## 使用方法

### 工具腳本使用（選項 5）

選項 5 是即時查詢生成工具，支援 Streaming 模式：

```bash
python tools/test_generation.py
# 選擇：5
```

#### 選項 5 特點

- **持續互動**：可連續輸入多個查詢，不需要重新啟動
- **模型僅載入一次**：首次輸入時載入模型，之後重複使用
- **即時 Streaming**：逐字顯示生成過程
- **純生成模式**：只生成 SQL，不執行查詢
- **快速迭代**：適合測試不同的查詢表述

#### 使用流程

```
================================================================================
輸入查詢生成 SQL（Streaming 模式）
================================================================================
提示: 輸入 'quit' 或 'q' 返回主選單

請輸入查詢問題: 查詢所有騰訊帳單

初始化模型（僅需一次）...
✓ 模型已載入

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

#### 退出命令

在輸入查詢問題時，可以使用：
- `quit` - 返回主選單
- `q` - 返回主選單（簡寫）
- `exit` - 返回主選單

#### 使用場景

1. **快速測試查詢**：測試不同的查詢表述，找到最佳問法
   ```
   請輸入查詢問題: 查詢帳單
   請輸入查詢問題: 找出所有帳單
   請輸入查詢問題: 顯示全部帳單記錄
   ```

2. **迭代優化**：根據生成結果調整查詢，逐步優化
   ```
   請輸入查詢問題: 查詢成本高的帳單
   # 結果不夠具體
   請輸入查詢問題: 查詢成本超過 1000 的帳單
   # 更好了
   ```

3. **探索模型能力**：測試複雜查詢和邊界情況
   ```
   請輸入查詢問題: 統計每個帳期的平均成本並排序
   請輸入查詢問題: 找出使用代金券最多的前 5 筆記錄
   ```

4. **開發調試**：調整 prompt 和測試不同表述
   ```
   # 測試不同的表述方式
   請輸入查詢問題: 給我看 2025-01 的帳單
   請輸入查詢問題: 顯示 2025 年 1 月的帳單
   請輸入查詢問題: 查詢帳期為 2025-01 的資料
   ```

### 程式化使用

#### 基本 Streaming

```python
from config import FULL_SCHEMA
from src.models.huggingface_model import HuggingFaceModel
from src.services.text_to_sql_service import TextToSQLService

# 初始化
model = HuggingFaceModel(device="cpu")
service = TextToSQLService(model)

# Streaming 生成
query = "查詢所有騰訊帳單"
for token in service.convert_stream(FULL_SCHEMA, query):
    print(token, end="", flush=True)
```

#### 收集完整結果

```python
# 邊顯示邊收集
full_response = []
for token in service.convert_stream(FULL_SCHEMA, query):
    print(token, end="", flush=True)
    full_response.append(token)

# 完整的 SQL
full_sql = "".join(full_response)
print("\n\n完整 SQL:", full_sql)
```

#### 清理和格式化

```python
from src.utils.sql_parser import SQLParser

parser = SQLParser()

# 生成
full_response = []
for token in service.convert_stream(FULL_SCHEMA, query):
    print(token, end="", flush=True)
    full_response.append(token)

# 清理
full_sql = "".join(full_response)
cleaned_sql = parser.clean_sql(full_sql)

print("\n\n清理後的 SQL:")
print(cleaned_sql)
```

## 完整範例

### 範例 1：簡單的 Streaming

```python
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import FULL_SCHEMA
from src.models.huggingface_model import HuggingFaceModel
from src.services.text_to_sql_service import TextToSQLService

# 初始化
model = HuggingFaceModel(device="cpu")
service = TextToSQLService(model)

# Streaming 生成
print("生成中: ", end="", flush=True)
for token in service.convert_stream(FULL_SCHEMA, "查詢所有資料"):
    print(token, end="", flush=True)
print()  # 換行
```

### 範例 2：批量 Streaming

```python
queries = [
    "查詢所有騰訊帳單",
    "找出成本超過 1000 的記錄",
    "統計每個帳期的總成本",
]

for i, query in enumerate(queries, 1):
    print(f"\n{i}. {query}")
    print("-" * 80)
    
    for token in service.convert_stream(FULL_SCHEMA, query):
        print(token, end="", flush=True)
    
    print("\n" + "-" * 80)
```

### 範例 3：互動式 Streaming

```python
while True:
    query = input("\n請輸入查詢 (quit 退出): ").strip()
    
    if query.lower() == "quit":
        break
    
    if not query:
        continue
    
    print("\n生成中:")
    print("-" * 80)
    
    for token in service.convert_stream(FULL_SCHEMA, query):
        print(token, end="", flush=True)
    
    print("\n" + "-" * 80)
```

## API 說明

### HuggingFaceModel.generate_stream()

```python
def generate_stream(
    self, 
    prompt: str, 
    max_tokens: int = 512
) -> Generator[str, None, None]:
    """
    使用 streaming 模式生成文字。
    
    Args:
        prompt: 輸入提示
        max_tokens: 最大生成 token 數
        
    Yields:
        生成的文字 token
    """
```

### TextToSQLService.convert_stream()

```python
def convert_stream(
    self,
    schema: str,
    user_query: str,
    max_tokens: int = 512
) -> Generator[str, None, None]:
    """
    使用 streaming 模式將自然語言轉換為 SQL。
    
    Args:
        schema: 資料庫 schema 描述
        user_query: 使用者的自然語言查詢
        max_tokens: 最大生成 token 數
        
    Yields:
        生成的文字 token
    """
```

## 技術實作

### 使用的技術

- **TextIteratorStreamer**：來自 transformers 庫
- **Threading**：在背景執行生成
- **Generator**：使用 Python generator 進行 streaming

### 工作原理

1. 模型在背景 thread 中生成文字
2. TextIteratorStreamer 即時捕獲生成的 token
3. 主 thread 透過 generator 逐個產出 token
4. 使用者程式即時顯示每個 token

### 效能考量

- **首 token 延遲**：首個 token 可能需要幾秒
- **後續 token**：之後的 token 會快速產出
- **記憶體使用**：與非 streaming 模式相同
- **CPU 使用**：略高（多一個 thread）

## Streaming vs 非 Streaming

### Streaming 模式

優點：
- 即時反饋
- 更好的使用者體驗
- 可提前看到結果

缺點：
- 稍微複雜的程式碼
- 需要處理 token 拼接

適用場景：
- 互動式應用
- 長時間生成
- 需要即時反饋的場合

### 非 Streaming 模式

優點：
- 簡單直接
- 一次獲得完整結果

缺點：
- 等待時間較長
- 沒有進度反饋

適用場景：
- 批次處理
- 自動化腳本
- 不需要使用者互動

## 最佳實踐

### 1. 顯示進度提示

```python
print("生成中", end="", flush=True)
for token in service.convert_stream(schema, query):
    print(token, end="", flush=True)
print()  # 確保換行
```

### 2. 使用分隔線

```python
print("-" * 80)
for token in service.convert_stream(schema, query):
    print(token, end="", flush=True)
print("\n" + "-" * 80)
```

### 3. 錯誤處理

```python
try:
    for token in service.convert_stream(schema, query):
        print(token, end="", flush=True)
except Exception as e:
    print(f"\n生成失敗: {e}")
```

### 4. 收集和清理

```python
full_response = []
for token in service.convert_stream(schema, query):
    print(token, end="", flush=True)
    full_response.append(token)

full_sql = "".join(full_response)
cleaned_sql = parser.clean_sql(full_sql)
```

## 故障排除

### 問題 1：沒有輸出

**原因**：可能缺少 `flush=True`
**解決**：確保使用 `print(token, end="", flush=True)`

### 問題 2：輸出延遲

**原因**：緩衝問題
**解決**：使用 `flush=True` 並確保 stdout 未被重定向

### 問題 3：首 token 很慢

**原因**：模型初始化和處理 prompt
**解決**：這是正常的，首 token 後會加快

## 範例腳本

完整的範例腳本位於：
- `examples/streaming_example.py` - Streaming 使用範例
- `tools/test_generation.py` - 選項 5 使用 Streaming

執行範例：
```bash
python examples/streaming_example.py
```

## 總結

Streaming 功能提供更好的使用者體驗，特別適合：
- 互動式應用
- 需要即時反饋的場景
- 長時間的生成任務

建議在工具腳本和互動式程式中使用 Streaming 模式。

