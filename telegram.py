from __future__ import print_function
import datetime

from googleapiclient.http import MediaFileUpload
from oauth2client import file
from telethon.sync import TelegramClient,events
import configparser

from telethon.tl.functions.contacts import GetContactsRequest
from telethon.tl.types import InputPeerUser

config = configparser.ConfigParser()
config.read("copy.ini")

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
SCOPES = ['https://www.googleapis.com/auth/drive']
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

with TelegramClient(username,api_id,api_hash) as client:
    messages=client.get_messages('https://t.me/UPSC_Prelims_Mains_PDF_Materials',limit=1000)
    try:
        year=int(input("Enter year for which you want do download the current affair file : "))
        print("1 for Jan,2 for Feb and so on if you type wrong then error show")
        month=int(input("Enter month for which you want do download the current affair file : "))
    except:
        print("Wrong Input")
    if 1<=month<=12:
        x = datetime.datetime(year, month,1)
        y=x.strftime("%B")
        i=0
        data={}
        name={}
        for msg in messages:
            try:
                pdf_name=msg.media.document.attributes[0].file_name

                if "current" in pdf_name.lower() or "affairs" in pdf_name.lower() or "affairs" in pdf_name.lower():
                    d=msg.date.date()
                    k=str(d)
                    date=k.split("-")
                    if str(month) in str(date[1]) and str(year)==str(date[0]):
                        print(pdf_name)
                        i=i+1
                        data[i]=msg
                        name[i]=pdf_name
            except:
                continue
        if data:
            print("Total Number of files to be download : %s"%(len(data)))
            print("Your downloading started.........")
            k=0
            for x in data:
                k=k+1
                na=name[x]
                print("%s file download start...."%(k))
                client.download_media(data[x],"{}/{}/".format(year,y))
                cred=None
                if os.path.exists('token.pickle'):
                    with open('token.pickle', 'rb') as token:
                        creds = pickle.load(token)
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)

                service = build('drive', 'v3', credentials=creds)

                # Call the Drive v3 API
                file_metadata = {
                'name': "%s/%s/%s"%(year,y,na),

                'mimeType': 'application/vnd.google-apps.folder'
            }
 
                file = service.files().create(body=file_metadata,
                                    fields='id').execute()
                folder_id=file.get('id')
                print("your folder id is %s"%(folder_id))
                print("your %s filename:%s start uploading to google drive"%(x,na))
                filen="%s/%s/%s"%(year,y,na)
                print(filen)
                file_metadata = {
            'name': na,
            'parents': [folder_id]  
                    }

                try:
                    media = MediaFileUpload(filen,
                        mimetype='application/pdf',
                        resumable=True)
                    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
                    file_id=file.get('id')
                    print ('File ID Upload on google drive: %s'%(file.get('id')))
                    print("")
                    file = service.files().get(fileId=file_id,
                                 fields='parents').execute()
                    previous_parents = ",".join(file.get('parents'))
                    file = service.files().update(fileId=file_id,
                                    addParents=folder_id,
                                    removeParents=previous_parents,
                                    fields='id, parents').execute()

                 

                except:
                    print("Due to some error the file not uploaded")
                    continue    

        else:
            print("No file at that time")

    else:
        print("wrong input")
