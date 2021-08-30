from __future__ import print_function

from google import auth
from constants import MEET, ZOOM
from datetime import timedelta, timezone, datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import re
import os

from events import Event



class GoogleCalendar():
    
    # If modifying these scopes, delete the file token.json
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    PATH = '.'
    
    SERVICE = None
    
    ADD_TO_DATABASE_HOURS_PRIOR = 72
    
    def __init__(self, path: str='.', add_to_database_hours_prior: int=72) -> None:
        self.PATH = path
        self.ADD_TO_DATABASE_HOURS_PRIOR = add_to_database_hours_prior
    
        creds = self.authenticate_google_account()
        
        self.SERVICE = build('calendar', 'v3', credentials=creds)
        
        
        
        
    
    def authenticate_google_account(self) -> dict:
    
        """Authenticate user through local cached token.json file ro by prompting Google login through local browser
            Returns dictionary of Google credentials for authenticated user (the format of the dictionary is determined through Google API)
        """

        token_file_path = os.path.join(self.PATH, 'token.json')
        
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_file_path):
            creds = Credentials.from_authorized_user_file(token_file_path, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(self.PATH, 'credentials.json'), self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file_path, 'w') as token:
                token.write(creds.to_json())

        return creds
    
    
    def get_all_calendar_ids(self) -> list:
        """
        Method to get ids of all calendars through a built Google Calendar Resource service
        Google Calendar API will return 100 calendars per page when listing calendars, so for users with more than 100 calendars, this needs to be done through multiple calls
        """
        calendar_ids = []
        
        page_token = None
        while True:
            calendar_list = self.SERVICE.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                calendar_ids.append(calendar_list_entry['id'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        
        return calendar_ids



    def get_events_for_calendar(self, calendar_id: str, min_time: datetime, max_time: datetime) -> list:
        """
        Fetch all the events in between min_time and max_time
        Returns the id, name, description (if a Google Meet link exists, it's appended to description), start_time of events
        """
        
        calendar_events = []
        
        page_token = None
        while True:
            events = self.SERVICE.events().list(calendarId=calendar_id, pageToken=page_token, timeMin=min_time.isoformat(), timeMax=max_time.isoformat()).execute()
            for event in events['items']:
                if 'dateTime' in event['start']: calendar_events.append(event) 
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        
            
        return [
            {
            'id': event['id'],
            'name': event.get('summary', ''), 
            'description': event.get('description', '') + ' ' + event.get('hangoutLink', ''),
            'start_time': datetime.fromisoformat(event['start']['dateTime'])
            } 
            for event in calendar_events]



    def parse_event_description(self, description: str):
        """
        Look at a description from an event, take out links that are Zoom and Google Meet links
        """
        
        url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        
        
        matches = re.findall(url_regex, description)
        
        zoom_link = [match[0] for match in matches if 'zoom.us' in match[0]]

        if zoom_link:
            return zoom_link[0], ZOOM
        
        meet_link = [match[0] for match in matches if 'meet.google.com' in match[0]]
        
        if meet_link:
            return meet_link[0], MEET
        
        return None, None
        



    def get_all_events(self, min_time: datetime=datetime.now(timezone.utc).astimezone(), max_time: datetime=(datetime.now(timezone.utc) + timedelta(hours=72)).astimezone()) -> list: 
        """
        Get all events in all calenders with the provided calendar service instance
        """
        
        calendar_ids = self.get_all_calendar_ids()
        
        events = []
        
        for calendar_id in calendar_ids:
            events += self.get_events_for_calendar(calendar_id, min_time=min_time, max_time=max_time)
        
        
        
        for event in events:
            url, service = self.parse_event_description(event['description'])
            event['url'] = url
            event['service'] = service
        
        events = [event for event in events if event['url']]
        
        return [Event(
            event_id=event['id'],
            name=event['name'], 
            start_time=event['start_time'],
            url=event['url'],
            service=event['service']
            ) for event in events]
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# def authenticate_google_account() -> dict:
    
#     """Authenticate user through local cached token.json file ro by prompting Google login through local browser
#         Returns dictionary of Google credentials for authenticated user (the format of the dictionary is determined through Google API)
#     """
    
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     return creds


# def get_google_service(service_name: str, version: str, creds: dict) -> Resource:
#     """
#     Returns a Resource instance with the provided service, version, and authenticated user credentials
#     """
#     return build(service_name, version, credentials=creds)


# def get_all_calendar_ids(service: Resource) -> list:
#     """
#     Method to get ids of all calendars through a built Google Calendar Resource service
#     Google Calendar API will return 100 calendars per page when listing calendars, so for users with more than 100 calendars, this needs to be done through multiple calls
#     """
#     calendar_ids = []
    
#     page_token = None
#     while True:
#         calendar_list = service.calendarList().list(pageToken=page_token).execute()
#         for calendar_list_entry in calendar_list['items']:
#             calendar_ids.append(calendar_list_entry['id'])
#         page_token = calendar_list.get('nextPageToken')
#         if not page_token:
#             break
    
#     return calendar_ids



# def get_events_for_calendar(service: Resource, calendar_id: str, min_time: datetime, max_time: datetime) -> list:
#     """
#     Fetch all the events in between min_time and max_time
#     Returns the id, name, description (if a Google Meet link exists, it's appended to description), start_time of events
#     """
    
#     calendar_events = []
    
#     page_token = None
#     while True:
#         events = service.events().list(calendarId=calendar_id, pageToken=page_token, timeMin=min_time.isoformat(), timeMax=max_time.isoformat()).execute()
#         for event in events['items']:
#             if 'dateTime' in event['start']: calendar_events.append(event) 
#         page_token = events.get('nextPageToken')
#         if not page_token:
#             break
    
        
#     return [
#         {
#         'id': event['id'],
#         'name': event.get('summary', ''), 
#         'description': event.get('description', '') + ' ' + event.get('hangoutLink', ''),
#         'start_time': datetime.fromisoformat(event['start']['dateTime'])
#         } 
#         for event in calendar_events]



# def parse_event_description(description: str):
#     """
#     Look at a description from an event, take out links that are Zoom and Google Meet links
#     """
    
#     url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    
    
#     matches = re.findall(url_regex, description)
    
#     zoom_link = [match[0] for match in matches if 'zoom.us' in match[0]]

#     if zoom_link:
#         return zoom_link[0], ZOOM
    
#     meet_link = [match[0] for match in matches if 'meet.google.com' in match[0]]
    
#     if meet_link:
#         return meet_link[0], MEET
    
#     return None, None
    



# def get_all_events(service: Resource, min_time: datetime=datetime.now(timezone.utc).astimezone(), max_time: datetime=(datetime.now(timezone.utc) + timedelta(hours=ADD_TO_DATABASE_HOURS_PRIOR)).astimezone()) -> list: 
#     """
#     Get all events in all calenders with the provided calendar service instance
#     """
    
#     calendar_ids = get_all_calendar_ids(service)
    
#     events = []
    
#     for calendar_id in calendar_ids:
#         events += get_events_for_calendar(service, calendar_id, min_time=min_time, max_time=max_time)
    
    
    
#     for event in events:
#         url, service = parse_event_description(event['description'])
#         event['url'] = url
#         event['service'] = service
    
#     events = [event for event in events if event['url']]
    
#     return [Event(
#         event_id=event['id'],
#         name=event['name'], 
#         start_time=event['start_time'],
#         url=event['url'],
#         service=event['service']
#         ) for event in events]
    

    
