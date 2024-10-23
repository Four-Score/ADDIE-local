from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
from googleapiclient.errors import HttpError

from crewai_tools import tool
from crewai import Agent, Task, Crew, Process
import asyncio
from io import BytesIO
from googleapiclient.http import MediaIoBaseDownload
import os
from dotenv import load_dotenv
import json
from authenticate import get_drive_service 


# Define the scopes
# SCOPES = ['https://www.googleapis.com/auth/drive']

# def authenticate_drive_api():
#     """Authenticates and returns the Google Drive API service instance."""
#     creds = None
#     # Token file stores user's access and refresh tokens
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If credentials are invalid or don't exist, log the user in
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             # Use InstalledAppFlow.from_client_secrets_file()
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'client_secret-agents.json',
#                 scopes=SCOPES,
#                 redirect_uri='http://localhost:8080/')
#             # Use run_local_server() with the specified port
#             creds = flow.run_local_server(port=8080)
#         # Save the credentials for future runs
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     # Build the Drive API service
#     service = build('drive', 'v3', credentials=creds)
#     return service



@tool("Extract Files From Google Drive Folder")
def extract_files_from_folder_tool(folder_id: str) -> str:
    """
    Extracts all files from a Google Drive folder and returns their names and IDs in a formatted string.
    
    Parameters:
    - folder_id (str): The ID of the folder from which to extract all files. Extract this ID from the folder URL. Example: '1aB2cDe3FgHiJk4LmNOpQr5StUv6WxYz' from 'https://drive.google.com/drive/folders/1aB2cDe3FgHiJk4LmNOpQr5StUv6WxYz'

    Returns:
    - A string formatted like a dict: "{file_url_1: [file_name_1, file_id_1], file_url_2: [file_name_2, file_id_2]}"
      Example: "{'https://drive.google.com/file/d/FILE_ID': ['File Name', 'FILE_ID']}"
    """
    
    # Authenticate Google Drive API service
    drive_service = get_drive_service()

    try:
        # Search for all files in the folder
        query = f"'{folder_id}' in parents"
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=100).execute()
        
        items = results.get('files', [])

        if not items:
            return "No files found."

        # Create a dict-like string containing the file URLs, names, and IDs
        file_dict = {
            f"https://drive.google.com/file/d/{file['id']}": [file['name'], file['id']]
            for file in items
        }

        return str(file_dict)

    except HttpError as error:
        return f"An error occurred: {error}"



# Load environment variables
load_dotenv()

