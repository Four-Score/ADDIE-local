import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from crewai_tools import tool
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from dateutil import tz
from pydantic import BaseModel, Field, ValidationError
import os.path


# Define the Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """Authenticates and returns the Google Calendar API service instance."""
    creds = None
    # The token3.json file stores the user's access and refresh tokens
    if os.path.exists('token3.json'):
        creds = Credentials.from_authorized_user_file('token3.json', SCOPES)
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
        with open('token3.json', 'w') as token:
            token.write(creds.to_json())
    # Build the Google Calendar API service
    service = build('calendar', 'v3', credentials=creds)
    return service




SCOPES = ['https://www.googleapis.com/auth/calendar']

def load_google_calendar_service():
    """Loads the Google Calendar service from saved credentials."""
    creds = None
    if os.path.exists('token3.json'):
        creds = Credentials.from_authorized_user_file('token3.json', SCOPES)
    if creds and creds.valid:
        service = build('calendar', 'v3', credentials=creds)
        return service
    else:
        raise Exception("User is not authenticated. Please authenticate first.")

class GetEventsSchema(BaseModel):
    start_datetime: str = Field(
        description=(
            "The start datetime for the event in the following format: "
            'YYYY-MM-DDTHH:MM:SS. Do not include timezone info as it will be automatically processed.'
        )
    )
    end_datetime: str = Field(
        description=(
            "The end datetime for the event in the following format: "
            'YYYY-MM-DDTHH:MM:SS. Do not include timezone info as it will be automatically processed.'
        )
    )
    max_results: int = Field(
        default=10,
        description="The maximum number of events to return.",
    )
    timezone: str = Field(
        default="America/Chicago",
        description="The timezone in TZ Database Name format, e.g., 'America/New_York'."
    )

class ListGoogleCalendarEvents:
    """Tool to list Google Calendar events."""
    def _parse_event(self, event, timezone):
        """Helper function to parse event details."""
        start = event['start'].get('dateTime', event['start'].get('date'))
        start = datetime.fromisoformat(start).astimezone(tz.gettz(timezone)).strftime('%Y-%m-%dT%H:%M:%SZ')
        end = event['end'].get('dateTime', event['end'].get('date'))
        end = datetime.fromisoformat(end).astimezone(tz.gettz(timezone)).strftime('%Y-%m-%dT%H:%M:%SZ')
        return {
            'start': start,
            'end': end,
            'summary': event.get('summary', 'No Title'),
            'description': event.get('description', 'No Description')
        }

    def run(self, start_datetime: str, end_datetime: str, max_results: int, timezone: str) -> str:
        """Fetches events from the user's Google Calendar."""
        service = load_google_calendar_service()

        # Convert start and end times to ISO 8601 with the proper timezone
        start = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')
        start = start.replace(tzinfo=tz.gettz(timezone)).isoformat()

        end = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S')
        end = end.replace(tzinfo=tz.gettz(timezone)).isoformat()

        # Execute the API request
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start,
            timeMax=end,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No events found."

        parsed_events = [self._parse_event(event, timezone) for event in events]
        return parsed_events


@tool("List Google Calendar Events")
def list_google_calendar_events_tool(start_datetime: str, end_datetime: str, max_results: str, timezone: str) -> str:
    """
    Fetches a list of events from the user's Google Calendar between specified start and end datetimes.

    Parameters:
    - start_datetime (str): The start date and time for the search, formatted as 'YYYY-MM-DDTHH:MM:SS'.
      - Example: '2024-09-01T10:30:00' (for September 1, 2024, at 10:30 AM).
    - end_datetime (str): The end date and time for the search, formatted as 'YYYY-MM-DDTHH:MM:SS'.
      - Example: '2024-09-10T12:00:00' (for September 10, 2024, at 12:00 PM).
    - max_results (str): Maximum number of events to return as a string. Must be a positive integer. 
      - Example: '10'.
    - timezone (str): The timezone in TZ Database Name format, e.g., 'America/New_York'. 
      This ensures the dates and times are returned in the correct timezone format.
      - Example: 'America/Chicago'.
    
    Expected Output:
    - A formatted string listing the events found, including:
      - Event start and end time in the specified timezone.
      - Event summary (title), description, and location (if available).
    - If no events are found, the tool returns 'No events found.'.
    
    Usage Example:
    ```
    list_google_calendar_events_tool(
        start_datetime='2024-09-01T10:30:00',
        end_datetime='2024-09-10T12:00:00',
        max_results='10',
        timezone='America/New_York'
    )
    ```
    """
    try:
        # Validate input schema
        validated_data = GetEventsSchema(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            max_results=int(max_results),
            timezone=timezone
        )
        list_events_tool = ListGoogleCalendarEvents()
        return list_events_tool.run(validated_data.start_datetime, validated_data.end_datetime, validated_data.max_results, validated_data.timezone)
    except ValidationError as e:
        return f"Input validation error: {e}"
    
from crewai_tools import tool
from pydantic import BaseModel, Field, ValidationError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
from dateutil import tz
import os.path

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CreateEventSchema(BaseModel):
    start_datetime: str = Field(
        description=(
            "The start datetime for the event in the following format: "
            'YYYY-MM-DDTHH:MM:SS. Do not include timezone info as it will be automatically processed.'
        )
    )
    end_datetime: str = Field(
        description=(
            "The end datetime for the event in the following format: "
            'YYYY-MM-DDTHH:MM:SS. Do not include timezone info as it will be automatically processed.'
        )
    )
    summary: str = Field(
        description="The title of the event."
    )
    location: str = Field(
        default="",
        description="The location of the event. Optional."
    )
    description: str = Field(
        default="",
        description="The description of the event. Optional."
    )
    timezone: str = Field(
        default="America/Chicago",
        description="The timezone in TZ Database Name format, e.g., 'America/New_York'."
    )

