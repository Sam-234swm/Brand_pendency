import streamlit as st
import pandas as pd

st.set_page_config(page_title="Brand Pendency Report", layout="wide")
st.title("📦 Brand Order Status Pivot Report")

uploaded_file = st.file_uploader("Upload ERP File (CSV or Excel)", type=["csv", "xls", "xlsx"])

BRANDS = ["Cosmix", "Krishna's Herbal", "Kiro", "The Whole Truth", "Giva"]
ORDER_STATUS_FILTERS = {
    "Krishna's Herbal": ['Not Dispatched', 'Pickedup', 'Attempted Delivery', 'In-transit'],
    "default": ['Not Dispatched', 'Pickedup', 'Attempted Delivery']
}

def read_uploaded_file(uploaded_file):
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif uploaded_file.name.endswith(".xls"):
            df = pd.read_excel(uploaded_file, engine='xlrd')
        else:
            return None, "Unsupported file format. Please upload CSV or Excel."
        return df, None
    except Exception as e:
        return None, str(e)

if uploaded_file:
    df, error = read_uploaded_file(uploaded_file)
    if error:
        st.error(f"❌ Error reading file: {error}")
    else:
        df.columns = [c.strip() for c in df.columns]

        required_cols = ['Client Name', 'Order Status', 'Dark Store', 'Order Date', 'AWB No']
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ Missing columns. Required: {required_cols}")
        else:
            # Convert Order Date to readable format
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
            df.dropna(subset=['Order Date'], inplace=True)
            df['Order Date'] = df['Order Date'].dt.strftime('%d %B')

            for brand in BRANDS:
                st.subheader(f"📊 {brand}")
                brand_df = df[df['Client Name'].str.contains(brand, case=False, na=False)]

                if brand_df.empty:
                    st.warning(f"No data found for {brand}.")
                    continue

                statuses = ORDER_STATUS_FILTERS.get(brand, ORDER_STATUS_FILTERS["default"])
                brand_df = brand_df[brand_df['Order Status'].isin(statuses)]

                pivot = pd.pivot_table(
                    brand_df,
                    values='AWB No',
                    index=['Dark Store', 'Order Date'],
                    columns='Order Status',
                    aggfunc='count',
                    fill_value=0,
                    margins=True,
                    margins_name='Grand Total'
                ).reset_index()

                st.dataframe(pivot, use_container_width=True)
