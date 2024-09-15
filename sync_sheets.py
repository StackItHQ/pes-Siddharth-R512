import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    creds = None
    # Path to your credentials.json file
    creds_path = os.path.join(os.getcwd(), 'credentials.json')
    
    # The file token.json stores the user's access and refresh tokens
    token_path = 'token.json'
    
    # Check if token.json exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    else:
        # If no token, generate it
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
    
    return creds

def main():
    # Get credentials
    creds = get_credentials()

    # Build the service object
    service = build('sheets', 'v4', credentials=creds)
    
    # Example of reading from a Google Sheet (replace with your Sheet ID and range)
    SAMPLE_SPREADSHEET_ID = 'your-spreadsheet-id'
    SAMPLE_RANGE_NAME = 'Sheet1!A1:D5'
    
    result = service.spreadsheets().values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    rows = result.get('values', [])
    
    if not rows:
        print('No data found.')
    else:
        print('Data from the Google Sheet:')
        for row in rows:
            print(row)

if __name__ == '__main__':
    main()
