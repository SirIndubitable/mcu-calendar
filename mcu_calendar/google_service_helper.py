"""
Helper methods for creating google api client services
"""
import os

from google.api_core.client_options import ClientOptions
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def update_creds_token(creds):
    """
    Updates the token.json containing the login token so that when testing
    it is not required to login constantly
    """
    with open("token.json", "w", encoding="UTF-8") as token:
        token.write(creds.to_json())


def get_local_creds(scopes):
    """
    Gets the google Credentials object in this order:
    1. Automatically created token.json
    2. credentials.json file created from https://console.cloud.google.com/
    """
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                update_creds_token(creds)
                return creds
            except RefreshError:
                pass

    # This is the credentials file that is created from making a project with an
    # OAuth 2.0 Client ID from
    if os.path.exists("credentials.json"):
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file="credentials.json", scopes=scopes
        )
        creds = flow.run_console(access_type="offline", include_granted_scopes="true")
        update_creds_token(creds)
        return creds

    raise RuntimeError(
        "Could not load local credentials, add a credentials.json "
        "file from https://console.cloud.google.com/"
    )


class MockService:
    """
    A service that doesn't allow post requests to update the calendar data, but still allows
    get requests so that the code can run properly
    """

    def __init__(self, realService):
        self.real_service = realService

    # Disable unused argument and missing doc string because these are required to match the methods
    # That they are Mocking out
    # pylint: disable=unused-argument,missing-docstring
    def list(self, **kwargs):
        return self.real_service.list(**kwargs)

    def update(self, **kwargs):
        return self

    def insert(self, **kwargs):
        return self

    def execute(self):
        pass


def create_service(scopes):
    """
    Creates a service with the given scopes, and uses either a service token or local credentials
    """
    token_path = os.path.join(os.environ.get("HOME"), "secrets", "service_token.json")
    if os.path.exists(token_path):
        return build(
            serviceName="calendar",
            version="v3",
            client_options=ClientOptions(credentials_file=token_path, scopes=scopes),
        ).events()

    return build(
        serviceName="calendar", version="v3", credentials=get_local_creds(scopes)
    ).events()
