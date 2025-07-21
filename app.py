from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Configurable options
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
UPLOAD_FOLDER = 'uploads'
BRANDS = ["Cosmix", "Krishna's Herbal", "Kiro", "The Whole Truth", "Giva"]
ORDER_STATUS_FILTERS = {
    "Krishna's Herbal": ['Not Dispatched', 'Pickedup', 'Attempted Delivery', 'In-transit'],
    "default": ['Not Dispatched', 'Pickedup', 'Attempted Delivery']
}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    tables = {}
    error = None

    if request.method == 'POST':
        file = request.files['file']

        if file and allowed_file(file.filename):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except Exception as e:
                error = f"❌ Error reading file: {e}"
                return render_template('index.html', tables=tables, error=error)

            # Basic cleanup
            df.columns = [str(c).strip() for c in df.columns]

            # Ensure necessary columns
            required_cols = ['Client Name', 'Order Status', 'Dark Store', 'Order Date', 'AWB No']
            if not all(col in df.columns for col in required_cols):
                error = f"Missing columns in file. Required: {required_cols}"
                return render_template('index.html', tables=tables, error=error)

            # Convert date to readable string
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce').dt.strftime('%d %B')
            df.dropna(subset=['Order Date'], inplace=True)

            for brand in BRANDS:
                brand_df = df[df['Client Name'].str.contains(brand, case=False, na=False)]
                if brand_df.empty:
                    continue

                # Choose brand-specific or default statuses
                statuses = ORDER_STATUS_FILTERS.get(brand, ORDER_STATUS_FILTERS['default'])
                brand_df = brand_df[brand_df['Order Status'].isin(statuses)]

                # Pivot table
                pivot = pd.pivot_table(
                    brand_df,
                    values='AWB No',
                    index=['Dark Store', 'Order Date'],
                    columns='Order Status',
                    aggfunc='count',
                    fill_value=0,
                    margins=True,
                    margins_name='Grand Total'
                )

                pivot = pivot.reset_index()
                html_table = pivot.to_html(classes='table table-bordered table-sm table-striped', index=False, escape=False)
                tables[brand] = html_table

        else:
            error = "Only Excel files (.xls, .xlsx) are allowed."

    return render_template('index.html', tables=tables, error=error)

if __name__ == '__main__':
    app.run(debug=True)
