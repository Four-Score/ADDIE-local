import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from bs4 import BeautifulSoup
from crewai_tools import tool
from crewai import Agent, Task, Crew, Process
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set environment variables for the agent
os.environ['OPENAI_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = 'llama-3.1-70b-versatile'
os.environ['OPENAI_API_BASE'] = 'https://api.groq.com/openai/v1'

# Define the Gmail API scope
SCOPES = ['https://mail.google.com/']

def authenticate_gmail_api():
    """Authenticates and returns the Gmail API service instance."""
    creds = None
    # The token2.json file stores the user's access and refresh tokens
    if os.path.exists('token2.json'):
        creds = Credentials.from_authorized_user_file('token2.json', SCOPES)
    # If credentials are invalid, expired, or lack required scopes, log the user in
    if not creds or not creds.valid or not creds.has_scopes(SCOPES):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use InstalledAppFlow.from_client_secrets_file()
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret-agents.json', SCOPES, redirect_uri='http://localhost:8080/')
            # Use run_local_server() with the specified port
            creds = flow.run_local_server(port=8080)
        # Save the credentials for future runs
        with open('token2.json', 'w') as token:
            token.write(creds.to_json())
    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_last_emails(service, max_results=20):
    """
    Fetches the last emails from the user's Gmail inbox.

    Parameters:
    - service: Authorized Gmail API service instance.
    - max_results: Number of emails to fetch.

    Returns:
    - A list of email messages.
    """
    try:
        # Call the Gmail API to fetch the message IDs
        results = service.users().messages().list(
            userId='me', maxResults=max_results, labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        email_messages = []

        if not messages:
            print('No messages found.')
            return email_messages

        for msg in messages:
            # Get the message details
            msg_id = msg['id']
            message = service.users().messages().get(
                userId='me', id=msg_id, format='full').execute()
            email_messages.append(message)

        return email_messages

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_email_body(message):
    """Extracts the text content from an email message, stripping out HTML tags."""
    body = ''
    payload = message['payload']

    def extract_parts(parts_list):
        nonlocal body
        for part in parts_list:
            mime_type = part.get('mimeType')
            if part.get('parts'):
                extract_parts(part['parts'])
            elif mime_type == 'text/plain':
                data = part['body'].get('data')
                if data:
                    text = base64.urlsafe_b64decode(data).decode('utf-8')
                    body += text
            elif mime_type == 'text/html' and not body:
                # Only process HTML if text/plain is not available
                data = part['body'].get('data')
                if data:
                    html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                    # Parse HTML and extract text
                    soup = BeautifulSoup(html_content, 'html.parser')
                    text = soup.get_text()
                    body += text

    if payload.get('parts'):
        extract_parts(payload['parts'])
    else:
        # Single-part message
        mime_type = payload.get('mimeType')
        data = payload['body'].get('data')
        if data:
            content = base64.urlsafe_b64decode(data).decode('utf-8')
            if mime_type == 'text/plain':
                body += content
            elif mime_type == 'text/html':
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text()
                body += text

    return body


def fetch_emails_as_dict(service, max_results=20):
    """
    Fetches the last emails and formats them into a dictionary.

    Parameters:
    - service: Authorized Gmail API service instance.
    - max_results: Number of emails to fetch.

    Returns:
    - dict: Dictionary where keys are the email senders, and values are a tuple containing email contents and a link to the email.
    """
    # Fetch the last X emails
    emails = get_last_emails(service, max_results)
    
    email_dict = {}

    if emails:
        for email in emails:
            headers = email['payload']['headers']
            from_email = ''
            for header in headers:
                if header['name'] == 'From':
                    from_email = header['value']
                    break  # Stop once we find the 'From' header

            # Extract the email body
            body = get_email_body(email)

            # Get the message ID and create the Gmail link for the email
            message_id = email['id']
            email_link = f"https://mail.google.com/mail/u/0/#inbox/{message_id}"

            # Combine everything into a tuple (email content, email link)
            email_dict[from_email] = {"content": body, "link": email_link}

    return email_dict



def process_email_with_crew(email_sender: str, email_link: str, email_content: str) -> dict:
    """
    Function to process an email using CrewAI agents to generate a concise report with summary and priority.
    
    Parameters:
    - email_sender (str): The sender of the email.
    - email_link (str): The link to the email in Gmail.
    - email_content (str): The content of the email.
    
    Returns:
    - dict: A structured report containing the email summary and priority.
    """
    # Summarizer Agent
    email_summarizer = Agent(
        role='Email Summarizer',
        goal=f'Go through the email provided to you by the sender {email_sender} with the link {email_link} and generate a concise summary (maximum 30 words) of its contents, highlighting only the key information. {email_content}',
        verbose=True,
        memory=True,
        backstory=(
            """You're an expert in email analysis and summarization. With your extensive experience, 
            you have developed a unique ability to generate concise and informative summaries of any given email. 
            This helps email recipients quickly find out about the contents of their emails and save time."""
        ),
        allow_delegation=False,
    )

    # Categorizer Agent
    email_categorizer = Agent(
        role='Email Priority Categorizer',
        goal=f'Go through the email provided to you by the sender {email_sender} with the link {email_link}. Based on its textual content, categorize it as high, low, or medium priority with brief justification. {email_content}',
        verbose=True,
        memory=True,
        backstory=(
            """You're an expert in email analysis and priority detection. You can detect whether an email is of high, low, or medium priority
            based on its contents. Your expertise lies in providing a brief justification (maximum 10 words) for the priority category assigned to the email. 
            This will help users in better organizing and managing their emails based on their priority levels."""
        ),
        allow_delegation=False,
    )

    # Consolidator Agent
    email_consolidator = Agent(
        role='Report Consolidator',
        goal=f'Combine the results obtained by each agent into a single coherent report for the email by {email_sender} whose link is {email_link}.',
        verbose=True,
        memory=True,
        backstory=(
            """You're an expert in consolidating information from multiple sources. Your role is to take the results obtained by 
            each agent and combine them into a single coherent report. Your expertise lies in synthesizing information from 
            different agents and presenting it in a structured and organized manner. This will help in providing a 
            comprehensive overview of the email analysis process."""
        ),
        allow_delegation=False,
    )

    # Summarization Task
    email_summarization_task = Task(
        description=(
            f'Go through the email provided to you by the sender {email_sender} with the link {email_link}. Check the email content: {email_content}.'
            'Analyze its contents and generate a concise summary of the email of maximum 30 words.'
        ),
        expected_output='A single concise paragraph of maximum 30 words summarizing the email\'s contents.',
        agent=email_summarizer,
        async_execution=False,
    )

    # Categorization Task
    email_categorization_task = Task(
        description=(
            f'Go through the email provided to you by the sender {email_sender} with the link {email_link}. Check the email content: {email_content}.'
            'Categorize the email as high, low or medium priority with a brief (10 words) justification.'
            'Only categorize as high priority if it requires immediate attention and has some important deadlines, otherwise go for medium or low priority.' 
            'Especially if it\'s some sort of blog or subscription message, classify it as low priority.'
        ),
        expected_output='A single sentence of the format: "[High/Medium/Low] Priority: [justification]." The justification should be no longer than 10 words.',
        agent=email_categorizer,
        async_execution=False,
    )

    # Consolidation Task
    email_consolidation_task = Task(
        description=(
            f'Consolidate the results obtained from the summarization and categorization tasks into a single coherent report for the email from {email_sender} with the link {email_link}.'
        ),
        expected_output="""A structured and organized report that combines the results obtained by each agent. Follow this json format: 
        "Email Sender": "email_sender", "Email Link": "email_link", "Email Summary": "["summary of maximum 30 words", "Email Priority": "priority with justification" """,
        agent=email_consolidator,
        context=[email_summarization_task, email_categorization_task],
        async_execution=False,
    )

    # Form the crew and execute the tasks
    crew = Crew(
        agents=[email_summarizer, email_categorizer, email_consolidator],
        tasks=[email_summarization_task, email_categorization_task, email_consolidation_task],
        process=Process.sequential
    )

    # Run the crew with input data
    crew_output = crew.kickoff(inputs={'email_sender': email_sender, 'email_link': email_link, 'email_content': email_content})

    # Access the output as a JSON dictionary
    if crew_output.json_dict:
        return crew_output.json_dict
    else:
        # Fallback to parsing raw output if JSON dict is unavailable
        try:
            return json.loads(crew_output.raw)
        except json.JSONDecodeError:
            return {"raw_output": crew_output.raw}

def process_all_emails(email_dict: dict) -> list:
    """
    Function to process all emails in the dictionary using the CrewAI agents to generate concise reports.
    
    Parameters:
    - email_dict (dict): Dictionary where keys are email senders and values contain email content and link.
    
    Returns:
    - list: A list of dictionaries where each dict contains the structured report for an email.
    """
    results = []
    
    for email_sender, email_data in email_dict.items():
        email_link = email_data["link"]
        email_content = email_data["content"]
        
        # Call the CrewAI email processing function for each email
        report = process_email_with_crew(email_sender, email_link, email_content)
        
        # Append the report to the results array
        results.append(report)
    
    return results


def main_gmail(max_results):   
    # Authenticate and get the Gmail API service
    gmail_service = authenticate_gmail_api()

    # Calling fetch_emails_as_dict and storing the result in 'email_data'
    email_data = fetch_emails_as_dict(gmail_service, max_results)
    
    # Process all the emails and get the reports
    email_reports = process_all_emails(email_data)

    # Return the structured reports for each email
    return email_reports


# main_gmail(2)