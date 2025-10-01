# Text-to-SQL Web UI

現代化的 Web 介面，用於將自然語言轉換為 SQL 查詢。

## 功能特色

- ✨ 現代化設計 - Material-UI + Framer Motion
- ⚡ 即時生成 - Streaming 模式顯示生成過程
- 🎨 豐富動畫 - 流暢的過場和互動效果
- 🌓 深色主題 - 保護眼睛的暗色介面
- 📱 響應式設計 - 支援各種螢幕尺寸
- 🔄 多 Provider 支援 - Local / Bedrock / GenAI

## 快速開始

### 1. 安裝依賴

```bash
# 後端依賴
pip install -r requirements-web.txt

# 前端依賴
cd web/frontend
npm install
```

### 2. 啟動後端

```bash
# 在專案根目錄
python web/backend/main.py

# 或使用 uvicorn
uvicorn web.backend.main:app --reload
```

後端將在 `http://localhost:8001` 啟動

### 3. 啟動前端

```bash
# 在 web/frontend 目錄
npm start
```

前端將在 `http://localhost:3000` 啟動

## 使用 Makefile

```bash
# 啟動後端
make web-backend

# 啟動前端（需另開終端）
make web-frontend

# 建置前端
make web-build
```

## API 文件

啟動後端後，訪問：
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 主要端點

- `GET /` - API 資訊
- `GET /api/providers` - 獲取可用的模型 Provider
- `GET /api/schema` - 獲取資料庫 Schema
- `GET /api/examples` - 獲取範例查詢
- `POST /api/generate` - 生成 SQL（支援 Streaming）
- `GET /api/health` - 健康檢查

## 架構

```
web/
├── backend/
│   └── main.py          # FastAPI 後端
├── frontend/
│   ├── public/          # 靜態資源
│   ├── src/
│   │   ├── App.js       # 主應用程式
│   │   └── index.js     # 入口點
│   └── package.json     # 前端依賴
└── README.md            # 本檔案
```

## 技術棧

### 後端
- **FastAPI** - 現代化的 Python Web 框架
- **Uvicorn** - ASGI 伺服器
- **Pydantic** - 資料驗證

### 前端
- **React** - UI 框架
- **Material-UI** - UI 組件庫
- **Framer Motion** - 動畫庫
- **Axios** - HTTP 客戶端

## 開發

### 熱重載

後端和前端都支援熱重載：
- 後端：修改 Python 檔案後自動重啟
- 前端：修改 JS/JSX 檔案後自動刷新

### 跨域設定

後端已設定 CORS，允許前端從不同 port 訪問。

## 生產部署

### 後端

```bash
# 使用 Gunicorn + Uvicorn
pip install gunicorn
gunicorn web.backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### 前端

```bash
# 建置
cd web/frontend
npm run build

# 使用 serve 或任何靜態伺服器
npx serve -s build
```

## 環境變數

確保 `.env` 檔案已正確設定：

```bash
# 資料庫
DB_HOST=your-host
DB_USER=your-user
DB_PASSWORD=your-password

# AWS Bedrock（可選）
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# Google GenAI（可選）
GCP_API_KEY=your-api-key
```

## 疑難排解

### 後端啟動失敗

檢查：
1. Python 依賴是否安裝：`pip list | grep fastapi`
2. Port 8001 是否被占用：`lsof -i :8001`
3. `.env` 檔案是否存在

### 前端無法連接後端

檢查：
1. 後端是否在 8001 port 運行
2. `App.js` 中的 API_BASE 是否正確
3. 瀏覽器控制台是否有 CORS 錯誤

### Provider 顯示「未設定」

表示對應的 API Key 未設定，請檢查 `.env` 檔案。

## 相關文件

- [專案 README](../README.md)
- [API 文件](http://localhost:8001/docs)
- [Provider 指南](../docs/PROVIDER_GUIDE.md)

---

**版本**: 1.4.0  
**更新日期**: 2025-10-01

