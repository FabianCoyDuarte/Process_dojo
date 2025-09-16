import streamlit as st
import os
import pandas as pd
from io import BytesIO
from processing import DojoAttendanceProcessor

st.title("Dojo Attendance Processor")

# Filter selection
filter_option = st.selectbox(
    "Choose a filter",
    ["", "Colombia", "Peru"]
)

# File uploader
uploaded_file = st.file_uploader("Choose a file to upload", type=["xls", "xlsx"])

if uploaded_file is not None:
    original_name = uploaded_file.name
    _, ext = os.path.splitext(original_name)
    if ext.lower() not in [".xls", ".xlsx"]:
        st.error("Please upload an Excel file (.xls or .xlsx)")
    else:
        if st.button("Process File"):
            if not filter_option:
                st.error("Please select a country filter.")
                st.stop()
            try:
                # Save uploaded file to a temporary location if needed
                # Or pass the file-like object directly if your processor supports it
                processor = DojoAttendanceProcessor()
                country = filter_option
                df_looker_tcbp, report_cleaned = processor.process(country, uploaded_file)
            except Exception as e:
                st.error(f"Error processing file: {e}")
                st.stop()

            st.success("File processed successfully!")
            st.write("Report Cleaned:")
            st.dataframe(report_cleaned)

            st.write("Total_Values:")
            st.dataframe(df_looker_tcbp.tail(1))
