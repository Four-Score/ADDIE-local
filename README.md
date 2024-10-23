# **ADDIE: AI-Powered Productivity App for ADHD Individuals**

ADDIE is an innovative productivity app designed to help individuals with ADHD stay organized and improve focus using AI-powered tools. It integrates with Google Calendar, Google Drive, and Google Meet to manage schedules, tasks, documents, and meetings effortlessly.

---

## **Demo Video**

https://github.com/user-attachments/assets/d8779e8b-163c-4a11-a5ce-beb80654967d

---

## **Reviews**

![image](https://github.com/user-attachments/assets/ecaa76ef-af03-457c-aea7-20937ec5a0bc)

---

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
- **Crew AI** for configuring AI Agents.
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

NOTE: When you run the app the very first time, you will have to authenticate with your authorised email account using the link in the **terminal** - this will have to be done only once in the first run.

## **How to Use**

1. **Authenticate with Google**: Log in to your Google account to integrate Calendar and Drive. Your account should be added as a test user - email aera.tech.ai@gmail.com to be added as a test user so you can use the app's features.
2. **Upload Files**: Upload meeting transcripts, documents, or input text to generate events or summaries.
3. **Analyze and Organize**: Let ADDIE automatically generate insights and organize your tasks, emails, meetings, and documents.

---

## **A Detailed Look at ADDIE**

### Google OAuth 2.0 Authentication

ADDIE integrates Google OAuth 2.0 for secure user authentication, allowing users to sign in with their Google accounts and interact with services like Google Calendar and Drive. The app securely manages access and refresh tokens, ensuring persistent sessions. Test users are added for streamlined development. Upon successful authentication, users are notified, and the app seamlessly integrates Google API services.

![Google OAuth UI](![image](https://github.com/user-attachments/assets/4951f5d1-6327-49c0-be1e-366d8dbc4bd1)

---

### Meeting Transcript Analyzer & Google Meet Generator

This feature allows users to generate new Google Meet links using Google API and analyze meeting transcripts using AI tools (Crew AI agents and Composio). Users can quickly create meetings, upload transcripts, and extract key points, action items, and deadlines from discussions. The tool automates meeting summary generation to improve productivity and efficiency.

The Transcript Analysis feature leverages advanced AI through Crew AI agents and Composio to automatically extract actionable insights from meeting transcripts. By simply uploading a transcript, the tool intelligently identifies key points, action items, and deadlines, providing a comprehensive meeting summary within seconds. This significantly reduces the time spent on post-meeting documentation and ensures that critical details never get overlooked. Whether managing complex projects or organizing routine team meetings, this feature brings efficiency to the next level by transforming raw meeting data into structured, actionable insights.

![Meeting Transcript UI](![image](https://github.com/user-attachments/assets/8b1253ee-6544-49b4-a2ad-ca75b11857dd))  
![Meeting Summary Output](![image](https://github.com/user-attachments/assets/79bab224-33d0-4117-b309-8e8425670569))

---

### Google Calendar Management

The **Google Calendar Management** feature allows users to seamlessly manage their Google Calendar events using both manual input and file uploads. Powered by Crew AI agents and the Google Calendar API, users can schedule new events or check existing events by providing text details or uploading documents with event information. The AI automatically extracts the necessary details and schedules the events for you, improving productivity and minimizing the manual effort required.

You can also view all scheduled events for a specific date or month in your Google Calendar, providing an organized and efficient way to manage your time and tasks.

![Calendar Management UI](![image](https://github.com/user-attachments/assets/f85cb282-8fc3-401a-9ab2-dd43f942d1cf))  
![Google Calendar Events](![image](https://github.com/user-attachments/assets/d6c4eeda-c698-4256-adc1-fb18e350aff8))

---

### Email Management

The **Email Management** feature allows users to generate detailed reports of their latest emails, selecting between 5 to 50 emails via a drop-down menu. Powered by Crew AI agents and the Gmail API, the tool efficiently fetches and summarizes the contents of your emails, prioritizing them based on their importance. This helps users quickly identify urgent or high-priority emails, improving productivity and ensuring that no critical emails are missed. Whether you're managing a busy inbox or sorting through recent communications, this feature simplifies the process by highlighting which emails need immediate attention.

![Email Management UI](![image](https://github.com/user-attachments/assets/42e0e971-5c5e-47c7-a757-0553e2026106))  

---

### Google Drive Report Generator

The **Google Drive Report Generator** is a powerful tool that allows users to generate detailed reports from their Google Drive folders. By simply providing a Google Drive folder link, the tool, powered by Crew AI agents and the Google Drive API, extracts relevant files based on user-defined criteria. It then summarizes the documents and prioritizes them as low, medium, or high priority. This feature helps users efficiently sift through large sets of files, filtering and prioritizing those that need immediate attention. It’s ideal for organizing critical documents, ensuring that important files are never missed, and enhancing productivity.

![Google Drive Report Generator UI](![image](https://github.com/user-attachments/assets/59b37cd2-a53b-4b96-ac56-cd4252a12593))  
![Document Summary Output](![image](https://github.com/user-attachments/assets/83cc0996-1398-4616-99cb-d21c8390c1f9))

---

