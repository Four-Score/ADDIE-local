import re
import streamlit as st
import os
from dotenv import load_dotenv
from composio_crewai import ComposioToolSet, Action
from crewai import Agent, Task, Crew, Process

# Load environment variables
load_dotenv()

# Set up environment variables for Llama model
os.environ['OPENAI_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = 'llama3-groq-70b-8192-tool-use-preview'
os.environ['OPENAI_API_BASE'] = 'https://api.groq.com/openai/v1'

# Initialize the Composio toolset for Google Meet creation
tool_set = ComposioToolSet()

# Use the correct action for creating a Google Meet
tools = tool_set.get_tools(actions=[Action.GOOGLEMEET_CREATE_MEET])

# Define Agent responsible for creating Google Meet meetings
meet_creator = Agent(
    role="Google Meet Creator",
    goal="Create a new Google Meet video conference without passing any parameters.",
    verbose=True,
    tools=tools,
    backstory="Do NOT pass any parameters to the Google Meet creation request.",
)

# Example of manually passing a payload that aligns with the input schema
manual_payload = {
    "access_type": None,
    "entry_point_access": None
}

# Define the task for Google Meet creation
create_meeting_task = Task(
    description="Create a new Google Meet video conference without passing any parameters.",
    agent=meet_creator,
    expected_output="A URL to the newly created Google Meet.",
    params=manual_payload
)

# Streamlit UI for file upload and transcript analysis
st.title("📋 Meeting Transcript Analyzer & Google Meet Generator")

# Divider for clean layout separation
st.markdown("---")

# Section for Google Meet Generation
st.subheader("🔗 Generate a New Google Meet Link")
st.write("Easily create a Google Meet for your meeting.")

if st.button("Generate Google Meet Link"):
    try:
        # Create a crew with the Google Meet creation task
        meet_crew = Crew(
            agents=[meet_creator],
            tasks=[create_meeting_task],
            process=Process.sequential
        )
        
        # Start the crew's execution when the button is clicked
        with st.spinner('Creating Google Meet...'):
            meet_output = meet_crew.kickoff()

        # Access the meet output
        if meet_output.json_dict:
            result_data = meet_output.json_dict
            if result_data.get('successfull', False):
                meeting_data = result_data.get('data', {}).get('response_data', {})
                meeting_url = meeting_data.get('meetingUri', 'No URL available')

                st.success(f"Google Meet created successfully! [Join Meeting]({meeting_url})")
                st.download_button(
                    label="Download Meeting URL",
                    data=meeting_url,
                    file_name="meeting_url.txt",
                    mime="text/plain"
                )
            else:
                st.error(f"Failed to create Google Meet.")
        else:
            st.write(f"Raw Output: {meet_output.raw}")

    except Exception as e:
        st.error(f"An error occurred during the execution: {str(e)}")

# Add some space before the next section
st.markdown("---")

# File uploader widget for transcript analysis
st.subheader("📂 Upload a Google Meet Transcript for Analysis")
st.write("After uploading, we'll extract key points, action items, and deadlines from your meeting.")

# File uploader for transcript
uploaded_file = st.file_uploader("Choose a Google Meet Transcript", type=["txt"])

# Helper function to extract valid names from the transcript
def extract_valid_names(transcript):
    names = re.findall(r'[A-Z][a-z]+(?: [A-Z][a-z]+)+', transcript)
    return set(names)

if uploaded_file is not None:
    # Save the uploaded file temporarily
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    # Read the file content
    with open(file_path, 'r') as f:
        transcript = f.read()

    # Extract valid names from the transcript
    valid_names = extract_valid_names(transcript)

    # Define a single agent to handle the entire transcript analysis
    transcript_analysis_agent = Agent(
    role="Transcript Analyzer",
    goal=f"""Analyze the following meeting transcript to extract:
    1. **Top Key points**: Only the most important topics and updates discussed in the transcript.
    2. **Top Action items**: Identify specific tasks assigned to individuals using names from the transcript: {', '.join(valid_names)}.
    3. **Top Deadlines**: Extract clear, specific deadlines by identifying phrases like "due", "by next week", specific dates, and time-related words. Ensure that deadlines are tied to specific tasks where possible.
    
    Transcript: {transcript}""",
    verbose=True,
    memory=True,
    backstory="You are an expert at analyzing meeting transcripts and extracting actionable insights. Limit the number of items to avoid overwhelming the user.",
    max_iter=5,
    cache=True,
    max_retry_limit=1,
)

# Define a single task for the agent
    transcript_analysis_task = Task(   
    description=f"""Extract top key points, top action items, and important deadlines from the following meeting transcript:
    Transcript: {transcript}""",
    expected_output="""Please structure the output in the following format:
    
    **Key Points:**
    [List the key points with clear and concise summaries of the most important topics]

    **Action Items:**
    [List specific tasks, making sure to include who is responsible and any details about the task]

    **Deadlines:**
    [For each deadline, ensure that it's tied to a specific task or event, and is as detailed as possible. Avoid vague or unclear timeframes.]
    
    Please ensure the output is cleanly formatted, without raw JSON or unnecessary symbols, and that the number of items in each section is limited to 5.""",
    
    agent=transcript_analysis_agent
)


    # Create the crew with a single agent and task
    crew = Crew(
        agents=[transcript_analysis_agent],
        tasks=[transcript_analysis_task],
        process=Process.sequential,
        full_output=True,
        verbose=True
    )

    # Run the analysis
    try:
        if 'crew_output' not in st.session_state:
            with st.spinner('Processing transcript...'):
                crew_output = crew.kickoff()
                st.session_state['crew_output'] = crew_output  # Store result to avoid re-running

        crew_output = st.session_state['crew_output']

        # Always display the raw output since it's user-friendly
        st.subheader("📝 Meeting Summary")
        st.write(crew_output.raw)

        # Add the download button for the file
        st.download_button(
            label="Download Transcript Analysis",
            data=crew_output.raw,
            file_name="transcript_analysis_output.txt",
            mime="text/plain",
        )

    except Exception as e:
        st.error(f"An error occurred during processing: {str(e)}")

    # Clean up the temporary file
    if os.path.exists(file_path):
        os.remove(file_path)
