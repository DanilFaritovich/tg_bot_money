import config

import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

"""Create and send an email message
Print the returned  message id
Returns: Message object, including message id

Load pre-authorized user credentials from the environment.
TODO(developer) - See https://developers.google.com/identity
for guides on implementing OAuth2 for the application.
"""

def send_message(user_mail, code):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content(f'Код подтверждения: {code}\n'
                            f'Если вы ничего не отправляли, напишите в telegram: '
                            f'https://t.me/Daniel_De_Casto')

        message['To'] = user_mail
        message['From'] = config.bot_mail
        message['Subject'] = 'Automated draft'

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
        return True
    except HttpError as error:
        print(F'An error occurred: {error}')
        return False