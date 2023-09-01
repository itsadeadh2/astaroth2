import os
import pickle

from dotenv import load_dotenv


from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from infrastructure.path_client import PathClient


class Google:
    def __init__(self):

        youtube_scopes = [
            'https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        self.__credentials = Google.__authenticate(pickle_path=PathClient.google_token(), scopes=youtube_scopes)

    @staticmethod
    def __authenticate(pickle_path: str, scopes=[]):
        credentials = None
        if os.path.exists(pickle_path):
            with open(pickle_path, "rb") as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                return credentials

            flow = InstalledAppFlow.from_client_secrets_file(
                PathClient.client_secret(),
                scopes=scopes
            )

            flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
            credentials = flow.credentials

            with open(pickle_path, 'wb') as f:
                pickle.dump(credentials, f)
        return credentials

    def youtube_client(self):
        return build('youtube', 'v3', credentials=self.__credentials)

    def sheets_client(self):
        return build('sheets', 'v4', credentials=self.__credentials)
