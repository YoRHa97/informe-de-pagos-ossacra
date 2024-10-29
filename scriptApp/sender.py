import time
import os.path
import base64
import mimetypes
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pandas import read_sql_query
from scriptApp.utils import log
from scriptApp.db import session, Provider, Transfer, PayOrder
from scriptApp.generator import message, subject, attachments


def gmail_send_message_with_attachment(index, creds, to, subject, message, attachments):
    while True:
        try:
            service = build("gmail", "v1", credentials=creds)
            mime_message = EmailMessage()
            mime_message["To"] = to
            mime_message["From"] = "no-reply@ossacra.org.ar"
            mime_message["Subject"] = subject
            mime_message.add_alternative(message, subtype="html")
            for attachment in attachments:
                type_subtype, _ = mimetypes.guess_type(attachment)
                maintype, subtype = type_subtype.split("/")
                with open(attachment, "rb") as fp:
                    attachment_data = fp.read()
                    mime_message.add_attachment(attachment_data, maintype, subtype, filename=os.path.basename(attachment))
            encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
            create_message = {"raw": encoded_message}
            send_message  = service.users().messages().send(userId="me", body=create_message).execute()
            print(f'Message Id: {index}_{send_message["id"]}')
            break
        except HttpError as error:
            print(f"An error occurred: {error}")
            send_message = None
            if error.resp['status'] == '429':
                log('Entrando en espera de 7200 segundos...')
                time.sleep(7200)
            else:
                break


def send_data(datadir):
    log(f"\nIniciando envio de informes...\n")
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    providers = session.query(Provider).all()
    time.sleep(1)
    counter = 0
    global_counter = 0
    for provider in providers:
        sql_query = session.query(PayOrder, Transfer).join(PayOrder, Transfer.pay_order).filter(PayOrder.provider_code == provider.code)
        transfers_dates_df = read_sql_query(sql_query.statement, session.bind).drop_duplicates(subset='date').filter(items=['date']).reset_index(drop=True)
        for index, row in transfers_dates_df.iterrows():
            date = row['date']
            to = []
            if provider.email != "0":
                to = provider.email.split(';')
            if provider.cc:
                to = to + provider.cc.split(';')
            log(f"Enviando: {provider.code} - {provider.name} - {to}")
            gmail_send_message_with_attachment(
                index=global_counter,
                creds=creds,
                to=to,
                subject=subject(date, provider.cuit, provider.name),
                message=message(date),
                attachments=attachments(datadir, date, provider))
            counter += 1
            global_counter += 1
            if counter == 500:
                log('500 mails enviados, entrando en espera de 3600 segundos...')
                time.sleep(3600)
                counter = 0
            time.sleep(1)
    time.sleep(1)
    log(f"\nEnvio finalizado")
    time.sleep(1)