# Set environment variables for the agent
os.environ['OPENAI_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = 'llama-3.1-70b-versatile'
os.environ['OPENAI_API_BASE'] = 'https://api.groq.com/openai/v1'

# Define function to call the agent and get the dictionary output
def extract_filtered_files(folder_link: str, query: str) -> dict:
    # Identifier Agent
    gdrive_agent = Agent(
        role='Google Drive Files Extractor', 
        goal=f"""Extract list of Google Drive Files from this folder {folder_link} and return the names and ids of those files which are related to: {query}. 
                Use the tool provided to you for files extraction and ONLY your own reasoning skills for files filtering (no tool needed). Invoking the tool  just once
                is enough to extract the files. Don't invoke the tool multiple times.""",
        verbose=True,
        memory=True,
        tools=[extract_files_from_folder_tool],
        backstory=(
            """Your task is to extract the list of files from the Google Drive folder with the provided folder ID and return the names and IDs of the files
            which seem related to the topic provided. This will help users filter out relevant files from their Google Drive folders and use them as per 
            their needs."""
        ),
        allow_delegation=False,
    )

    # Identification Task
    gdrive_task = Task(
        description=f"""Extract list of Google Drive Files from this folder {folder_link} and return the names and ids of those files which are related to: {query}""",
        expected_output='A python dict containing all filtered files using this format for the keys and values: "file name": "file id".',
        agent=gdrive_agent,
        async_execution=False,  # Set to synchronous execution
    )

    # Form the crew and execute the task
    crew = Crew(
        agents=[gdrive_agent],
        tasks=[gdrive_task],
        process=Process.sequential  # Sequential task execution is default
    )
    
    # Kick off the crew and retrieve the result
    crew_output = crew.kickoff(inputs={'folder_link': folder_link, 'query': query})
    
    # Try to extract the output from json_dict
    if crew_output.json_dict:
        output_dict = crew_output.json_dict
    else:
        # If json_dict is not available, fallback to parsing raw output
        result_str = crew_output.raw
        try:
            output_dict = json.loads(result_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing the agent's output into a dictionary: {e}")
    
    return output_dict




class ExtractFileContentsTool:
    """
    A tool to extract the textual contents of a file from Google Drive given its file ID.

    Parameters:
    - file_id (str): The ID of the file to extract contents from.

    The tool identifies the file type (Google Docs, plain text, etc.) and retrieves the textual content accordingly.
    """

    def __init__(self, service):
        self.service = service

    def run(self, file_id: str) -> str:
        """
        Executes the tool to extract the contents of the file with the given ID.

        Parameters:
        - file_id (str): The ID of the file in Google Drive.

        Returns:
        - The contents of the file as a string.
        """
        try:
            # Get the file metadata to determine its MIME type
            file = self.service.files().get(fileId=file_id, fields='mimeType, name').execute()
            mime_type = file.get('mimeType')
            file_name = file.get('name')

            print(f'File Name: {file_name}')
            print(f'MIME Type: {mime_type}')

            # Handle different types of files
            if mime_type == 'application/vnd.google-apps.document':
                # Export Google Docs as plain text
                request = self.service.files().export_media(fileId=file_id, mimeType='text/plain')
            elif mime_type.startswith('text/'):
                # Directly download text files
                request = self.service.files().get_media(fileId=file_id)
            else:
                # Handle non-text files
                return f"File '{file_name}' is not a text-based file. Cannot extract contents."

            # Download the file contents
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f'Download progress: {int(status.progress() * 100)}%')

            # Convert the downloaded bytes to a string
            file_contents = fh.getvalue()
            text = file_contents.decode('utf-8')
            return text

        except HttpError as error:
            return f"An error occurred: {error}"

# CrewAI tool wrapper
@tool("Extract Google Drive File Contents")
def extract_drive_file_contents_tool(file_id: str) -> str:
    """
    This tool extracts the contents of a file from Google Drive by its file ID and returns them as a string.
    
    Parameters:
    - file_id (str): The unique ID of the file in Google Drive.
    
    The tool will download or export the file and return its textual content if available. Only works for text files, not other types.
    """
    # Authenticate Google Drive API (service should be pre-authenticated)
    service = get_drive_service()

    # Initialize the file extraction tool
    file_extractor = ExtractFileContentsTool(service)
    
    # Extract the contents of the file
    return file_extractor.run(file_id)


from crewai_tools import tool

# Define the tool for generating Google Drive file links
@tool("Generate Google Drive File Link")
def generate_drive_file_link_tool(file_id: str) -> str:
    """
    Tool to generate a Google Drive file link given the file ID.
    
    Parameters:
    - file_id (str): The Google Drive file ID.
    
    Returns:
    - str: The Google Drive file link in the format 'https://drive.google.com/file/d/<file_id>/view'.
    """
    return f"https://drive.google.com/file/d/{file_id}/view"



# Synchronous function to run the crew and consolidate the report for a single file
def analyze_and_consolidate_drive_file(file_id: str, file_name: str) -> dict:
    """
    Function to run a crew that extracts contents from a Google Drive file,
    generates a summary, categorizes it, and consolidates the result into a coherent report.
    
    Parameters:
    - file_id (str): The Google Drive file ID.
    - file_name (str): The name of the Google Drive file.
    
    Returns:
    - dict: A dictionary containing the consolidated report with the file name, link, summary, and priority.
    """
    
    # Summarizer Agent
    summarizer = Agent(
        role='Document Summarizer',
        goal=f"""Use the tool provided to you to extract the textual contents of the google drive file {file_name} with the file id {file_id}.
                 Then, use your own skills to generate a concise summary of its contents, highlighting only the key information.""",
        verbose=True,
        memory=True,
        tools=[extract_drive_file_contents_tool],
        backstory=(
            f"""You're an expert in document analysis and summarization. With your extensive experience, 
            you have developed a unique ability to generate concise and informative summaries of any given document. 
            Your expertise lies in providing succinct summaries for any information/piece of text that is provided to you."""
        ),
        allow_delegation=False,
    )

    # Categorizer Agent
    categorizer = Agent(
        role='Document Priority Categorizer',
        goal=f"""Use the tool provided to you to extract the textual contents of the google drive file {file_name} with the file id {file_id}. 
                Based on its textual content, use your own reasoning skills to categorize it as high, low, or medium priority with brief justification.""",
        verbose=True,
        memory=True,
        tools=[extract_drive_file_contents_tool],
        backstory=(
            f"""You're an expert in document analysis and priority detection. You can detect whether a document is of high, low, or medium priority
            based on its contents. Your expertise lies in providing a brief justification for the priority category assigned to the document. 
            This will help users in better organizing and managing the documents based on their priority levels."""
        ),
        allow_delegation=False,
    )

    # Consolidator Agent
    consolidator = Agent(
        role='Report Consolidator',
        goal=f"""Combine the results obtained by each agent into a single coherent report for the file {file_name} with file id {file_id}.'
                Use the tool provided to you (generate_drive_file_link_tool) to generate the Google Drive file link for the document given its file id.
                Invoking generate_drive_file_link_tool once is enough to generate the link.
                Once you get the link, consolidate all the information together by yourself without using any tool.""",
        verbose=True,
        memory=True,
        tools=[generate_drive_file_link_tool],
        backstory=(
            f"""You're an expert in consolidating information from multiple sources. Your role is to take the results obtained by 
            each agent and combine them into a single coherent report. Your expertise lies in synthesizing information from 
            different agents and presenting it in a structured and organized manner. This will help in providing a 
            comprehensive overview of the document analysis process."""
        ),
        allow_delegation=False,
    )

    # Summarization Task
    summarization_task = Task(
        description=(
            f'Use the tool provided to you to extract the textual contents of the google drive file {file_name} with the file id {file_id}. '
            'Analyze its contents and generate a concise summary of the document.'
        ),
        expected_output='A single concise paragraph of maximum 100 words summarizing the document\'s contents.',
        agent=summarizer,
        async_execution=True,
    )

    # Categorization Task
    categorization_task = Task(
        description=(
            f'Use the tool provided to you to extract the textual contents of the google drive file {file_name} with the file id {file_id}. '
            'Categorize the document as high, low or medium priority with a brief justification.'
            'Only categorize as high priority if it requires immediate attention and has some important deadlines, otherwise go for medium or low priority.'
        ),
        expected_output='A single sentence of the format: "[High/Medium/Low] Priority: [justification]." The justification should be no longer than 20 words.',
        agent=categorizer,
        async_execution=True,
    )

    # Consolidation Task
    consolidation_task = Task(
        description=(
            f'Consolidate the results obtained from the summarization and categorization tasks into a single coherent report for the file {file_name}. '
            'Use the tool provided (generate_drive_file_link_tool) to generate the Google Drive file link for the document given its file id.'
        ),
        expected_output="""A structured and organized report that combines the results obtained by each agent. Follow this json format: 
        "File Name": "file_name", "File Link": "file_link", "Document Summary": "["summary of maximum 50 words", "Document Priority": "priority with justification" """,
        agent=consolidator,
        context=[summarization_task, categorization_task],
        async_execution=False,
    )

    # Forming the crew
    crew = Crew(
        agents=[summarizer, categorizer, consolidator],
        tasks=[summarization_task, categorization_task, consolidation_task],
        process=Process.sequential  # Optional: Sequential task execution is default
    )

    # Running the crew with input topic
    crew_output = crew.kickoff(inputs={'file_id': file_id, 'file_name': file_name})

    # Accessing the output as a JSON dictionary
    if crew_output.json_dict:
        result_dict = crew_output.json_dict
        return result_dict
    else:
        # Parse the raw output as JSON if json_dict is unavailable
        try:
            parsed_output = json.loads(crew_output.raw)
            return parsed_output
        except json.JSONDecodeError:
            # Fallback to raw output if parsing fails
            return {"raw_output": crew_output.raw}

def process_files_sequentially(folder_link: str, query: str) -> list:
    """
    Function to extract files from the Google Drive folder, and then process each file sequentially
    to generate summaries, priorities, and consolidated reports for each file.

    Parameters:
    - folder_link (str): The Google Drive folder link.
    - query (str): The query for filtering files.

    Returns:
    - list: A list of dictionaries containing the consolidated reports for each file.
    """
    
    # Extract the files from the folder using Crew Function 1
    output_dict = extract_filtered_files(folder_link, query)

    # Initialize a list to store results
    results = []
    
    # Loop over each file and process it sequentially
    for file_name, file_id in output_dict.items():
        result = analyze_and_consolidate_drive_file(file_id, file_name)
        results.append(result)

    return results

# # Example usage of the function
# folder_link = "https://drive.google.com/drive/folders/1gNZgMkDgLKWVdfYItao4ms8m3MY-gIfj"
# query = "BYTE"

# if __name__ == '__main__':
#     file_analysis_results = process_files_sequentially(folder_link, query)
#     print(file_analysis_results)