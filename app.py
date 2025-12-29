import streamlit as st
import pandas as pd
import os
from PIL import Image
import database

# --- Configuration ---
st.set_page_config(
    page_title="產品建立工具 (PDM)",
    page_icon="📦",
    layout="wide"
)

# Ensure storage directory exists
if not os.path.exists('storage'):
    os.makedirs('storage')

# Initialize DB
database.init_db()

# --- CSS Styling ---
st.markdown("""
<style>
    .main {
        background-color: #f9f9f9;
        font-family: "Microsoft JhengHei", sans-serif;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stButton>button {
        background-color: #2980b9;
        color: white;
    }
    .success-msg {
        padding: 10px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("📦 PDM 系統")
page = st.sidebar.selectbox("功能選單", ["建立新產品", "產品列表"])

# --- Page: Create New Product ---
if page == "建立新產品":
    st.title("➕ 建立新產品")
    
    with st.form("new_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            code = st.text_input("產品編號*")
            name = st.text_input("產品名稱*")
            category = st.selectbox("分類", ["電子產品", "辦公用品", "家具", "其他"])
        
        with col2:
            spec = st.text_input("規格")
            image_file = st.file_uploader("產品圖片", type=['png', 'jpg', 'jpeg'])
        
        description = st.text_area("產品描述")
        
        submitted = st.form_submit_button("建立產品")
        
        if submitted:
            if not code or not name:
                st.error("請填寫必填欄位 (編號與名稱)")
            else:
                image_path = ""
                if image_file:
                    image_path = os.path.join("storage", image_file.name)
                    with open(image_path, "wb") as f:
                        f.write(image_file.getbuffer())
                
                success, msg = database.add_product(code, name, category, spec, description, image_path)
                
                if success:
                    st.success(f"產品 {name} ({code}) 建立成功！")
                else:
                    st.error(f"建立失敗: {msg}")

# --- Page: Product List ---
elif page == "產品列表":
    st.title("📋 產品列表")
    
    # --- Batch Actions ---
    with st.expander("📂 批次功能 (匯出/匯入)"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 匯出產品 (Export)")
            products = database.get_all_products()
            if products:
                df = pd.DataFrame(products, columns=['id', 'code', 'name', 'category', 'spec', 'description', 'image_path', 'created_at'])
                # Export specific columns
                export_df = df[['code', 'name', 'category', 'spec', 'description', 'image_path']]
                
                # Convert to Excel in memory
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    export_df.to_excel(writer, index=False, sheet_name='Products')
                
                st.download_button(
                    label="📥 下載 Excel 檔案",
                    data=buffer.getvalue(),
                    file_name="products_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("無資料可匯出")

        with c2:
            st.markdown("### 批次上傳/更新 (Batch Upload)")
            uploaded_file = st.file_uploader("上傳 Excel 檔案 (.xlsx)", type=['xlsx'])
            if uploaded_file:
                if st.button("開始匯入"):
                    try:
                        import_df = pd.read_excel(uploaded_file)
                        # Check required columns
                        required_cols = ['code', 'name']
                        if not all(col in import_df.columns for col in required_cols):
                            st.error(f"Excel 必須包含欄位: {', '.join(required_cols)}")
                        else:
                            success_count = 0
                            fail_count = 0
                            
                            progress_bar = st.progress(0)
                            
                            for i, row in import_df.iterrows():
                                # Handle missing optional fields
                                p_code = str(row['code'])
                                p_name = str(row['name'])
                                p_category = str(row.get('category', ''))
                                p_spec = str(row.get('spec', ''))
                                p_desc = str(row.get('description', ''))
                                p_img = str(row.get('image_path', ''))
                                if pd.isna(row.get('category')): p_category = ""
                                if pd.isna(row.get('spec')): p_spec = ""
                                if pd.isna(row.get('description')): p_desc = ""
                                if pd.isna(row.get('image_path')): p_img = ""

                                succ, msg = database.upsert_product(p_code, p_name, p_category, p_spec, p_desc, p_img)
                                if succ:
                                    success_count += 1
                                else:
                                    fail_count += 1
                                    st.warning(f"Row {i+1} fail: {msg}")
                                
                                progress_bar.progress((i + 1) / len(import_df))
                            
                            st.success(f"匯入完成! 成功: {success_count}, 失敗: {fail_count}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"讀取檔案失敗: {str(e)}")


    products = database.get_all_products()
    
    if products:
        # Convert to DataFrame for better display
        df = pd.DataFrame(products, columns=['id', 'code', 'name', 'category', 'spec', 'description', 'image_path', 'created_at'])
        
        # Search/Filter
        search_term = st.text_input("🔍 搜尋產品 (名稱/編號)", "")
        if search_term:
            df = df[df['name'].str.contains(search_term, case=False) | df['code'].str.contains(search_term, case=False)]
        
        # Display Table with Chinese Headers
        display_df = df[['code', 'name', 'category', 'spec', 'created_at']].copy()
        display_df.columns = ['產品編號', '產品名稱', '分類', '規格', '建立時間']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("### 🖼️ 詳細預覽")
        # Simple detail view
        selected_code = st.selectbox("選擇要預覽/刪除的產品編號", df['code'].tolist())
        
        if selected_code:
            prod = df[df['code'] == selected_code].iloc[0]
            
            c1, c2 = st.columns([1, 2])
            with c1:
                if prod['image_path'] and os.path.exists(prod['image_path']):
                    st.image(prod['image_path'], caption=prod['name'], use_container_width=True)
                else:
                    st.write("無圖片")
            
            with c2:
                st.write(f"**編號:** {prod['code']}")
                st.write(f"**名稱:** {prod['name']}")
                st.write(f"**分類:** {prod['category']}")
                st.write(f"**規格:** {prod['spec']}")
                st.write(f"**描述:** {prod['description']}")
                
                if st.button("🗑️ 刪除此產品", key="del_btn"):
                    database.delete_product(prod['id'])
                    st.rerun()
    else:
        st.info("目前沒有產品資料。請從側邊欄新增產品，或使用批次匯入。")

