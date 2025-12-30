import streamlit as st
import database as db
import pandas as pd
import sys
import os

# 引用上層模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="產品列表",
    page_icon="📋",
    layout="wide"
)

st.title("📋 產品資料庫")

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("🔄 重新整理列表"):
        st.rerun()

df = db.get_all_products()

with col2:
    if not df.empty:
        # 匯出 Excel
        # 為了避免重新讀取導致按鈕重置，這裡直接生成
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Products')
        processed_data = output.getvalue()
        
        st.download_button(
            label="📥 匯出 Excel",
            data=processed_data,
            file_name="pdm_products.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if not df.empty:
    # 簡單的統計指標
    c1, c2, c3 = st.columns(3)
    c1.metric("總產品數", len(df))
    if 'price' in df.columns:
        c1.metric("總產品數", len(df))
        c2.metric("平均售價", f"${df['price'].mean():.2f}")
        c3.metric("總庫存價值(估)", f"${df['cost'].sum():,.0f}")
    
    st.markdown("---")
    
    # 建立顯示用的 DataFrame
    display_df = df.copy()
    
    # 資料表格
    st.dataframe(
        display_df,
        column_config={
            "id": "ID",
            "name": "名稱",
            "sku": "SKU",
            "category": "分類",
            "price": st.column_config.NumberColumn("售價", format="$%.2f"),
            "cost": st.column_config.NumberColumn("成本", format="$%.2f"),
            "description": "描述",
            "image_path": st.column_config.ImageColumn("圖片", help="產品預覽圖"),
            "created_at": "建立時間",
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.header("✏️ 編輯產品")
    
    # 選擇要編輯的產品
    product_options = df.set_index('id')['name'].to_dict()
    selected_product_id = st.selectbox(
        "選擇要修改的產品", 
        options=[None] + list(product_options.keys()), 
        format_func=lambda x: "請選擇..." if x is None else f"{product_options[x]} (ID: {x})"
    )

    if selected_product_id:
        product_data = df[df['id'] == selected_product_id].iloc[0]
        
        with st.expander("展開編輯表單", expanded=True):
            with st.form("edit_product_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("產品名稱", value=product_data['name'])
                    new_sku = st.text_input("產品代號 (SKU)", value=product_data['sku'])
                    
                    # 處理 Category 選項，確保原始值在選項中
                    categories = ["電子產品", "辦公用品", "生活雜貨", "服飾配件", "其他"]
                    current_category = product_data['category']
                    if current_category not in categories:
                        categories.append(current_category)
                    new_category = st.selectbox("產品分類", categories, index=categories.index(current_category))
                
                with col2:
                    new_price = st.number_input("銷售價格 (TWD)", min_value=0.0, step=10.0, format="%.2f", value=float(product_data['price']))
                    new_cost = st.number_input("成本價格 (TWD)", min_value=0.0, step=10.0, format="%.2f", value=float(product_data['cost']))
                    
                    # 圖片處理
                    if product_data['image_path']:
                        st.image(product_data['image_path'], caption="目前圖片", width=100)
                    new_uploaded_file = st.file_uploader("更換圖片 (若不修改請留空)", type=["jpg", "png", "jpeg"])
                
                new_description = st.text_area("產品描述", value=product_data['description'], height=150)
                
                submitted = st.form_submit_button("💾 儲存變更")
                
                if submitted:
                    # 處理圖片上傳
                    new_image_path = None
                    if new_uploaded_file:
                        # 簡單的儲存邏輯，這裡直接使用相對路徑
                        UPLOAD_DIR = "uploads"
                        if not os.path.exists(UPLOAD_DIR):
                            os.makedirs(UPLOAD_DIR)
                        new_image_path = os.path.join(UPLOAD_DIR, new_uploaded_file.name)
                        with open(new_image_path, "wb") as f:
                            f.write(new_uploaded_file.getbuffer())
                    
                    # 更新資料庫
                    else:
                        st.error("⚠️ 更新失敗：SKU 可能與其他產品重複。")

    st.markdown("---")
    st.header("📤 批次處理")
    
    with st.expander("批次上傳/更新產品 (Excel)"):
        st.info("請上傳 Excel 檔案 (`.xlsx`)。系統將依據 **SKU** 判斷：若 SKU 已存在則更新，不存在則新增。")
        st.markdown("必要欄位：`name`, `sku`, `category`, `price`, `cost`, `description` (選填)")
        
        uploaded_excel = st.file_uploader("上傳 Excel 檔案", type=["xlsx"])
        
        if uploaded_excel:
            try:
                # 讀取 Excel
                batch_df = pd.read_excel(uploaded_excel)
                
                # 欄位檢查 (不區分大小寫，統一轉小寫比對)
                batch_df.columns = batch_df.columns.str.lower()
                required_cols = {'name', 'sku', 'category', 'price', 'cost'}
                if not required_cols.issubset(set(batch_df.columns)):
                    st.error(f"❌ 缺少必要欄位，請檢查 Excel 是否包含：{', '.join(required_cols)}")
                else:
                    if st.button("🚀 開始批次處理"):
                        success_count = 0
                        update_count = 0
                        fail_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        total_rows = len(batch_df)
                        
                        for index, row in batch_df.iterrows():
                            # 更新進度
                            progress = (index + 1) / total_rows
                            progress_bar.progress(progress)
                            status_text.text(f"正在處理第 {index + 1}/{total_rows} 筆: {row['sku']}")
                            
                            # 準備資料
                            p_name = str(row['name'])
                            p_sku = str(row['sku'])
                            p_category = str(row['category']) if 'category' in row and pd.notna(row['category']) else "未分類"
                            p_price = float(row['price']) if pd.notna(row['price']) else 0.0
                            p_cost = float(row['cost']) if pd.notna(row['cost']) else 0.0
                            p_desc = str(row['description']) if 'description' in row and pd.notna(row['description']) else ""
                            # 批次上傳暫不支援圖片路徑更新，除非 Excel 有 image_path 欄位且檔案在 server 上，這裡先忽略
                            
                            # 檢查是否存在
                            existing_prod = db.get_product_by_sku(p_sku)
                            
                            if existing_prod:
                                # 更新 (id is index 0)
                                prod_id = existing_prod[0]
                                # 保留原圖片 (image_path is index 7)
                                current_image_path = existing_prod[7]
                                
                                if db.update_product(prod_id, p_name, p_sku, p_category, p_price, p_cost, p_desc, current_image_path):
                                    update_count += 1
                                else:
                                    fail_count += 1
                            else:
                                # 新增
                                if db.add_product(p_name, p_sku, p_category, p_price, p_cost, p_desc):
                                    success_count += 1
                                else:
                                    fail_count += 1
                        
                        st.success(f"處理完成！新增: {success_count} 筆, 更新: {update_count} 筆, 失敗: {fail_count} 筆")
                        st.balloons()
                        # 延遲一點後重整，讓用戶看到結果
                        st.rerun()
                        
            except Exception as e:
                st.error(f"讀取或處理 Excel 時發生錯誤: {e}")

else:
    st.info("目前資料庫中沒有產品，請前往「新建產品」頁面新增。")
