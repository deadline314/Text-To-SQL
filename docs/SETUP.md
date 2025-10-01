# 設定指南

## 1. 安裝依賴

```bash
make install
# 或
pip install -r requirements.txt
```

## 2. 設定 SSL 證書

資料庫連接需要 SSL 證書。證書檔案位於 `server-cert/` 目錄。

### 自動解壓證書

```bash
make setup-certs
```

這會解壓以下檔案：
- `server-ca.zip` → `server-ca.pem`
- `client-cert.zip` → `client-cert.pem`
- `client-key.zip` → `client-key.pem`

### 手動解壓證書

```bash
cd server-cert
unzip server-ca.zip
unzip client-cert.zip
unzip client-key.zip
```

## 3. 配置資料庫（可選）

如果需要修改資料庫配置，可以創建 `.env` 檔案：

```bash
cp .env.example .env
```

然後編輯 `.env` 檔案設定 `DB_NAME`（資料庫名稱）。

## 4. 測試連接

```bash
python test_db_connection.py
```

如果看到 "✓ 資料庫連接成功！"，表示設定完成。

## 5. 開始使用

### 互動式 CLI

```bash
python -m src.main
```

### 快速演示

```bash
python demo.py
```

### 使用範例

```bash
python examples/basic_usage.py
```

## 常見問題

### Q: 證書解壓失敗

**A:** 確認 `server-cert/` 目錄下有以下 zip 檔案：
- server-ca.zip
- client-cert.zip
- client-key.zip

### Q: 資料庫連接失敗

**A:** 檢查以下幾點：
1. 網路連接是否正常
2. SSL 證書是否已正確解壓
3. 資料庫名稱是否正確（檢查 `config.py` 中的 `DB_NAME`）
4. IP 是否可以訪問

### Q: 模型下載慢

**A:** 首次使用會自動下載 Qwen/Qwen2.5-0.5B-Instruct 模型（約 1GB）。可以：
1. 使用代理加速下載
2. 手動下載模型到 `~/.cache/huggingface/`

### Q: 想使用其他模型

**A:** 修改程式碼中的模型名稱：

```python
model = HuggingFaceModel(
    model_name="google/gemma-2-2b-it",  # 更換模型
    device="cpu"
)
```

## 資料表說明

### tencent_bill
騰訊帳單主表，包含：
- tencent_id (騰訊帳號)
- cost (成本)
- coupon (代金券)
- bill_month (帳期)

### global_bill
全球帳單表，包含：
- tencent_global_account_id (全球帳號)
- business_code_name (產品名稱)
- cost (成本)
- voucher_pay_amount (代金券)

### global_bill_l3
全球帳單明細表，包含：
- product_name (產品細項)
- region (區域)
- real_cost (代金券前金額)
- total_cost (代金券後金額)

