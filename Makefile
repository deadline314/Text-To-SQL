.PHONY: fix test install clean setup-certs gen help conda-env setup-full install-cli install-web web-backend web-frontend web-dev web-install web-stop web-restart

help:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  Text-to-SQL Makefile 指令"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo ">> 快速開始："
	@echo "  make install-cli    - CLI 模式一鍵安裝（命令列工具）"
	@echo "  make install-web    - Web 模式一鍵安裝（CLI + Web UI）[推薦]"
	@echo ""
	@echo ">> CLI 模式使用："
	@echo "  make gen            - 啟動互動式測試工具"
	@echo "  python tools/quick_test.py  - 快速測試"
	@echo ""
	@echo ">> Web 模式使用："
	@echo "  make web-dev        - 一鍵啟動前後端 [推薦]"
	@echo "  make web-stop       - 停止前後端"
	@echo "  make web-restart    - 重啟前後端"
	@echo "  make web-backend    - 啟動後端 (port 8001)"
	@echo "  make web-frontend   - 啟動前端 (port 3000)"
	@echo "  make web-build      - 建置前端"
	@echo ""
	@echo ">> 開發工具："
	@echo "  make fix            - 修復程式碼風格"
	@echo "  make test           - 執行單元測試"
	@echo "  make clean          - 清理快取檔案"
	@echo ""
	@echo ">> 更多資訊："
	@echo "  make help-full      - 顯示完整指令說明"
	@echo "════════════════════════════════════════════════════════════════"

help-full:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  Text-to-SQL 完整指令說明"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📦 安裝指令："
	@echo "  make install-cli      - CLI 模式安裝（Python + 基本依賴）"
	@echo "  make install-web      - Web 模式安裝（CLI + Web 依賴）"
	@echo "  make install-providers - 安裝 Provider 依賴（AWS + Google）"
	@echo "  make conda-env        - 建立 conda 環境"
	@echo "  make setup-full       - 完整安裝（conda + 依賴 + 證書）"
	@echo ""
	@echo "💻 CLI 使用："
	@echo "  make gen              - 互動式 SQL 生成工具"
	@echo "  python tools/quick_test.py      - 快速測試"
	@echo "  python tools/test_connection.py - 測試資料庫連接"
	@echo "  python tools/list_databases.py  - 查看資料庫結構"
	@echo ""
	@echo "🌐 Web UI："
	@echo "  make web-dev          - 一鍵啟動前後端"
	@echo "  make web-backend      - 啟動後端 API"
	@echo "  make web-frontend     - 啟動前端 UI"
	@echo "  make web-build        - 建置前端"
	@echo "  make web-install      - 安裝 Web 依賴"
	@echo ""
	@echo "🔧 開發："
	@echo "  make fix              - 修復程式碼風格 (ruff)"
	@echo "  make test             - 執行測試"
	@echo "  make clean            - 清理快取"
	@echo ""
	@echo "📝設定："
	@echo "  python config.py      - 查看當前設定"
	@echo "  vim .env              - 編輯環境變數"
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"

conda-env:
	@echo "檢查 conda 環境..."
	@if conda env list | grep -q "^t2s "; then \
		echo "✓ Conda 環境 't2s' 已存在"; \
	else \
		echo "建立 conda 環境 't2s'..."; \
		conda create -n t2s python=3.10 -y; \
		echo "✓ Conda 環境 't2s' 建立完成"; \
	fi

install:
	pip install -r requirements.txt

setup-certs:
	@chmod +x scripts/unzip_certs.sh
	@./scripts/unzip_certs.sh

fix:
	ruff check --fix .
	ruff format .

test:
	pytest $(if $(scope),tests/$(scope),tests/)

