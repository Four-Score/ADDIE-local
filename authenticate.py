import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes for Gmail, Google Drive, and Google Calendar
SCOPES = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/calendar'
]

# Global variables to store the authenticated services
drive_service = None
gmail_service = None
calendar_service = None

def get_token_file(email):
    """Generate a unique token file name based on the user's email."""
    return f"token_{email}.json"

def authenticate_google_services(email):
    """Authenticates and returns the Google API service instances for Gmail, Drive, and Calendar."""
    global drive_service  # Make drive_service globally accessible
    creds = None
    token_file = get_token_file(email)

    # Check if a token for this user already exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If credentials are invalid, expired, or lack required scopes, log the user in
    if not creds or not creds.valid or not creds.has_scopes(SCOPES):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use InstalledAppFlow.from_client_secrets_file() to authenticate user
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret-agents.json', SCOPES, redirect_uri='http://localhost:8080/')
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for future runs in a user-specific token file
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    # Build the service instances for Gmail, Drive, and Calendar
    gmail_service = build('gmail', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)  # Store the Drive service globally
    calendar_service = build('calendar', 'v3', credentials=creds)
    
    return gmail_service, drive_service, calendar_service

def get_drive_service():
    """Returns the globally authenticated Google Drive service."""
    global drive_service
    if drive_service is None:
        raise ValueError("Google Drive service has not been authenticated yet. Call authenticate_google_services() first.")
    return drive_service

def get_gmail_service():
    """Returns the globally authenticated Gmail service."""
    global gmail_service
    if gmail_service is None:
        raise ValueError("Gmail service has not been authenticated yet. Call authenticate_google_services() first.")
    return gmail_service    

def get_calendar_service(): 
    """Returns the globally authenticated Google Calendar service."""
    global calendar_service
    if calendar_service is None:
        raise ValueError("Google Calendar service has not been authenticated yet. Call authenticate_google_services() first.")
    return calendar_service
