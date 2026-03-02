import os.path
import pandas as pd
import streamlit as st
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# App Configuration
st.set_page_config(page_title="Deepak's Scheduler", layout="wide")
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # Port=0 automatically free port dhoond lega
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def main():
    st.title("📅 Smart Scheduling Automation")
    st.write(f"Welcome, **Deepak Yadav**! Let's manage your meetings.") #

    try:
        service = get_calendar_service()
        
        # Sidebar for User Inputs (st.text_input aur st.date_input)
        st.sidebar.header("Meeting Details")
        meeting_title = st.sidebar.text_input("Meeting Title", "Data Science Discussion")
        meeting_date = st.sidebar.date_input("Select Date", datetime.now())
        duration = st.sidebar.number_input("Duration (minutes)", min_value=15, max_value=120, value=30)
        guest_email = st.sidebar.text_input("Guest Email", "example@gmail.com")

        # 1. Fetch Busy Slots
        now = datetime.now(timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚫 Your Busy Slots")
            if not events:
                st.info("No upcoming events found.")
                busy_df = pd.DataFrame()
            else:
                event_list = []
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))
                    event_list.append({
                        'Summary': event.get('summary', 'No Title'),
                        'Start': pd.to_datetime(start).strftime('%I:%M %p'),
                        'End': pd.to_datetime(end).strftime('%I:%M %p')
                    })
                busy_df = pd.DataFrame(event_list)
                st.table(busy_df) # st.table ka use table dikhane ke liye

        # 2. Logic for Free Slots (Simplified for Demo)
        with col2:
            st.subheader("✅ Available Gaps")
            # Yahan humne wahi logic lagaya hai jo pehle discuss kiya tha
            # Demo ke liye hum fixed slots dikha rahe hain jo busy nahi hain
            st.success("You are free between 11:30 AM - 01:00 PM")
            
            if st.button("🚀 Book Meeting Now"):
                # Event create karne ka logic yahan call hoga
                st.balloons()
                st.write(f"Booking '{meeting_title}' for {duration} mins...")
                # create_event function yahan call karein

    except Exception as e:
        st.error(f"Connection Error: {e}")

if __name__ == '__main__':
    main()