gen:
	python tools/test_generation.py $(ARGS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

# ============================================================================
# 安裝指令 (Installation Commands)
# ============================================================================

# CLI 模式安裝（僅命令列工具）
install-cli:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  CLI 模式一鍵安裝"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo ">> 步驟 1: 安裝 Python 依賴..."
	pip install -r requirements.txt
	@echo ""
	@echo ">> 步驟 2: 解壓 SSL 證書..."
	@$(MAKE) setup-certs
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  [完成] CLI 模式安裝完成"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo ">> 使用方式："
	@echo "  make gen                    # 啟動互動式工具"
	@echo "  python tools/quick_test.py  # 快速測試"
	@echo ""
	@echo ">> 進階選項："
	@echo "  make install-providers      # 安裝 AWS + Google 支援"
	@echo "  python config.py            # 查看設定"
	@echo ""

# Web 模式安裝（CLI + Web UI）
install-web:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  Web 模式一鍵安裝"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo ">> 步驟 1: 安裝 CLI 模式依賴..."
	@$(MAKE) install-cli
	@echo ""
	@echo ">> 步驟 2: 安裝 Web 後端依賴..."
	pip install -r requirements-web.txt
	@echo ""
	@echo ">> 步驟 3: 安裝 Web 前端依賴..."
	@if [ -d "web/frontend" ]; then \
		cd web/frontend && npm install && echo "[完成] 前端依賴安裝完成"; \
	else \
		echo "[錯誤] 前端目錄不存在"; \
	fi
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  [完成] Web 模式安裝完成"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo ">> 啟動方式："
	@echo "  make web-dev                # 一鍵啟動前後端 [推薦]"
	@echo ""
	@echo ">> 或分別啟動："
	@echo "  Terminal 1: make web-backend   # 後端 (port 8001)"
	@echo "  Terminal 2: make web-frontend  # 前端 (port 3000)"
	@echo ""
	@echo ">> 瀏覽器開啟："
	@echo "  http://localhost:3000"
	@echo ""

# 安裝 Provider 依賴（AWS Bedrock + Google GenAI）
install-providers:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  安裝 Provider 依賴"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	pip install -r requirements-provider.txt
	@echo ""
	@echo "[完成] Provider 依賴安裝完成"
	@echo ""
	@echo ">> 已安裝："
	@echo "  - boto3 (AWS Bedrock)"
	@echo "  - google-genai (Google GenAI)"
	@echo "  - tenacity (重試機制)"
	@echo ""
	@echo ">> 設定方式："
	@echo "  編輯 .env 檔案，填入 API Keys："
	@echo "    AWS_ACCESS_KEY_ID=..."
	@echo "    AWS_SECRET_ACCESS_KEY=..."
	@echo "    GCP_API_KEY=..."
	@echo ""

# ============================================================================
# Web UI 指令 (Web UI Commands)
# ============================================================================

# 一鍵啟動前後端
web-dev:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  啟動 Web 開發模式"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo ">> 正在啟動後端 (port 8001)..."
	@echo ""
	@(python web/backend/main.py &)
	@sleep 2
	@echo ""
	@echo ">> 正在啟動前端 (port 3000)..."
	@echo ""
	@cd web/frontend && npm start

# 僅啟動後端
web-backend:
	@echo ">> 啟動後端 API (port 8001)..."
	@echo "   API 文件: http://localhost:8001/docs"
	@echo ""
	python web/backend/main.py

# 僅啟動前端
web-frontend:
	@echo ">> 啟動前端 UI (port 3000)..."
	@echo "   瀏覽器: http://localhost:3000"
	@echo ""
	cd web/frontend && npm start

# 建置前端
web-build:
	@echo ">> 建置前端..."
	cd web/frontend && npm run build
	@echo ""
	@echo "[完成] 輸出在 web/frontend/build/"

# 安裝 Web 依賴
web-install:
	@echo ">> 安裝 Web 依賴..."
	pip install -r requirements-web.txt
	cd web/frontend && npm install
	@echo ""
	@echo "[完成] Web 依賴安裝完成"

# 停止前後端
web-stop:
	@echo ">> 停止 Web 服務..."
	@echo "   正在查找並停止後端 (port 8001)..."
	@-lsof -ti:8001 | xargs kill -9 2>/dev/null && echo "   [完成] 後端已停止" || echo "   [提示] 後端未運行"
	@echo "   正在查找並停止前端 (port 3000)..."
	@-lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "   [完成] 前端已停止" || echo "   [提示] 前端未運行"
	@echo ""
	@echo "[完成] Web 服務已停止"

# 重啟前後端
web-restart: web-stop
	@echo ""
	@echo ">> 重新啟動 Web 服務..."
	@sleep 1
	@$(MAKE) web-dev

setup: install setup-certs
	@echo "Setup completed!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate conda env: conda activate t2s"
	@echo "  2. Test connection: python tools/test_connection.py"
	@echo "  3. Quick test: python tools/quick_test.py"
	@echo "  4. See all commands: make help"

setup-full: conda-env
	@echo ""
	@echo "啟動 conda 環境並安裝..."
	@bash -c "source $$(conda info --base)/etc/profile.d/conda.sh && conda activate t2s && make install && make setup-certs"
	@echo ""
	@echo "=" 
	@echo "✅ 完整安裝完成！"
	@echo "="
	@echo ""
	@echo "使用方式："
	@echo "  1. 啟動環境: conda activate t2s"
	@echo "  2. 測試連接: python tools/test_connection.py"
	@echo "  3. 快速開始: make gen"
	@echo ""
	@echo "查看設定："
	@echo "  python config.py"
	@echo ""
	@echo "查看所有命令："
	@echo "  make help"
