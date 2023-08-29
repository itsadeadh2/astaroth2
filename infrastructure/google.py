import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

dirname = os.path.dirname(__file__)
TOKEN_PATH = os.path.join(dirname, '../config/token.pickle')
SECRETS_PATH = os.path.join(dirname, '../config/client_secrets.json')


class Google:
    def __init__(self):
        self.__set_credentials()

    def __set_credentials(self):
        self.__credentials = None
        if os.path.exists(TOKEN_PATH):
            print('Loading credentials from file...')
            with open(TOKEN_PATH, "rb") as token:
                self.__credentials = pickle.load(token)

        if not self.__credentials or not self.__credentials.valid:
            if self.__credentials and self.__credentials.expired and self.__credentials.refresh_token:
                print('Refreshing access token...')
                self.__credentials.refresh(Request())
            else:
                print('Fetching new tokens')

                flow = InstalledAppFlow.from_client_secrets_file(
                    SECRETS_PATH,
                    scopes=['https://www.googleapis.com/auth/youtube']
                )

                flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
                self.__credentials = flow.credentials

    def youtube_client(self):
        return build('youtube', 'v3', credentials=self.__credentials)
