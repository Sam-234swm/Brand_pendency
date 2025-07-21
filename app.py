import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="ERP Order Report Viewer", layout="wide")
st.title("📊 ERP Order Report Viewer")

# Upload CSV
uploaded_file = st.file_uploader("Upload ERP Order Report CSV", type=["csv"])
if uploaded_file is not None:
    try:
        # Try loading with default encoding first
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8', low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', low_memory=False)

        # Normalize column names
        df.columns = df.columns.str.strip()
        if 'Brand Name' not in df.columns or 'Order Status' not in df.columns:
            st.error("Required columns 'Brand Name' or 'Order Status' not found in the uploaded file.")
        else:
            # Define allowed order status
            common_status = ["Attempted delivery", "Not dispatched", "Pickedup"]
            extra_status = ["In-transit"]

            # Get list of unique brands
            brands = df['Brand Name'].dropna().unique()

            # Show table per brand
            for brand in sorted(brands):
                with st.expander(f"📦 {brand}", expanded=False):
                    brand_df = df[df['Brand Name'] == brand]

                    # Define filters
                    if brand.strip().lower() == "krishna herbal":
                        filtered_df = brand_df[brand_df['Order Status'].isin(common_status + extra_status)]
                    else:
                        filtered_df = brand_df[brand_df['Order Status'].isin(common_status)]

                    # Display pivot-like table
                    if not filtered_df.empty:
                        st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
                    else:
                        st.info("No matching records found for selected Order Statuses.")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("⬆️ Upload a CSV file to begin.")
