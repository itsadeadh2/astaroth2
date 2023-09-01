from dotenv import load_dotenv
import os
dirname = os.path.dirname(__file__)
ENV_PATH = os.path.join(dirname, '../config/.env')
load_dotenv(dotenv_path=ENV_PATH)
CUSTOM_CREDENTIALS_SUFFIX = os.getenv('CUSTOM_CREDENTIALS_SUFFIX', '')


class PathClient:

    @staticmethod
    def client_secret():
        return os.path.join(dirname, f'../config/client_secrets{CUSTOM_CREDENTIALS_SUFFIX}.json')

    @staticmethod
    def google_token():
        return os.path.join(dirname, f'../config/token{CUSTOM_CREDENTIALS_SUFFIX}.pickle')