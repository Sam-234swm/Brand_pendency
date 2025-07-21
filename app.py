
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 ERP Order Report Viewer")

uploaded_file = st.file_uploader("Upload ERP CSV Report", type=["csv"])

if uploaded_file is not None:
    # Try multiple CSV read methods
    try:
        df = pd.read_csv(uploaded_file, low_memory=False, encoding='utf-8')
    except Exception:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep='\t', engine='python', encoding='utf-8')
        except Exception:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=';', engine='python', encoding='utf-8')
            except Exception as e:
                st.error(f"❌ Could not read CSV file. Error: {e}")
                st.stop()

    st.success("✅ File successfully loaded.")
    
    # Display file name
    st.write(f"### File: `{uploaded_file.name}`")
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Brand-specific filter conditions
    brand_conditions = {
        "Krishna Herbal": ["Attempted delivery", "Not dispatched", "Pickedup", "In-transit"],
        "Kiro": ["Attempted delivery", "Not dispatched", "Pickedup"],
        "Kapiva": ["Attempted delivery", "Not dispatched", "Pickedup"],
        "Plix": ["Attempted delivery", "Not dispatched", "Pickedup"]
    }

    # Check essential columns
    required_cols = {"Brand Name", "Order Status"}
    if not required_cols.issubset(df.columns):
        st.error("❌ Required columns missing in file: 'Brand Name', 'Order Status'")
        st.stop()

    # Display filtered tables per brand
    for brand, statuses in brand_conditions.items():
        st.markdown(f"## 📦 {brand} Orders")
        filtered = df[(df["Brand Name"] == brand) & (df["Order Status"].isin(statuses))]
        
        if filtered.empty:
            st.info("No data available for this brand.")
        else:
            st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
else:
    st.info("Please upload a CSV file.")
