import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from db_connection import create_connection, close_connection

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_credentials():
    creds = None
    # Path to your credentials.json file
    creds_path = r'C:\Users\siddh\Documents\SuperJoin cred\credentials.json'
    
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

def insert_data_to_db(data):
    # Create a connection to the database
    connection = create_connection()
    cursor = connection.cursor()

    # Insert each row into the MySQL database
    for row in data[1:]:  # Skip the header row
        sql = "INSERT INTO sheet_data (id, name, email, age) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (row[0], row[1], row[2], row[3]))

    # Commit changes and close connection
    connection.commit()
    cursor.close()
    close_connection(connection)
    print(f"{len(data) - 1} records inserted into the database.")

def main():
    # Get credentials
    creds = get_credentials()

    # Build the service object
    service = build('sheets', 'v4', credentials=creds)
    
    # Replace with your Google Sheet ID and range
    SPREADSHEET_ID = '1qPjVehT7mn5W1Qq_B6P0bP_bTtn3iHH9XwpwTrXxdaw'
    RANGE_NAME = 'Sheet1!A1:D16'
    
    # Fetch data from the Google Sheet
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])
    
    if not rows:
        print('No data found in the Google Sheet.')
    else:
        print('Data fetched from the Google Sheet. Inserting into database...')
        insert_data_to_db(rows)

if __name__ == '__main__':
    main()