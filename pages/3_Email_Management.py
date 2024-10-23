import streamlit as st
from gmail import main_gmail  # Import the main function from gmail.py

# Page layout settings
st.set_page_config(page_title="Generate Emails Report", layout="centered")

# Custom styles to match your previous page's aesthetics
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

# Check if the Gmail service is available in session state
if 'gmail_service' not in st.session_state:
    st.error("You need to authenticate first. Please go back to the authentication page.")
    st.stop()

# Main page content
st.markdown('<p class="title-text">Generate Emails Report</p>', unsafe_allow_html=True)

# Dropdown to select the number of emails for report generation
with st.container():
    num_emails = st.selectbox(
        "How many latest emails do you want to generate a report of?",
        options=[2, 5, 10, 20, 30, 40, 50],
        index=0,
        key="email_count"
    )

# Submit button to store the selected value
submit_button = st.button("Generate Report", key="submit", help="Click to generate report for the selected number of emails")

if submit_button:
    selected_emails = num_emails

    # Run the main_gmail function from gmail.py
    with st.spinner(f"Generating report for {selected_emails} emails..."):
        try:
            # Call the main Gmail function to get reports
            email_reports = main_gmail(selected_emails)  # Pass the number of emails to the function

            # Display the reports if they are found
            if email_reports and len(email_reports) > 0:
                st.success(f"Report for {selected_emails} emails generated successfully!")
                for report in email_reports:
                    st.json(report)  # Display the JSON output for each email report
            else:
                st.error("No emails found or an error occurred while fetching the emails.")
        
        except Exception as e:
            # Display the specific error that occurred
            st.error(f"An error occurred while generating the report: {str(e)}")
