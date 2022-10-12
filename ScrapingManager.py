import time

import numpy as np
import pandas as pd

import Downloadpdffromwebsites
from UploadpdfToGoogleDrive import UploadPdftoGdrive


#this project is built to download pdf files from website, using simulation(selenium) 
# and automatically save the in a specific name to the google drive account 
class ScrapingManager:
    
    #reading url from csv file:
    #csv file contains: fileurl,filedownloadname(id) , section and subsection for upload data to google drive
    #  account and file size.
    #saving path: 
    # websitename/filedownloadname/saction/sectionprefex_filesizeMB/sectionprefex_filesizeMB_subsection/filedownloadname
    #it also return the time duration for each pdf downloading process and also returns the total time 
    #for downloading the whole files.
    #function to automatically upload the file to google drive account with a specific path and file name. 
    def save_files_to_gdrive(self,files_path,file_name,gdrive_download_path,gdrive_file_name):
        uploading=UploadPdftoGdrive()
        uploading.upload_Pdf_to_Gdrive(files_path)
        
    def website_scrping(self,urls_csv_file,defualt_download_path,summary_csv_file_name):
        books = pd.read_csv(urls_csv_file,delimiter=',',encoding='utf-8')
        #extract the books names from url:
        print(books.head())
        books['booksname']=books['url'].str.split('/',expand=True)[3]
        print(books['booksname'])
        print(books.head())

        #sizes=[10,25,50,100,200]
        books['file_size_range']=np.zeros(len(books.index))
        books['file_size_range'][books[books['file_size_MB'] <= 10].index]=int(10)
        books['file_size_range'][books[books['file_size_MB'] > 10 ].index]=int(25)
        books['file_size_range'][books[books['file_size_MB'] > 25 ].index]=int(50)
        books['file_size_range'][books[books['file_size_MB'] > 50 ].index]=int(100)
        books['file_size_range'][books[books['file_size_MB'] >100 ].index]=int(200)

        print(books.head())

        #login to the website account.
        connection=Downloadpdffromwebsites.Downloadpdffromwebsite()
        connection.login_to_website()
        print('done')


        step=0
        books['time']=np.zeros(len(books.index))
        books['download_status']=np.zeros(len(books.index))
        books['gdrive_download_path']=np.zeros(len(books.index))
        for i in books.index: 
            copyright_prefix=str(books['copyright'][i]).split('_')
            sup_section=copyright_prefix[0][0]+copyright_prefix[1][0]+'_'+str(books['file_size_range'][i])+'MB'
            gdrive_download_path=f"al_noor_books/{books['copyright'][i]}/{sup_section}/{sup_section}_{books['section'][i]}/"
            print(gdrive_download_path)
            books['gdrive_download_path'][i]=gdrive_download_path
            #set the expected name for downloaded file(id)
            gdrive_file_name=books['id'][i]+'.pdf'
            bookpath=books['url'][i]
            #set the default local download path
            files_path=defualt_download_path

        books.to_csv(summary_csv_file_name)
        
        begin_time=time.time()
        #start the downloading process for pdf files.
        for i in books.index: 
            start_time=time.time()  
            if books['copyright'][i]=='writer_accept' or books['file_size_range'][i]<=100 :
                step+=1
                #set the google drive path for file uploading 
                copyright_prefix=str(books['copyright'][i]).split('_')
                sup_section=copyright_prefix[0][0]+copyright_prefix[1][0]+'_'+str(books['file_size_range'][i])+'MB'
                gdrive_download_path=f"al_noor_books/{books['copyright'][i]}/{sup_section}/{sup_section}_{books['section'][i]}/"
                print(gdrive_download_path)
                books['gdrive_download_path'][i]=gdrive_download_path
                #set the expected name for downloaded file(id)
                gdrive_file_name=books['id'][i]+'.pdf'
                bookpath=books['url'][i]
                #set the default local download path
                file_path=defualt_download_path
                status=connection.all_pdf_download(bookpath,gdrive_download_path,gdrive_file_name,file_path)
                books['download_status'][i]=status[bookpath]
                if status[bookpath]==0:
                    i-=1
                end_time=time.time()
                time.sleep(3)
                print(start_time-end_time)
                books['time'][i]=start_time-end_time
                if step ==15:
                    time.sleep(30)
                    step=0


        
        finish_time=time.time()
        total_time=finish_time-begin_time
        print("files download time",total_time)
        books.to_csv(summary_csv_file_name)
        connection.close_connection()

        begin_time=time.time()
        self.save_files_to_gdrive(files_path) 
        finish_time=time.time()
        total_time=finish_time-begin_time
        print("files upload time",total_time)
        
ScrapingManager.website_scrping('Noor-metadata-01-csv.csv','C:\\Users\\user\\Desktop\\iman\\DataImbalanced\\WebsitePdfFilesScraping\\Download','summary.csv')