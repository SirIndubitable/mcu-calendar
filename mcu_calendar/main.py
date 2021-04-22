import datetime
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import yaml

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def get_google_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_cal_id():
    with open('cal_id.txt', 'r') as reader:
        return reader.read().strip()


def get_google_events(num_events):
    global service
    global calId
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId=calId,
        timeMin=now,
        maxResults=num_events,
        singleEvents=True,
        orderBy='startTime').execute()
    return events_result.get('items', [])


def get_movies():
    movies = []
    for filename in os.listdir('data'):
        with open(os.path.join('data', filename), 'r') as movie_yaml:
            movies.append(yaml.load(movie_yaml.read(), Loader=yaml.Loader))
    return movies


calId = get_cal_id()
creds = get_google_creds()
service = build('calendar', 'v3', credentials=creds)
def main():
    movies = get_movies()

    for movie in movies:
        print(movie['title'], movie['release_date'].isoformat())
        movie_event = {
            "start": { "date": movie['release_date'].isoformat() },
            "end": { "date": movie['release_date'].isoformat() },
            "summary": movie['title'],
            "description": movie['description']
        }
        service.events().insert(
            calendarId=calId,
            body=movie_event).execute()

if __name__ == '__main__':
    main()