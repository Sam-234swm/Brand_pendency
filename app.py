import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📦 Brand-wise Order Status Viewer")

# Step 1: Upload CSV file
uploaded_file = st.file_uploader("Upload your ERP OrderReport CSV", type=["csv"])

if uploaded_file:
    try:
        # Load CSV with fallback encoding
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8', engine='python', on_bad_lines='skip')
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', engine='python', on_bad_lines='skip')

        st.success("✅ File loaded successfully!")

        # Step 2: Normalize column names
        df.columns = df.columns.str.strip()

        # Step 3: Required columns
        required_columns = ["Client Name", "Order Status"]
        if not all(col in df.columns for col in required_columns):
            st.error(f"❌ Missing columns: {set(required_columns) - set(df.columns)}")
        else:
            # Step 4: Filter for only your 5 clients
            brand_list = ["Cosmix", "Krishna's Herbal", "Kiro", "The Whole Truth", "Giva"]
            df = df[df["Client Name"].isin(brand_list)]

            # Define status filters
            common_statuses = ["Attempted delivery", "Not dispatched", "Pickedup"]
            krishna_statuses = common_statuses + ["In-transit"]

            # Step 5: Brand-wise Display
            for brand in brand_list:
                st.subheader(f"📌 {brand}")

                # Filter based on brand and status
                if brand == "Krishna's Herbal":
                    brand_df = df[(df["Client Name"] == brand) & (df["Order Status"].isin(krishna_statuses))]
                else:
                    brand_df = df[(df["Client Name"] == brand) & (df["Order Status"].isin(common_statuses))]

                if not brand_df.empty:
                    # Show pivot-style grouped count
                    summary = brand_df.groupby(["Order Status"]).size().reset_index(name="Count")
                    st.dataframe(summary, use_container_width=True)
                else:
                    st.info("No matching orders for this brand.")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.warning("Please upload a CSV file to begin.")
