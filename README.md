# **ADDIE: AI-Powered Productivity App for ADHD Individuals**

ADDIE is an innovative productivity app designed to help individuals with ADHD stay organized and improve focus using AI-powered tools. It integrates with Google Calendar, Google Drive, and Google Meet to manage schedules, tasks, documents, and meetings effortlessly.

## **Features**

### 1. **Google Calendar Integration**
Easily manage and create events using natural language input or file uploads.

- Input thoughts or upload files, and ADDIE will automatically create calendar events.
- Retrieve upcoming meetings and events with simple commands.

---

### 2. **Google Meet Transcript Analyzer**
Upload Google Meet transcripts and receive AI-generated summaries of the meeting.

- Extract key points, action items, and deadlines.
- Save time by reviewing concise summaries instead of watching the entire meeting.

---

### 3. **Document Management with Google Drive**
Connect to Google Drive to fetch, categorize, and summarize your documents.

- Prioritize documents into high, medium, and low categories.
- Summarize key information to reduce information overload.

---

### 3. **Email Management with Gmail API**
Connect to Gmail to fetch, categorize, and prioritize your emails.

- Prioritize emails into high, medium, and low categories.
- Summarize key information to reduce information overload.

---

## **Tech Stack**
- **Llama 3.1 70B** for advanced NLP capabilities.
- **Streamlit** for building the user-friendly interface.
- **Google API** for Calendar, Gmail and Drive integrations.
- **Composio** for Google Meet transcript processing.

## **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/Four-Score/addie-local.git
   ```
2. Navigate to the project directory:
   ```bash
   cd addie-local
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Get Groq API Key:
   Get your Groq API Key from https://console.groq.com/keys? and add it as an environment variable GROQ_API_KEY in a .env file in the project's root folder
   ```bash
   GROQ_API_KEY=<your-groq-api-key>
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## **How to Use**

1. **Authenticate with Google**: Log in to your Google account to integrate Calendar and Drive. Your account should be added as a test user - email aera.tech.ai@gmail.com to be added as a test user so you can use the app's features.
2. **Upload Files**: Upload meeting transcripts, documents, or input text to generate events or summaries.
3. **Analyze and Organize**: Let ADDIE automatically generate insights and organize your tasks, emails, meetings, and documents.
