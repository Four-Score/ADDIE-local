import streamlit as st
import os
from PyPDF2 import PdfReader
import docx2txt
from event import run_main  # Import the function from event.py

# Streamlit App Title and Description
st.title("Google Calendar Manager")
st.write(
    "I can assist you with managing your Google Calendar events by processing text or extracting content from uploaded files."
)

# Display radio buttons for user choice
option = st.radio(
    "How would you like to provide the information?",
    ("Enter your thoughts", "Upload file")
)

# Variable to hold the extracted or entered text
user_input = None

# Option 1: Input box for entering thoughts
if option == "Enter your thoughts":
    thoughts = st.text_area("Enter your thoughts")
    if st.button("Submit"):
        user_input = thoughts
        # Show loading spinner while result is being generated
        with st.spinner('Processing...'):
            crew_output = run_main(user_input)  # Call the run_main function with the text
            result = crew_output.raw  # Extract only the raw output
        st.write("Here are the events found:")
        st.write(result)  # Display the extracted raw result

# Option 2: File upload for PDF or DOCX
elif option == "Upload file":
    uploaded_file = st.file_uploader("Upload a DOCX or PDF file", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        if st.button("Submit"):
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                # Extract text from PDF
                reader = PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                user_input = text
                # Display the extracted text first
                st.write("Extracted Text from PDF:")
                st.write(user_input)
            
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # Extract text from DOCX
                text = docx2txt.process(uploaded_file)
                user_input = text
                # Display the extracted text first
                st.write("Extracted Text from DOCX:")
                st.write(user_input)
            
            # Show loading spinner while result is being generated
            with st.spinner('Processing...'):
                crew_output = run_main(user_input)  # Call the run_main function with the extracted text
                result = crew_output.raw  # Extract only the raw output
            
            # Display the results from run_main
            st.write("Here are the events found:")
            st.write(result)
