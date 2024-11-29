import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account
import gspread

SCOPES = [  'https://www.googleapis.com/auth/gmail.readonly',
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"]

class GoogleHelper:
    def __init__(self):
        pass
    
    def do_google_stuff(self):
        service = self.authenticate_gmail()
        user_id = 'me'
        store_dir = 'attachments'
        if not os.path.exists(store_dir):
            os.makedirs(store_dir)
        # Specify a query if needed, e.g., 'has:attachment filename:pdf'
        query = 'has:attachment'
        
        messages = self.get_messages(service, user_id, query)
        if not messages:
            print('No messages found.')
            return
        threads = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            # Check for attachments
            if 'payload' in msg and 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['filename']:
                        self.save_attachment(service, message['id'], store_dir, user_id)
                        print(f"Attachment found: {part['filename']}")
            else:
                print("No attachments found.")
            threads.append(msg['snippet'])
        return threads
                
    def authenticate_gmail(self):
        """Authenticate the user and return the Gmail service."""
        secret_filepath = "credentials/secret_python.json"
        token_filepath = "credentials/google_python_token.json"
        creds = None
        # The token.json file stores the user's access and refresh tokens.
        if os.path.exists(token_filepath):
            creds = Credentials.from_authorized_user_file(token_filepath, SCOPES)
        # If credentials are invalid, authenticate the user.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    secret_filepath, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save credentials for future use
            with open(token_filepath, 'w') as token:
                token.write(creds.to_json())
        # Build the Gmail service
        service = build('gmail', 'v1', credentials=creds)
        return service
    
    def get_messages(self, service, user_id='me', query=''):
        """Get all messages of the user's mailbox matching the query."""
        try:
            # result = service.users().messages().list(userId=user_id, q=query).execute()
            result = service.users().messages().list(userId=user_id).execute()
            messages = []
            print(result)
            if 'messages' in result:
                messages.extend(result['messages'])
            # Handle pagination if necessary
            while 'nextPageToken' in result:
                page_token = result['nextPageToken']
                result = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
                messages.extend(result['messages'])
            return messages
        except Exception as e:
            print(f'An error occurred: {e}')
            return []
        
    def get_message(self, service, msg_id, user_id='me'):
        """Get a Message with given ID."""
        try:
            message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
            return message
        except Exception as e:
            print(f'An error occurred: {e}')
            return None
        
    def save_attachment(self, service, msg_id, store_dir, user_id='me'):
        """Get and store attachment from Message with given ID."""
        message = self.get_message(service, msg_id, user_id)
        if not message:
            return
        parts = message.get('payload', {}).get('parts', [])
        for part in parts:
            if part.get('filename'):
                if 'attachmentId' in part.get('body', {}):
                    attachment_id = part['body']['attachmentId']
                    attachment = service.users().messages().attachments().get(
                        userId=user_id, messageId=msg_id, id=attachment_id
                    ).execute()
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    path = os.path.join(store_dir, part['filename'])
                    with open(path, 'wb') as f:
                        f.write(file_data)
                    print(f"Attachment {part['filename']} saved.")
                    
    def get_messages_with_service_account():
        # Path to your service account key file
        SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-file.json'
        # Create credentials using the service account file
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )

        # Impersonate the user
        delegated_credentials = credentials.with_subject("ryan.scott@garlandrelocation.com")

        # Build the Gmail service
        service = build('gmail', 'v1', credentials=delegated_credentials)

        # Retrieve the user's emails
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        email_list = []
        if not messages:
            return {"message": "No messages found."}
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                email_list.append(msg)

        return {"emails": email_list}
    
    def authenticate_gsheet(self):
        secret_filepath = "credentials/secret_python.json"
        token_filepath = "credentials/google_python_token.json"
        creds = None
        # The token.json file stores the user's access and refresh tokens.
        if os.path.exists(token_filepath):
            creds = Credentials.from_authorized_user_file(token_filepath, SCOPES)
        # If credentials are invalid, authenticate the user.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    secret_filepath, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save credentials for future use
            with open(token_filepath, 'w') as token:
                token.write(creds.to_json())
            
        client = gspread.authorize(creds)
        
        return client
    
    def open_sheet(self, client):
        # Open the Google Sheet
        sheet = client.open("Test Output Spreadsheet").sheet1
        # Data to be added
        data = ["Name", "Age", "City"]
        # Insert data into the first row
        sheet.insert_row(data, 1)