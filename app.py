import streamlit as st
import database as db

st.set_page_config(
    page_title="PDM 系統首頁",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化資料庫
db.init_db()

st.title("📦 歡迎使用 PDM 產品管理系統")

st.markdown("""
### 系統簡介
本系統旨在協助管理組織內的所有產品資料。您可以透過左側選單進行操作：

- **✨ 建立新產品**：輸入詳細資訊並建立新的產品項目。
- **📋 產品列表**：瀏覽所有現有產品，並檢視詳細內容。

---
""")

# 顯示一些最近的數據概況
df = db.get_all_products()
if not df.empty:
    st.subheader("📊 系統概況")
    col1, col2, col3 = st.columns(3)
    col1.metric("已建檔產品數", len(df))
    latest_product = df.iloc[0]
    col2.metric("最新產品", latest_product['name'])
    col3.metric("總資產規模", f"${df['cost'].sum():,.0f}")
else:
    st.info("目前尚無資料，請立即開始新增您的第一項產品！")
    
st.markdown("---")
st.caption("PDM Tool v1.0 | Powered by Python & Streamlit")
