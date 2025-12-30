import streamlit as st
import database as db
import os
import sys

# 為了讓 pages 下的檔案能引用 database.py，將上層目錄加入 sys.path (雖然 Streamlit 預設會處理，但顯式加入較保險)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="新建產品",
    page_icon="✨",
    layout="wide"
)

# 自訂 CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        background-color: #0068c9;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 確保 uploads 目錄存在 (重複確保)
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_uploaded_file(uploaded_file):
    """儲存上傳的檔案並回傳相對路徑"""
    if uploaded_file is None:
        return None
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

st.title("✨ 建立新產品")
st.markdown("請填寫以下資訊以建立新的產品項目。")

with st.form("create_product_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("產品名稱", placeholder="例如：高效能無線滑鼠")
        sku = st.text_input("產品代號 (SKU)", placeholder="例如：MS-2024-WL")
        category = st.selectbox("產品分類", ["電子產品", "辦公用品", "生活雜貨", "服飾配件", "其他"])
    
    with col2:
        price = st.number_input("銷售價格 (TWD)", min_value=0.0, step=10.0, format="%.2f")
        cost = st.number_input("成本價格 (TWD)", min_value=0.0, step=10.0, format="%.2f")
        uploaded_file = st.file_uploader("產品圖片", type=["jpg", "png", "jpeg"])
    
    description = st.text_area("產品描述", placeholder="請輸入產品詳細說明...", height=150)
    
    submitted = st.form_submit_button("🚀 確認建立產品")
    
    if submitted:
        if not name or not sku:
            st.error("❌ 請填寫產品名稱與 SKU！")
        else:
            image_path = save_uploaded_file(uploaded_file)
            success = db.add_product(name, sku, category, price, cost, description, image_path)
            if success:
                st.success(f"✅ 產品 **{name}** ({sku}) 已成功建立！")
                if image_path:
                    st.image(image_path, width=200, caption="已上傳圖片")
                st.balloons()
            else:
                st.error(f"⚠️ 建立失敗：SKU **{sku}** 可能已存在。")
