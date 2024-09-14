from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsListener:
    def __init__(self, sheet_id):
        self.sheet_id = sheet_id
        self.service = self._get_sheets_service()
        self.last_known_state = self._get_current_state()

    def _get_sheets_service(self):
        creds = None
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        return build('sheets', 'v4', credentials=creds)

    def _get_current_state(self):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheet_id, range='A1:Z1000').execute()
        return result.get('values', [])

    def get_changes(self):
        current_state = self._get_current_state()
        changes = []
        for i, row in enumerate(current_state):
            if i >= len(self.last_known_state) or row != self.last_known_state[i]:
                changes.append(('update', i, row))
        for i in range(len(current_state), len(self.last_known_state)):
            changes.append(('delete', i, None))
        self.last_known_state = current_state
        return changes