class CreateGoogleCalendarEvent:
    """Tool to create Google Calendar events."""
    def run(self, start_datetime: str, end_datetime: str, summary: str, location: str, description: str, timezone: str) -> str:
        """Creates a new event in the user's Google Calendar."""
        service = load_google_calendar_service()

        start = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')
        start = start.replace(tzinfo=tz.gettz(timezone)).isoformat()
        end = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S')
        end = end.replace(tzinfo=tz.gettz(timezone)).isoformat()

        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start
            },
            'end': {
                'dateTime': end
            },
            'location': location if location else None,
            'description': description if description else None
        }

        event = service.events().insert(calendarId='primary', body=event_body).execute()

        return f"Event created successfully: {event.get('htmlLink', 'Failed to create event')}"

@tool("Create Google Calendar Event")
def create_google_calendar_event_tool(start_datetime: str, end_datetime: str, summary: str, location: str, description: str, timezone: str) -> str:
    """
    Creates a new event in the user's Google Calendar.

    Parameters:
    - start_datetime (str): The start date and time for the event, formatted as 'YYYY-MM-DDTHH:MM:SS'.
      - Example: '2024-09-01T10:30:00' (for September 1, 2024, at 10:30 AM).
    - end_datetime (str): The end date and time for the event, formatted as 'YYYY-MM-DDTHH:MM:SS'.
      - Example: '2024-09-01T11:30:00' (for September 1, 2024, at 11:30 AM).
    - summary (str): The title of the event, a brief description of what the event is about.
      - Example: 'Team Meeting'.
    - location (str): The location of the event (optional). Can be an address or meeting link.
      - Example: '123 Main Street' or 'https://meet.google.com/xyz'.
      If not provided, pass an empty string: ''.
    - description (str): A more detailed description of the event (optional). Can contain agenda or other notes.
      - Example: 'Discuss Q3 project updates and goals'.
      If not provided, pass an empty string: ''.
    - timezone (str): The timezone in TZ Database Name format, e.g., 'America/New_York'.
      This ensures the start and end times are interpreted in the correct timezone.
      - Example: 'America/Chicago'.
    
    Expected Output:
    - A confirmation message that the event has been successfully created, including the event's link.
    - If there is an error, an error message is returned.

    Usage Example:
    ```
    create_google_calendar_event_tool(
        start_datetime='2024-09-01T10:30:00',
        end_datetime='2024-09-01T11:30:00',
        summary='Project Kickoff Meeting',
        location='123 Main Street',
        description='Discuss Q3 project updates and goals',
        timezone='America/New_York'
    )
    ```
    """
    try:
        # Validate input schema
        validated_data = CreateEventSchema(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            summary=summary,
            location=location,
            description=description,
            timezone=timezone
        )
        create_event_tool = CreateGoogleCalendarEvent()
        return create_event_tool.run(
            validated_data.start_datetime,
            validated_data.end_datetime,
            validated_data.summary,
            validated_data.location,
            validated_data.description,
            validated_data.timezone
        )
    except ValidationError as e:
        return f"Input validation error: {e}"

from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = 'llama3-groq-70b-8192-tool-use-preview'
os.environ['OPENAI_API_BASE'] = 'https://api.groq.com/openai/v1'

# Identifier Agent
calendar_agent = Agent(
  role='Google Calendar Manager', 
  goal='Get list of Google Calendar Events or add a new event based on user\'s input: {query}'
  'If the user has uploaded text indicating meetings should be scheduled, then use the create_google_calendar_event_tool to schedule the meetings.'
  'If there are multiple events to be created, then create them ALL.',
  verbose=True,
  memory=True,
  tools=[list_google_calendar_events_tool, create_google_calendar_event_tool],
  backstory=(
    f"""Your job is to manage Google Calendar events. You can list events between two dates or create a new event.
    Use of the two tools provided to you: 'List Google Calendar Events' and 'Create Google Calendar Event'.
    Make sure you pass in the correct parameters to the tools."""
  ),
  allow_delegation=False,
)

# Identification Task
event_task = Task(
  description=(
    """Analyse the user's query: {query}
    Determine whether to list events between specified dates or add anew event based on the query and use the appropriate tool."""
  ),
  expected_output='A message confirming the addition of event(s) and the link of the newly added event(s) OR a list of events in user\'s calendar within specified timeline.',
  agent=calendar_agent,
  async_execution=True,
  tools=[list_google_calendar_events_tool, create_google_calendar_event_tool],
)

# Forming the tech-focused crew with enhanced configurations
crew = Crew(
  agents=[calendar_agent],
  tasks=[event_task],
  process=Process.sequential  # Optional: Sequential task execution is default
)

# Running the crew with input topic
# result = crew.kickoff(inputs={'query': f"""I want to see all the events I have scheduled between 2024-09-01 and 2024-12-09."""})


def run_main(query):
    authenticate_google_calendar()
    result = crew.kickoff(inputs={'query': query})
    return result

# result = run_main("I want to see all the events I have scheduled between 2024-09-01 and 2024-12-09.")
# print(result)