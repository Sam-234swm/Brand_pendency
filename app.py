import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📦 Brand-wise Order Status Viewer")

# Step 1: Upload CSV file
uploaded_file = st.file_uploader("Upload your ERP OrderReport CSV", type=["csv"])

if uploaded_file:
    try:
        # More tolerant CSV loader with updated syntax
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8', engine='python', on_bad_lines='skip')
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', engine='python', on_bad_lines='skip')

        st.success("✅ File loaded successfully!")

        # Step 2: Normalize column names
        df.columns = df.columns.str.strip()

        # Ensure required columns exist
        required_columns = ["Brand Name", "Order Status"]
        if not all(col in df.columns for col in required_columns):
            st.error(f"❌ Missing columns: {set(required_columns) - set(df.columns)}")
        else:
            # Step 3: Filter Order Status
            base_status = ["Attempted delivery", "Not dispatched", "Pickedup"]
            krishna_status = base_status + ["In-transit"]

            # Step 4: Get all brand names
            brands = df["Brand Name"].dropna().unique()

            for brand in brands:
                st.subheader(f"📌 {brand}")

                if brand.strip().lower() == "krishna herbal":
                    brand_df = df[(df["Brand Name"] == brand) & (df["Order Status"].isin(krishna_status))]
                else:
                    brand_df = df[(df["Brand Name"] == brand) & (df["Order Status"].isin(base_status))]

                if not brand_df.empty:
                    # Pivot-like summary
                    summary = brand_df.groupby(["Order Status"]).size().reset_index(name="Count")
                    st.dataframe(summary, use_container_width=True)
                else:
                    st.info("No matching orders found.")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.warning("Please upload a CSV file to begin.")
