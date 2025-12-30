
# 實作計畫：新產品建立工具 (PDM Tool)

## 任務目標
建立一個基於 Python + Streamlit 的 Web 應用程式，用於建立新產品資料並儲存至 SQLite 資料庫。

## 技術架構
- **Frontend/Backend**: Python + Streamlit
- **Database**: SQLite (`pdm.db`)
- **ORM**: 直接使用 `sqlite3` 或 `SQLAlchemy` (為保持簡單與擴充性，建議使用 `SQLAlchemy` 或是純 SQL 封裝在 `database.py`)

## 檔案結構
```text
m:/PDM/
├── app.py              # 應用程式主入口 (首頁/儀表板)
├── database.py         # 資料庫連線與操作邏輯
├── pages/              # 分頁目錄
│   ├── 1_New_Product.py # 新建產品頁面
│   └── 2_Product_List.py # 產品列表頁面
├── uploads/            # 圖片上傳目錄
├── requirements.txt    # 專案依賴套件
└── .gitignore          # Git 忽略設定
```

## 功能規劃
1. **資料庫初始化**:
   - 自動建立 `products` 資料表 (若不存在)。
   - 欄位包含: ID, 產品名稱, 產品代號 (SKU), 分類, 價格, 成本, 描述, 建立時間。

2. **使用者介面 (UI)**:
   - **側邊欄 (Sidebar)**: Streamlit 原生多頁面導航 (無 Radio Button)。
   - **首頁 (Home)**: 系統簡介與簡易統計。
   - **新增產品頁面** (`pages/1_New_Product.py`):
     - 表單輸入 (名稱, SKU, 分類, 價格, 成本, 描述)。
     - **圖片上傳**: 支援上傳產品圖片 (JPG, PNG)。
     - 驗證 (必填欄位, SKU 唯一性)。
     - 提交按鈕 -> 儲存圖片至 `uploads/` -> 寫入資料庫 (含圖片路徑)。
   - **產品列表頁面** (`pages/2_Product_List.py`):
     - 表格式顯示已建立的產品 (含縮圖)。
     - **編輯功能**:
       - 選擇要編輯的產品 (下拉選單 or 點選)。
       - 顯示編輯表單 (預填現有資料)。
       - 支援修改圖片。
       - 儲存變更 -> 更新資料庫。
     - **進階功能**:
       - **匯出 Excel**: 下載完整產品清單。
       - **批次上傳/更新**: 上傳 Excel 檔，依 SKU 判斷：
         - 若存在 -> 更新資料。
         - 若不存在 -> 新增產品。
     - 簡單的搜尋或過濾功能。

## 執行步驟
1. 建立 `requirements.txt` 並安裝依賴 (streamlit, pandas, openpyxl).
2. 建立 `database.py` (含 `update_product`, `get_product_by_id`, `get_product_by_sku` logic).
3. 建立 `uploads` 資料夾用於存放圖片。
4. 建立 `pages` 資料夾並建立分頁檔案。
5. 重構 `app.py` 為首頁。
6. 更新 `pages/2_Product_List.py` 加入編輯、匯出與批次上傳邏輯。
7. 啟動 Streamlit 伺服器進行測試。

## 待確認事項
- 是否有特定的產品欄位需求？ (目前預設為標準 PDM 欄位)
