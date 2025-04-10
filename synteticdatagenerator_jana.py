import streamlit as st
import pandas as pd
from faker import Faker
import random
import tempfile
import pdfplumber

fake = Faker()

def infer_and_generate_synthetic_data(df, num_rows=100):
    synthetic_rows = []
    for _ in range(num_rows):
        row = {}
        for column in df.columns:
            dtype = df[column].dtype

            if pd.api.types.is_string_dtype(dtype):
                row[column] = fake.name() if "name" in column.lower() else fake.word()
            elif pd.api.types.is_numeric_dtype(dtype):
                row[column] = random.randint(1000, 9999)c
            elif pd.api.types.is_bool_dtype(dtype):
                row[column] = random.choice([True, False])
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                row[column] = fake.date_this_decade()
            else:
                row[column] = fake.word()
        synthetic_rows.append(row)

    return pd.DataFrame(synthetic_rows)

st.title("📄 Generate Synthetic Data from Uploaded File")

uploaded_file = st.file_uploader("Upload Excel or PDF", type=["xlsx", "pdf"])
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(tmp_path) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        st.text_area("Extracted PDF Text", text, height=300)
        st.warning("PDF text structure cannot directly infer columns, so synthetic generation is skipped.")
    else:
        df = pd.read_excel(tmp_path)
        st.write("📊 Uploaded Data Preview", df.head())

        num_records = st.slider("Select number of synthetic records", 10, 500, 1000)
        if st.button("Generate Synthetic Data"):
            synthetic_df = infer_and_generate_synthetic_data(df, num_records)
            st.success("✅ Synthetic data generated!")
            st.dataframe(synthetic_df)

            csv = synthetic_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Synthetic Data CSV", csv, "synthetic_data.csv", "text/csv")