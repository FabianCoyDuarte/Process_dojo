import streamlit as st
import os

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
            file_bytes = uploaded_file.read()
            name, ext = os.path.splitext(original_name)

            # Apply filter
            if filter_option == "Uppercase Filename":
                name = name.upper()
            elif filter_option == "Lowercase Filename":
                name = name.lower()
            elif filter_option == "Add Suffix":
                name = f"{name}_suffix"

            new_name = f"{name}_renamed{ext}"

            st.success(f"File processed: {original_name} → {new_name}")
            st.download_button(
                label=f"Download as {new_name}",
                data=file_bytes,
                file_name=new_name,
                mime=uploaded_file.type
            )