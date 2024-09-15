import streamlit as st
from drive2 import process_files_sequentially
import io

# Page layout settings
st.set_page_config(page_title="Google Drive Report Generator", layout="centered")

# Custom styles to make the app look more professional and align input boxes properly
st.markdown(
    """
    <style>
    .title-text {
        font-size: 30px;
        font-weight: bold;
        color: #4f8bf9;
        text-align: center;
        margin-bottom: 20px;
    }
    .stTextInput > div > input {
        padding: 10px;
        font-size: 16px;
        border-radius: 10px;
        border: 1px solid #ccc;
        box-shadow: none;
        margin-bottom: 10px;
    }
    .submit-button {
        background-color: #4f8bf9;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px 20px;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Check if the drive service is available in session state
if 'drive_service' not in st.session_state:
    st.error("You need to authenticate first. Please go back to the authentication page.")
    st.stop()

# Get the authenticated Google Drive service from session state
drive_service = st.session_state['drive_service']

# Main page content
st.markdown('<p class="title-text">Google Drive Report Generator</p>', unsafe_allow_html=True)

with st.container():
    # Input field for Google Drive folder link
    google_drive_link = st.text_input("Google Drive Folder Link", placeholder="Enter your Google Drive folder link here")

    # Input field for file types
    file_types = st.text_input("Which files do you want reports about?", placeholder="e.g., PDF, Excel, Word, etc.")

    # Submit button
    submit_button = st.button("Generate Reports", key="submit", help="Click to generate reports for the selected files")

# Initialize variable to hold the text report
report_text = ""

# When the submit button is pressed
if submit_button:
    if google_drive_link and file_types:
        # Display loading spinner while the processing is running
        with st.spinner("Processing files and generating reports. Please wait..."):
            try:
                # Call the process_files_sequentially function with the user inputs
                report_results = process_files_sequentially(google_drive_link, file_types)
                st.success("Reports generated successfully!")

                # Display the report results and build the report text
                for result in report_results:
                    st.json(result)
                    # Construct the report text
                    report_text += f"File Name: {result['File Name']}\n"
                    report_text += f"File Link: {result['File Link']}\n"
                    report_text += f"Document Summary: {result['Document Summary']}\n"
                    report_text += f"Document Priority: {result['Document Priority']}\n\n"

            except Exception as e:
                st.error(f"An error occurred while processing: {str(e)}")
    else:
        st.error("Please fill in both fields before submitting.")

# If report text is not empty, provide the download button
if report_text:
    # Convert the report text into a BytesIO object for download
    report_file = io.BytesIO(report_text.encode('utf-8'))
    st.download_button(
        label="Download Reports as TXT",
        data=report_file,
        file_name="google_drive_reports.txt",
        mime="text/plain"
    )