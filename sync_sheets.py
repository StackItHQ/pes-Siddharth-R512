import os
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from db_connection import create_connection, close_connection
import mysql.connector

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1qPjVehT7mn5W1Qq_B6P0bP_bTtn3iHH9XwpwTrXxdaw'
RANGE_NAME = 'Sheet1!A1:D'

def get_credentials():
    creds = None
    creds_path = r'C:\Users\siddh\Documents\SuperJoin cred\credentials.json'
    token_path = 'token.json'
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_sheet_data(service):
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])

def get_db_data(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sheet_data")
    result = cursor.fetchall()
    cursor.close()
    return result

def update_sheet(service, values):
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()

def update_db(connection, data):
    cursor = connection.cursor()
    for row in data[1:]:  # Skip header
        # Ensure row has all required fields
        if len(row) < 4:
            print(f"Skipping incomplete row: {row}")
            continue
        
        try:
            cursor.execute("""
                INSERT INTO sheet_data (id, name, email, age) 
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name), email = VALUES(email), age = VALUES(age)
            """, (row[0], row[1], row[2], row[3]))
        except mysql.connector.Error as err:
            print(f"Error updating row {row}: {err}")
    
    connection.commit()
    cursor.close()

def delete_from_db(connection, id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM sheet_data WHERE id = %s", (id,))
    connection.commit()
    cursor.close()

def delete_from_sheet(service, row_index):
    request = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": 0,
                        "dimension": "ROWS",
                        "startIndex": row_index,
                        "endIndex": row_index + 1
                    }
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=request).execute()

def sync_data(service, connection):
    sheet_data = get_sheet_data(service)
    db_data = get_db_data(connection)
    
    # Convert DB data to match Sheet data format
    db_rows = [[str(row['id']), row['name'], row['email'], str(row['age'])] for row in db_data]
    
    # Update Sheet with new DB data
    if db_rows != sheet_data[1:]:
        update_sheet(service, [sheet_data[0]] + db_rows)
    
    # Update DB with new Sheet data
    update_db(connection, sheet_data)
    
    # Handle deletions
    sheet_ids = set(row[0] for row in sheet_data[1:])
    db_ids = set(str(row['id']) for row in db_data)
    
    # Delete from DB if not in Sheet
    for id in db_ids - sheet_ids:
        delete_from_db(connection, id)
    
    # Delete from Sheet if not in DB
    for i, row in enumerate(sheet_data[1:], start=1):
        if row[0] not in db_ids:
            delete_from_sheet(service, i)

def main():
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    connection = create_connection()
    
    try:
        while True:
            sync_data(service, connection)
            print("Sync completed. Waiting for next sync...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Sync stopped by user.")
    finally:
        close_connection(connection)

if __name__ == '__main__':
    main()