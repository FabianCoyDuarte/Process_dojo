import streamlit as st
import os
import pandas as pd
from io import BytesIO

st.title("File Renamer App")

# Filter selection
filter_option = st.selectbox(
    "Choose a filter",
    ["", "Colombia", "Peru"]
)

# File uploader
uploaded_file = st.file_uploader("Choose a file to upload", type=["xls", "xlsx"])

# Button to trigger renaming
if uploaded_file is not None:
    original_name = uploaded_file.name
    _, ext = os.path.splitext(original_name)
    if ext.lower() not in [".xls", ".xlsx"]:
        st.error("Please upload an Excel file (.xls or .xlsx).")
    else:
        if st.button("Process File"):
            # Read all sheets into a dictionary of DataFrames
            try:
                excel_data = pd.read_excel(uploaded_file, sheet_name=None)
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                st.stop()

            # Show sheet names and preview
            st.write("Sheets found:", list(excel_data.keys()))
            for sheet_name, df in excel_data.items():
                st.write(f"Preview of '{sheet_name}':")
                st.dataframe(df.head())

            # Prepare file renaming
            name, ext = os.path.splitext(original_name)
            if filter_option == "Colombia":
                name = f"{name}_colombia"
            elif filter_option == "Peru":
                name = f"{name}_peru"
            new_name = f"{name}_renamed{ext}"

            st.success(f"File processed: {original_name} → {new_name}")

            # To allow download, re-save the Excel with all sheets
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for sheet, df in excel_data.items():
                    df.to_excel(writer, sheet_name=sheet, index=False)
                output.seek(0)

            st.download_button(
            label=f"Download as {new_name}",
            data=output,
            file_name=new_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )