import streamlit as st
from authenticate import authenticate_google_services

st.title("Google API Services Integration")

# Ask the user for their email
user_email = st.text_input("Enter your email address to authenticate")

if st.button('Authenticate and List Services'):
    if user_email:
        try:
            # Authenticate and get Google services
            gmail_service, drive_service, calendar_service = authenticate_google_services(user_email)
            
            # Store the services in session state
            st.session_state['gmail_service'] = gmail_service
            st.session_state['drive_service'] = drive_service
            st.session_state['calendar_service'] = calendar_service
            
            st.success("Successfully authenticated with Google APIs.")
        
        except Exception as e:
            st.error(f"An error occurred during authentication: {str(e)}")
    else:
        st.warning("Please enter your email address to proceed.")
