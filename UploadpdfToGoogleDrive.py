#upload pdf files to GoogleDrive account:
from __future__ import print_function

import glob
import os
import random
from turtle import title

import google.auth
import pandas as pd
from google.oauth2.service_account import \
    Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import client, file, tools
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

DEFAULT_SCOPES = [
                             "https://www.googleapis.com/auth/documents",
                             "https://www.googleapis.com/auth/drive",
                             "https://www.googleapis.com/auth/drive.file",
                             "https://www.googleapis.com/auth/drive.appfolder",
                             "https://www.googleapis.com/auth/drive.resource",	
                             'https://www.googleapis.com/auth/drive.metadata']


class UploadPdftoGdrive:
    def __init__(self):
        # define path variables
        credentials_file_path = './credentials/credentials.json'
        clientsecret_file_path = './credentials/client_secret.json'
        self.gauth = GoogleAuth()
        self.credentials,self.project_id = google.auth.default()
        self.gauth.LoadClientConfigFile(clientsecret_file_path)
        self.drive = GoogleDrive(self.gauth)
        # define store
        store = file.Storage(credentials_file_path)
        credentials = store.get()
        # get access token
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(clientsecret_file_path, DEFAULT_SCOPES)
            self.credentials = tools.run_flow(flow, store)
        self.drive_service = build('drive', 'v3', credentials=credentials)
        # define API service
        http = credentials.authorize(Http())
        self.http_drive = build('drive', 'v3', http=http)
        self.gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(self.gauth)

    def find_all_gdrive_folders(self):
        
        folder_list = self.drive.ListFile({'q': "trashed=false"}).GetList()
        for folder in folder_list:
            print('folder title: %s, id: %s' % (folder['title'], folder['id']))
        return folder_list

    def upload_file_to_specific_folder(self,file_name,gd_folder_path):
        try:
            folder_path="C:\\Users\\user\\Desktop\\iman\\DataImbalanced\\WebsitePdfFilesScraping\\Download"#set your own download path
            file_metadata = {'name': file_name,'parents': [{'id': gd_folder_path, "kind": "drive#childList"}]}
            folder = self.drive.CreateFile(file_metadata)
            folder.SetContentFile(file_name) #The contents of the file
            #folder.SetContentFile(os.path.join(folder_path, file_name))
            folder.Upload()
            folder.clear()
        except:
            folder=None
           
        return folder
    def create_folder(self,folder_name,parents,mimeType="application/vnd.google-apps.folder"):
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': mimeType,
                'parents': [parents]
            }                                                               
            
            
            #drive_service = build('drive', 'v3', credentials=self.credentials)
            folder_id = self.http_drive.files().create(body=file_metadata, fields='id').execute().get('id')
            #folder_id = drive_service.files().create(body=file_metadata, fields='id').execute().get('id')
            #folder_id = self.drive.CreateFile(file_metadata).get('id')
            print(F'Folder has created with ID: "{folder_id}".')

        except HttpError as error:
            print(F'An error occurred: {error}')
            folder_id = None

        return folder_id


    def search_file(self,file_name,mime_type='application/vnd.google-apps.folder'):
            query="trashed = false and mimeType = 'application/vnd.google-apps.folder'"

            #query = {'q': f"name='{file_name}' and mimeType='application/vnd.google-apps.folder'"}  # Added
            folder_list = self.drive.ListFile({'q':f'name="{file_name}"' and  f'mimeType="{mime_type}"' }).GetList()
            #page_token = None
            #self.drive.files().list(
            #                        pageSize=1000,
            #                        fields="nextPageToken, files(id, name, mimeType, parents)",
            #                        includeItemsFromAllDrives=True, supportsAllDrives=True,
            #                        pageToken=page_token,
            #                        q=query).execute()
            id=dict()
            #folder_list = self.drive.ListFile(query).GetList()
            for file in folder_list:
                # Process change
                
                if file["title"]==file_name:
                    print(F'Found file: {file["title"]}, {file["id"]}')
                    id[file_name]=file["id"]
                    break
                else:
                    #print('file not found',{file["id"]})
                    id[file_name]=0
        
            
            return id[file_name]


    def upload_Pdf_to_Gdrive(self,files_path="C:\\Users\\user\\Desktop\\iman\\DataImbalanced\\WebsitePdfFilesScraping\\Download"):
        books=pd.read_csv('summary.csv',encoding='utf-8')#set your own csv file that contains the files details
        #such as : name,section,subsection,size,
        
        os.chdir(files_path)
        for file_name in glob.glob("*.pdf"):
            folders_id=[]
            print(file_name)
            gdrive_download_path=books['gdrive_download_path'][books[books['id']==file_name.split('.')[0]].index].values
            print(gdrive_download_path)
            sections=gdrive_download_path[0].split('/')
            sections.pop()
            print(sections)
            root_parent_id=self.search_file(sections[0])
            print('root_parent_id=',root_parent_id)
            for section in sections:
                print(section)
                folder_id=self.search_file(section)
                print(folder_id)

                if folder_id:
                    print(section,'exist')
                    folders_id.append(folder_id)
                    root_parent_id=folder_id
                    print("root_parent_id",root_parent_id)
                else:
                    print(section,'not exist')
                    new_folder_id=self.create_folder(section,root_parent_id)
                    #new_folder_id=self.search_file(new_folder_name)
                    print(new_folder_id)
                    folders_id.append(new_folder_id)
                    root_parent_id=new_folder_id
            print('folders_id[3]',folders_id[3])
            uploaded_file_id=self.upload_file_to_specific_folder(file_name,folders_id[3])
            print('uploaded_file_id',uploaded_file_id)
        print("All files have been uploaded")


#gdrive=UploadPdftoGdrive()
#folders=gdrive.find_all_gdrive_folders()
#print(folders)
#gdrive.search_file()
#gdrive.test()
